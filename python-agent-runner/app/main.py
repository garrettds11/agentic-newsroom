from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, status

from app.aws_store import StoryStore, get_story_store
from app.config import Settings, get_settings
from app.editor import EditorAgent
from app.fact_checker import FactChecker
from app.journalist import JournalistAgent
from app.schemas import FinalStoryRecord, ResearchRequest, ResearchResponseMetadata, RunRequest, RunResponse, RunStatus
from app.search_tools import SearchAdapter, get_search_adapter

app = FastAPI(title="Agentic Newsroom Python Agent Runner", version="0.1.0")


def get_search(settings: Settings = Depends(get_settings)) -> SearchAdapter:
    return get_search_adapter(
        settings.search_provider,
        searxng_base_url=settings.searxng_base_url,
        rss_feed_urls=settings.rss_feed_urls,
        rss_source_registry_path=settings.rss_source_registry_path,
        rss_source_ids=settings.rss_source_ids,
        rss_default_max_items=settings.rss_default_max_items,
        rss_default_excerpt_chars=settings.rss_default_excerpt_chars,
        rss_cache_ttl_seconds=settings.rss_cache_ttl_seconds,
    )


def get_store(settings: Settings = Depends(get_settings)) -> StoryStore:
    return get_story_store(settings.storage_provider, dry_run=settings.dry_run)


def require_api_key(
    settings: Settings = Depends(get_settings),
    x_newsroom_api_key: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
) -> None:
    if not settings.require_auth:
        return

    expected = settings.newsroom_api_key
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="NEWSROOM_API_KEY must be configured when REQUIRE_AUTH=true",
        )

    bearer = None
    if authorization and authorization.lower().startswith("bearer "):
        bearer = authorization[7:].strip()

    provided = x_newsroom_api_key or bearer
    if provided != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key")


@app.get("/health")
def health(settings: Settings = Depends(get_settings)) -> dict[str, str | bool]:
    return {
        "status": "ok",
        "environment": settings.environment,
        "dry_run": settings.dry_run,
    }


@app.post("/notifications/placeholder")
def placeholder_notification(payload: dict) -> dict[str, bool | dict]:
    return {
        "accepted": True,
        "dry_run": True,
        "payload": payload,
    }


@app.post("/runs", response_model=RunResponse)
def create_run(
    request: RunRequest,
    _: None = Depends(require_api_key),
    search: SearchAdapter = Depends(get_search),
    store: StoryStore = Depends(get_store),
) -> RunResponse:
    return run_research_flow(request=request, search=search, store=store)


@app.post("/research", response_model=RunResponse)
def create_research(
    request: ResearchRequest,
    _: None = Depends(require_api_key),
    settings: Settings = Depends(get_settings),
    store: StoryStore = Depends(get_store),
) -> RunResponse:
    provider = request.source_provider or settings.search_provider
    source_ids = request.source_ids or settings.rss_source_ids
    requested_max_sources = request.max_sources
    effective_max_sources = requested_max_sources or settings.newsroom_default_max_sources
    capped = effective_max_sources > settings.newsroom_system_max_sources
    if capped:
        effective_max_sources = settings.newsroom_system_max_sources

    search = get_search_adapter(
        provider,
        searxng_base_url=settings.searxng_base_url,
        rss_feed_urls=settings.rss_feed_urls,
        rss_source_registry_path=settings.rss_source_registry_path,
        rss_source_ids=source_ids,
        rss_default_max_items=effective_max_sources,
        rss_default_excerpt_chars=settings.rss_default_excerpt_chars,
        rss_cache_ttl_seconds=settings.rss_cache_ttl_seconds,
    )
    response = run_research_flow(
        request=request.to_run_request(),
        search=search,
        store=store,
        max_sources=effective_max_sources,
    )
    response.metadata = ResearchResponseMetadata(
        requested_max_sources=requested_max_sources,
        effective_max_sources=effective_max_sources,
        system_max_sources=settings.newsroom_system_max_sources,
        capped=capped,
        result_count=len(response.story.sources),
        page_size=request.page_size,
        cursor=request.cursor,
        next_cursor=None,
    )
    return response


def run_research_flow(
    request: RunRequest,
    search: SearchAdapter,
    store: StoryStore,
    max_sources: int | None = None,
) -> RunResponse:
    run_id = f"run_{uuid4().hex}"
    sources = search.search(request.topic)
    if max_sources is not None:
        sources = sources[:max_sources]

    draft = JournalistAgent().draft(run_id=run_id, request=request, sources=sources)
    fact_check = FactChecker().check(draft=draft, sources=sources)
    editor_decision = EditorAgent().review(fact_check=fact_check)

    status = RunStatus.COMPLETED if fact_check.passed else RunStatus.NEEDS_REVISION
    story = FinalStoryRecord(
        run_id=run_id,
        status=status,
        topic=request.topic,
        draft=draft,
        sources=sources,
        fact_check=fact_check,
        editor_decision=editor_decision,
    )
    store.save_story(story)

    return RunResponse(run_id=run_id, status=status, story=story)

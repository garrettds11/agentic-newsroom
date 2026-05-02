from uuid import uuid4

from fastapi import Depends, FastAPI

from app.aws_store import StoryStore, get_story_store
from app.config import Settings, get_settings
from app.editor import EditorAgent
from app.fact_checker import FactChecker
from app.journalist import JournalistAgent
from app.schemas import FinalStoryRecord, RunRequest, RunResponse, RunStatus
from app.search_tools import SearchAdapter, get_search_adapter

app = FastAPI(title="Agentic Newsroom Python Agent Runner", version="0.1.0")


def get_search(settings: Settings = Depends(get_settings)) -> SearchAdapter:
    return get_search_adapter(
        settings.search_provider,
        searxng_base_url=settings.searxng_base_url,
        rss_feed_urls=settings.rss_feed_urls,
    )


def get_store(settings: Settings = Depends(get_settings)) -> StoryStore:
    return get_story_store(settings.storage_provider, dry_run=settings.dry_run)


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
    search: SearchAdapter = Depends(get_search),
    store: StoryStore = Depends(get_store),
) -> RunResponse:
    run_id = f"run_{uuid4().hex}"
    sources = search.search(request.topic)

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

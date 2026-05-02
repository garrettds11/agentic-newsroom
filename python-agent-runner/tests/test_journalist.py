from app.fact_checker import FactChecker
from app.journalist import JournalistAgent
from app.schemas import RunRequest, SourceRecord


def rss_like_source() -> SourceRecord:
    return SourceRecord(
        source_id="src_zdi_1",
        title="ZDI advisory for sample product",
        url="https://example.com/zdi-advisory",
        excerpt="ZDI published an advisory for a sample product issue.",
        provider="rss",
        metadata={
            "published_at": "2026-05-02T12:00:00+00:00",
            "source_name": "Zero Day Initiative Published Advisories 2026",
        },
    )


def test_rss_like_source_title_and_url_appear_in_draft_body() -> None:
    source = rss_like_source()
    draft = JournalistAgent().draft(
        run_id="run_test",
        request=RunRequest(topic="ZDI advisories"),
        sources=[source],
    )

    assert "ZDI advisory for sample product" in draft.body
    assert "https://example.com/zdi-advisory" in draft.body
    assert "Zero Day Initiative Published Advisories 2026" in draft.body
    assert "2026-05-02T12:00:00+00:00" in draft.body
    assert "deterministic source-grounded draft" in draft.body


def test_all_included_source_ids_are_preserved() -> None:
    sources = [
        rss_like_source(),
        SourceRecord(
            source_id="src_zdi_2",
            title="Second advisory",
            url="https://example.com/second-advisory",
            excerpt="Second advisory excerpt.",
            provider="rss",
        ),
    ]

    draft = JournalistAgent().draft(
        run_id="run_test",
        request=RunRequest(topic="ZDI advisories"),
        sources=sources,
    )

    assert draft.source_ids == ["src_zdi_1", "src_zdi_2"]


def test_fact_checker_passes_source_grounded_draft() -> None:
    source = rss_like_source()
    draft = JournalistAgent().draft(
        run_id="run_test",
        request=RunRequest(topic="ZDI advisories"),
        sources=[source],
    )

    report = FactChecker().check(draft=draft, sources=[source])

    assert report.passed is True


def test_placeholder_path_still_produces_source_grounded_draft() -> None:
    source = SourceRecord(
        source_id="src_placeholder",
        title="Placeholder source for local newsroom",
        url="https://example.com/agentic-newsroom-placeholder-source",
        excerpt="Placeholder source text for local dry-run execution.",
        provider="placeholder",
        metadata={"dry_run": True},
    )

    draft = JournalistAgent().draft(
        run_id="run_test",
        request=RunRequest(topic="local newsroom"),
        sources=[source],
    )

    assert "Placeholder source for local newsroom" in draft.body
    assert "https://example.com/agentic-newsroom-placeholder-source" in draft.body
    assert draft.source_ids == ["src_placeholder"]

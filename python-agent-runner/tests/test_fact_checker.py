from app.fact_checker import FactChecker
from app.schemas import DraftRecord, SourceRecord


def make_source(excerpt: str = "The report said 42 people attended on 2026-05-02.") -> SourceRecord:
    return SourceRecord(
        source_id="src_test",
        title="Test source",
        url="https://example.com/source",
        excerpt=excerpt,
    )


def test_fact_checker_passes_sourced_draft() -> None:
    source = make_source()
    draft = DraftRecord(
        run_id="run_test",
        topic="Test",
        title="Test draft",
        body="The report said 42 people attended on 2026-05-02.",
        source_ids=[source.source_id],
    )

    report = FactChecker().check(draft=draft, sources=[source])

    assert report.passed is True
    assert report.issues == []


def test_fact_checker_fails_without_sources() -> None:
    draft = DraftRecord(
        run_id="run_test",
        topic="Test",
        title="Test draft",
        body="A draft without sources.",
        source_ids=[],
    )

    report = FactChecker().check(draft=draft, sources=[])

    assert report.passed is False
    assert any(issue.check == "source_url_presence" for issue in report.issues)


def test_fact_checker_flags_unknown_source_id() -> None:
    source = make_source()
    draft = DraftRecord(
        run_id="run_test",
        topic="Test",
        title="Test draft",
        body="A sourced draft.",
        source_ids=["missing_source"],
    )

    report = FactChecker().check(draft=draft, sources=[source])

    assert report.passed is False
    assert any(issue.check == "draft_source_mapping" for issue in report.issues)


def test_fact_checker_flags_untraced_quote_as_error() -> None:
    source = make_source(excerpt="The report described the meeting.")
    draft = DraftRecord(
        run_id="run_test",
        topic="Test",
        title="Test draft",
        body='A witness said "this exact quote is absent".',
        source_ids=[source.source_id],
    )

    report = FactChecker().check(draft=draft, sources=[source])

    assert report.passed is False
    assert any(issue.check == "quotes" for issue in report.issues)


def test_fact_checker_warns_on_unmatched_numbers_percentages_and_dates() -> None:
    source = make_source(excerpt="The report described the meeting.")
    draft = DraftRecord(
        run_id="run_test",
        topic="Test",
        title="Test draft",
        body="Attendance rose by 25% to 100 people on 2026-05-02.",
        source_ids=[source.source_id],
    )

    report = FactChecker().check(draft=draft, sources=[source])

    assert report.passed is True
    assert {issue.check for issue in report.issues} >= {"numbers", "percentages", "dates"}

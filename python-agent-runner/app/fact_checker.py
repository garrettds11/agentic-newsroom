import re

from app.schemas import DraftRecord, FactCheckIssue, FactCheckReport, SourceRecord

NUMBER_PATTERN = re.compile(r"\b\d+(?:,\d{3})*(?:\.\d+)?\b")
PERCENT_PATTERN = re.compile(r"\b\d+(?:\.\d+)?%(?=\s|$|[.,;:)])")
DATE_PATTERN = re.compile(
    r"\b(?:\d{4}-\d{2}-\d{2}|"
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.? \d{1,2}, \d{4})\b",
    re.IGNORECASE,
)
QUOTE_PATTERN = re.compile(r'"([^"]+)"')


class FactChecker:
    """Deterministic guardrail checks that do not call model providers."""

    def check(self, draft: DraftRecord, sources: list[SourceRecord]) -> FactCheckReport:
        issues: list[FactCheckIssue] = []
        body = draft.body

        issues.extend(self._check_source_url_presence(sources))
        issues.extend(self._check_draft_source_mapping(draft, sources))
        issues.extend(self._check_numbers(body, sources))
        issues.extend(self._check_percentages(body, sources))
        issues.extend(self._check_dates(body, sources))
        issues.extend(self._check_quotes(body, sources))

        blocking = [issue for issue in issues if issue.severity == "error"]
        return FactCheckReport(passed=not blocking, issues=issues)

    def _check_source_url_presence(self, sources: list[SourceRecord]) -> list[FactCheckIssue]:
        if not sources:
            return [
                FactCheckIssue(
                    check="source_url_presence",
                    message="At least one source with a URL is required.",
                    severity="error",
                )
            ]
        return []

    def _check_draft_source_mapping(
        self, draft: DraftRecord, sources: list[SourceRecord]
    ) -> list[FactCheckIssue]:
        known_source_ids = {source.source_id for source in sources}
        missing = [source_id for source_id in draft.source_ids if source_id not in known_source_ids]

        if missing:
            return [
                FactCheckIssue(
                    check="draft_source_mapping",
                    message=f"Draft references unknown source ids: {', '.join(missing)}.",
                    severity="error",
                )
            ]

        if not draft.source_ids:
            return [
                FactCheckIssue(
                    check="draft_source_mapping",
                    message="Draft does not reference any source ids.",
                    severity="error",
                )
            ]

        return []

    def _check_numbers(self, body: str, sources: list[SourceRecord]) -> list[FactCheckIssue]:
        return self._check_pattern_presence("numbers", NUMBER_PATTERN, body, sources)

    def _check_percentages(self, body: str, sources: list[SourceRecord]) -> list[FactCheckIssue]:
        return self._check_pattern_presence("percentages", PERCENT_PATTERN, body, sources)

    def _check_dates(self, body: str, sources: list[SourceRecord]) -> list[FactCheckIssue]:
        return self._check_pattern_presence("dates", DATE_PATTERN, body, sources)

    def _check_quotes(self, body: str, sources: list[SourceRecord]) -> list[FactCheckIssue]:
        issues: list[FactCheckIssue] = []
        source_text = "\n".join(source.excerpt for source in sources).lower()

        for quote in QUOTE_PATTERN.findall(body):
            if quote.lower() not in source_text:
                issues.append(
                    FactCheckIssue(
                        check="quotes",
                        message=f"Quote is not present in source excerpts: {quote}",
                        severity="error",
                    )
                )

        return issues

    def _check_pattern_presence(
        self,
        check_name: str,
        pattern: re.Pattern[str],
        body: str,
        sources: list[SourceRecord],
    ) -> list[FactCheckIssue]:
        matches = pattern.findall(body)
        if not matches:
            return []

        source_text = "\n".join(source.excerpt for source in sources)
        missing = [match for match in matches if match not in source_text]
        if not missing:
            return []

        return [
            FactCheckIssue(
                check=check_name,
                message=f"Draft contains values not found in source excerpts: {', '.join(missing)}.",
                severity="warning",
            )
        ]

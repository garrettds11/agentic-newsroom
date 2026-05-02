from app.schemas import EditorDecision, EditorDecisionStatus, FactCheckReport


class EditorAgent:
    """Minimal deterministic editor decision maker."""

    def review(self, fact_check: FactCheckReport) -> EditorDecision:
        if fact_check.passed:
            return EditorDecision(
                status=EditorDecisionStatus.ACCEPT,
                summary="Draft is acceptable for human review in local dry-run mode.",
            )

        return EditorDecision(
            status=EditorDecisionStatus.REVISE,
            summary="Draft needs revision before human review.",
            required_revisions=[issue.message for issue in fact_check.issues if issue.severity == "error"],
            optional_notes=[issue.message for issue in fact_check.issues if issue.severity != "error"],
        )


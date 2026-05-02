from app.schemas import DraftRecord, RunRequest, SourceRecord


class JournalistAgent:
    """Minimal deterministic draft creator for the initial runner scaffold."""

    def draft(self, run_id: str, request: RunRequest, sources: list[SourceRecord]) -> DraftRecord:
        source_ids = [source.source_id for source in sources]
        body = (
            f"This is a local dry-run draft about {request.topic}. "
            "It uses placeholder source material and should not be treated as publishable reporting. "
            "The draft includes one source URL for provenance review."
        )

        return DraftRecord(
            run_id=run_id,
            topic=request.topic,
            title=f"Draft: {request.topic}",
            body=body,
            source_ids=source_ids,
        )


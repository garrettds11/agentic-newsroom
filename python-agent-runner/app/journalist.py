from app.schemas import DraftRecord, RunRequest, SourceRecord


class JournalistAgent:
    """Deterministic source-grounded draft creator."""

    def draft(self, run_id: str, request: RunRequest, sources: list[SourceRecord]) -> DraftRecord:
        source_ids = [source.source_id for source in sources]
        body = self._build_body(request=request, sources=sources)

        return DraftRecord(
            run_id=run_id,
            topic=request.topic,
            title=f"Draft: {request.topic}",
            body=body,
            source_ids=source_ids,
        )

    def _build_body(self, request: RunRequest, sources: list[SourceRecord]) -> str:
        lines = [
            f"This deterministic draft is based on retrieved sources for: {request.topic}.",
            "",
            "Key items",
        ]

        if not sources:
            lines.append("- No retrieved sources were available for this draft.")

        for source in sources:
            provider = self._source_label(source)
            published_at = source.metadata.get("published_at")
            excerpt = self._clean_excerpt(source.excerpt)

            lines.append(f"- {source.title}")
            lines.append(f"  URL: {source.url}")
            if published_at:
                lines.append(f"  Published: {published_at}")
            if provider:
                lines.append(f"  Source: {provider}")
            lines.append(f"  Summary: {excerpt}")

        lines.extend(
            [
                "",
                (
                    "Note: This is a deterministic source-grounded draft assembled from retrieved "
                    "SourceRecord objects. It is not final reporting and still requires editorial review."
                ),
            ]
        )
        return "\n".join(lines)

    def _source_label(self, source: SourceRecord) -> str:
        source_name = source.metadata.get("source_name")
        if source_name:
            return str(source_name)
        return source.provider

    def _clean_excerpt(self, excerpt: str, max_chars: int = 500) -> str:
        cleaned = " ".join(excerpt.split())
        if len(cleaned) <= max_chars:
            return cleaned
        return cleaned[: max_chars - 3].rstrip() + "..."

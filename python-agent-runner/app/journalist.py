import hashlib

from app.schemas import DraftRecord, RunRequest, SourceRecord, SourceSupport


class JournalistAgent:
    """Deterministic source-grounded draft creator."""

    def draft(self, run_id: str, request: RunRequest, sources: list[SourceRecord]) -> DraftRecord:
        source_ids = [source.source_id for source in sources]
        body = self._build_body(request=request, sources=sources)
        source_support = [self._support_for_source(source) for source in sources]

        return DraftRecord(
            run_id=run_id,
            topic=request.topic,
            title=f"Draft: {request.topic}",
            body=body,
            source_ids=source_ids,
            source_support=source_support,
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

    def _support_for_source(self, source: SourceRecord) -> SourceSupport:
        published_at = source.metadata.get("published_at")
        supported_fields = ["title", "url", "excerpt"]
        if published_at:
            supported_fields.append("published_at")

        excerpt_preview = self._clean_excerpt(source.excerpt, max_chars=180)
        excerpt_hash = hashlib.sha256(source.excerpt.encode("utf-8")).hexdigest()

        return SourceSupport(
            source_id=source.source_id,
            title=source.title,
            url=source.url,
            provider=source.provider,
            published_at=str(published_at) if published_at else None,
            excerpt_hash=excerpt_hash,
            excerpt_preview=excerpt_preview,
            supported_fields=supported_fields,
        )

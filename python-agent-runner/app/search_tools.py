from abc import ABC, abstractmethod

from app.schemas import SourceRecord


class SearchAdapter(ABC):
    @abstractmethod
    def search(self, topic: str) -> list[SourceRecord]:
        """Return normalized source records for a topic."""


class PlaceholderSearchAdapter(SearchAdapter):
    def search(self, topic: str) -> list[SourceRecord]:
        return [
            SourceRecord(
                title=f"Placeholder source for {topic}",
                url="https://example.com/agentic-newsroom-placeholder-source",
                excerpt=(
                    "Placeholder source text for local dry-run execution. "
                    "Replace this adapter before relying on live research."
                ),
                provider="placeholder",
                metadata={"dry_run": True},
            )
        ]


def get_search_adapter(provider: str = "placeholder") -> SearchAdapter:
    if provider != "placeholder":
        raise ValueError(f"Search provider '{provider}' is not implemented yet")
    return PlaceholderSearchAdapter()


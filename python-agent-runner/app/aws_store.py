from abc import ABC, abstractmethod

from app.schemas import FinalStoryRecord


class StoryStore(ABC):
    @abstractmethod
    def save_story(self, story: FinalStoryRecord) -> None:
        """Persist a final story record."""


class InMemoryStoryStore(StoryStore):
    def __init__(self) -> None:
        self.records: dict[str, FinalStoryRecord] = {}

    def save_story(self, story: FinalStoryRecord) -> None:
        self.records[story.run_id] = story


class AwsStoryStore(StoryStore):
    """Placeholder AWS wrapper. Real DynamoDB/S3/SQS calls are intentionally deferred."""

    def __init__(self, dry_run: bool = True) -> None:
        self.dry_run = dry_run

    def save_story(self, story: FinalStoryRecord) -> None:
        if self.dry_run:
            return
        raise NotImplementedError("Real AWS persistence is not implemented in this slice")


def get_story_store(provider: str = "memory", dry_run: bool = True) -> StoryStore:
    if provider == "memory":
        return InMemoryStoryStore()
    if provider == "aws":
        return AwsStoryStore(dry_run=dry_run)
    raise ValueError(f"Storage provider '{provider}' is not implemented")


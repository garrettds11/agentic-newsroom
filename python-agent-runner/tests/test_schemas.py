import pytest
from pydantic import ValidationError

from app.schemas import RunRequest, SourceRecord


def test_run_request_trims_topic() -> None:
    request = RunRequest(topic="  Local newsroom test  ")

    assert request.topic == "Local newsroom test"


def test_run_request_rejects_blank_topic() -> None:
    with pytest.raises(ValidationError):
        RunRequest(topic="   ")


def test_source_record_requires_valid_url() -> None:
    with pytest.raises(ValidationError):
        SourceRecord(
            title="Invalid source",
            url="not-a-url",
            excerpt="Source text",
        )


def test_source_record_accepts_https_url() -> None:
    source = SourceRecord(
        title="Valid source",
        url="https://example.com/source",
        excerpt="Source text",
    )

    assert str(source.url) == "https://example.com/source"


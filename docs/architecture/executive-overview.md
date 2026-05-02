# Executive Overview

Agentic Newsroom is a local-first newsroom cockpit for turning a human topic into a reviewed, source-backed draft.

The system separates creative reporting from editorial judgment. The Journalist Agent gathers sources and drafts a story. The Editor Agent challenges the draft for evidence, clarity, and risk. A deterministic fact-checking layer enforces rules that should not depend on model confidence alone.

## Why This Shape

- **Human control:** PyGPT remains the operator cockpit for topic intake, prompt testing, review, and notifications.
- **Workflow visibility:** n8n provides inspectable workflow orchestration instead of hiding the newsroom process in one script.
- **Deeper runtime ownership:** Python handles agent execution, validation, retries, and persistence because those responsibilities need testable code.
- **Local-first development:** contributors can build and test without cloud writes or production credentials.
- **Cloud-ready persistence:** AWS can store durable state, raw sources, drafts, artifacts, and queued jobs when intentionally enabled.

## Executive Flow

1. A human starts with a topic in PyGPT.
2. n8n coordinates the newsroom workflow.
3. The Python runtime runs research, drafting, editing, and fact checking.
4. Optional external search providers supply source material.
5. Optional AWS persistence archives state and artifacts.
6. The human reviews the final output before publishing or reuse.

See [executive-view.mmd](diagrams/executive-view.mmd) for the simple system view.

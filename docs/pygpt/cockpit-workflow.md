# PyGPT Cockpit Workflow

PyGPT is the local desktop cockpit for Agentic Newsroom. It is used for topic intake, prompt testing, draft review, notification review, and operator feedback.

PyGPT is not the production runtime. The production execution path belongs to n8n for orchestration and the Python Agent Runner for agent execution, deterministic checks, retries, schemas, and persistence adapters.

## Operator Flow

1. Draft or paste a newsroom topic in PyGPT.
2. Optionally test the topic against Journalist and Editor prompt presets.
3. Submit the topic to the n8n webhook.
4. Let n8n call or enqueue work for the Python Agent Runner.
5. Review the runner response, n8n notification, or generated artifact summary.
6. Approve, revise, or reject the story outside any automatic publication path.

## Responsibilities

PyGPT should handle:

- Human topic entry.
- Prompt experiments.
- Manual review and comments.
- Notification display.
- Local tool experiments.
- Operator checklists.

PyGPT should not own:

- Production state transitions.
- Deterministic fact checking.
- Schema validation.
- Retry bookkeeping.
- Durable AWS writes.
- Queue consumption.
- Publication decisions without human review.

## Local-First Workflow

During local development, PyGPT can submit to n8n at:

```text
http://localhost:5678/webhook/newsroom-topic
```

The n8n workflow can then call the Python Agent Runner at:

```text
http://python-agent-runner:8000/runs
```

When testing outside Docker, use:

```text
http://localhost:8000/runs
```

## Review Loop

PyGPT can be used as the place where the human operator reviews:

- Topic fit.
- Source quality.
- Fact-check report.
- Editor decision.
- Required revisions.
- Final story metadata.

Any future notification bridge should send concise summaries to PyGPT, not bypass the human review gate.

## Future MCP and Local Tools

Future PyGPT integrations may include:

- Local file pickers for source packets.
- MCP tools for local artifact browsing.
- Local webhook tools for submitting topics to n8n.
- Desktop notifications for run completion.
- Prompt library management.
- Review checklist tools.

These tools should remain cockpit helpers. Durable workflow control should stay in n8n and the Python Agent Runner.


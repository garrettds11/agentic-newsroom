# Fact-Checking Rules

The deterministic fact checker enforces rules that should not depend on model judgment alone.

## Required Checks

- Every factual claim in the claim inventory must map to at least one source.
- Every cited source must exist in the normalized source list.
- Every source must include a retrieval timestamp.
- URLs must be syntactically valid when the source is web-based.
- Quotes must be traceable to retrieved or user-supplied source text.
- Dates must be explicit for recent, breaking, scheduled, or time-sensitive events.
- Statistics must include a source and measurement context.
- Draft output must match the expected schema.
- Retry count and run state must be valid.

## High-Risk Claim Checks

Apply stricter review to claims involving:

- Legal allegations.
- Medical or health advice.
- Financial advice or market-moving claims.
- Public safety.
- Elections and government officials.
- Breaking news.
- Private individuals.

High-risk claims should require stronger sourcing, preferably primary sources or multiple independent sources.

## Failure Conditions

The fact checker should fail a draft when:

- A claim has no source mapping.
- A cited source is missing.
- A quote cannot be traced.
- A recent event lacks a concrete date or timestamp.
- A high-risk claim relies on weak or single-source evidence without caveat.
- The schema is invalid.
- Required metadata is missing.
- The draft contains invented source details.

## Output

The fact-check report should include:

- Pass or fail status.
- Rule failures.
- Claim identifiers.
- Source identifiers.
- Required remediation.
- Timestamp of validation.

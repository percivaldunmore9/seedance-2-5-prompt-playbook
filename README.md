# Seedance 2.5 — Prompt Playbook For Video Generation

Argolink-focused prompt playbook for video generation for Seedance 2.5. This repository is a self-contained integration reference: it explains the request shape, the asynchronous lifecycle where applicable, safe retries, and the failure states that matter in production.

[Seedance 2.5 model page →](https://argolink.io/gh-seedance-2-5-prompt-playbook) · [Argolink API docs →](https://argolink.io/gh-unified-api-docs)

The model page is authoritative for live availability, pricing, limits, and fields. This repository gives the workflow a searchable home; it does not invent a second model catalog.

## What is inside

- `docs/model-contract.md`: model-specific facts checked against the current Argolink catalog.
- `docs/workflow.md`: the intent behind this repository and the decision points that prevent accidental resubmission.
- `examples/request.sh` and `examples/client.py`: safe, runnable request examples using `ARGOLINK_API_KEY`.
- `tests/test_repository.py`: offline checks for the public contract and examples.
- `ARGOLINK.md`: public-boundary rules for contributors.

## Quick start

Set the key only in your shell or secret manager, then run the example:

```bash
export ARGOLINK_API_KEY='your-key'
./examples/request.sh
```

The example uses model ID `seedance-2.5` and endpoint family `/v1/videos/generations`. Submit once, persist the returned task ID, and poll the documented task endpoint before downloading the media URL. A timeout is not evidence that a job failed, so do not submit the same generation again automatically.

## Model facts

- Model ID: `seedance-2.5`
- Argolink model page: `https://argolink.io/gh-seedance-2-5-prompt-playbook` (tracked shortlink; destination is the model page)
- Endpoint family: `/v1/videos/generations`
- Listed video tiers: 480p `$0.1352`/second, 720p `$0.30043`/second, 1080p `$0.74555`/second.
- Base generation rate: `$0.1352`/second before any tier multiplier.

## Scope

This repository has one clear search intent: **prompt playbook for video generation**. It keeps the integration boundary small enough for a developer or an AI assistant to answer a concrete question, while linking the live Argolink model page for changes.

## Safety

Never commit an API key, a returned media URL containing a private token, or production input. Examples are deliberately small and do not make a request during tests.

# Unified AI Chatbot

> **Portfolio reconstruction / demonstration.** This is a reference implementation based on a described project, not a verified copy of original production source or evidence of deployment.

## Problem and purpose

Claude CLI with SQLite conversation history. This demo makes the workflow reproducible with synthetic data or mocked API responses and exposes the assumptions that need review before real use.

## Stack and flow

Python, Anthropic SDK, SQLite, python-dotenv.

CLI -> bounded recent context -> injected Claude client -> atomic SQLite turn persistence. /history, /search keyword and /quit are supported.

`src/` contains processing code, `tests/` contains offline regression tests, `.github/workflows/checks.yml` runs offline checks on pushes and pull requests. Samples are synthetic; `output/` and runtime files are ignored.

## Setup and execution

Use Python 3.12 and an isolated virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.lock
# Copy .env.example to .env and configure an authorized API key and available model.
python -m src.chatbot
```

`requirements.txt` records direct dependencies; `requirements.lock` pins the resolved runtime set. Offline transformations/tests do not require API credentials after installation. No API or email call is executed automatically.

## Implemented behavior and example output

Mocked responses verify multi-turn context, failed/empty responses, context trimming and atomic persistence. SQL search escapes literal %/_ characters. Failed requests do not save orphan user turns. Up to 20 prior messages and a 12,000-character budget bound outbound context; this is not a token counter.

## Tests

```powershell
python -m unittest discover -s tests -v
python -m compileall -q src tests
```

The suite uses synthetic files and mocked service responses. See the preparation validation report for actual results and environment limitations; a workflow file is not evidence of a completed GitHub Actions run.

## Limitations and future work

Single local conversation, plaintext local history, no web UI, access controls, retention scheduler or live API validation. Model access/cost depends on your account. Future work: conversation IDs, token-aware limits and explicit retention controls.

## Data and publication

Do not commit real customer records, tokens, production identifiers, proprietary drawings, pricing data or personal photos. Keep `.env` local. Error messages from the adapter omit request URLs and credential values. Local file paths/messages can still reveal context; review logs before sharing.

This repository contains a reconstructed demonstration prepared for a public engineering portfolio. See `docs/PROVENANCE.md` for its origin and limits. No original employer/client implementation is included. No license is granted by this publication; third-party dependencies retain their own license terms.

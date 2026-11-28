# Devlog

## 2026-11-26
- Did: Initialized sika_x with uv, ruff, pytest, config loader, and ADRs (M0).
- Blocked: None.
- Next: Push to GitHub and begin M1 (Walking Skeleton).

## 2026-11-28
- Did: Built M1 walking skeleton (models, SQLite/SQLAlchemy db, pipeline, FastAPI /health + /v1/chat, request_id logging, 9 passing tests).
- Blocked: None.
- Next: Start M2 (Brain v1 — LLMClient interface, sika_x Pidgin/English persona, cost logging).

## 2026-11-28 (M2)
- Did: Built M2 Brain v1 (LLMClient interface, GeminiClient + MockLLMClient, persona.md, <user_message> delimiter, retry-once + fallback, token/cost logging in SQLite, 18 passing tests).
- Surprises: gemini-4-hydrogen free tier capped at 20 RPD; switched default to gemini-3.5-flash-lite (~$0.00025-$0.0005/msg). Tightened persona.md after noticing English->Pidgin drift and a guessed product name.
- Next: Start M3 (Users, sessions, conversation history, /start /reset /help).

# 0002: Why a Lean In-House Loop Instead of an Agent Framework

Date: 2026-11-26
Status: Accepted

## Context
Building `sika_x` part-time for 20-50 alpha testers in Ghana. Frameworks like LangChain add heavy dependencies and hide errors and token costs.

## Decision
Build our own small, explicit pipeline (`core/pipeline.py`) and bounded tool loop (`core/loop.py`) in Python behind a single `LLMClient` interface.

## Alternatives Rejected
- LangChain / multi-agent frameworks: too heavy, harder to debug and control cost.

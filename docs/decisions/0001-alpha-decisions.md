# 0001: Alpha Baseline Decisions (D1-D7)

Date: 2026-11-26
Status: Accepted

| ID | Decision | Choice |
|----|----------|--------|
| D1 | First audience | Students, with traders as second |
| D2 | Engine | Lean in-house loop behind `agent.reply(user, msg)` |
| D3 | Model strategy | Cheap fast model default, stronger on escalation, provider-agnostic |
| D4 | Database | SQLite for alpha, Postgres at beta |
| D5 | First channel | Telegram (easiest), then web, then WhatsApp |
| D6 | Language policy | Mirror user; simple Twi best-effort; fallback to English if unsure |
| D7 | Working name | sika_x |

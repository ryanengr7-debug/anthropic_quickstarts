# CambioML Assessment — Implementation Progress Log

**Purpose:** Track what has been **implemented** (not planning). Update this file as work completes.  
**Plan reference:** [CAMBIO_ML_ASSESSMENT_PLAN.md](./CAMBIO_ML_ASSESSMENT_PLAN.md) — master checkboxes are in **Section 2 (Task list)** of that file; use this file for dated log entries.

**Instructions:** After each meaningful change, append a dated entry under **Log** and tick boxes when the item is truly done (tested / documented).

---

## Checklist (sync with plan phases)

- [x] **Spike:** `sampling_loop` callable without Streamlit (smoke test documented).
- [x] **FastAPI app:** project layout, config, health route.
- [x] **Database:** schema + migrations + session/message CRUD.
- [x] **Session API:** `POST/GET/DELETE /sessions` (and metadata as designed).
- [x] **Messages API:** `POST` user message; `GET` history with pagination.
- [x] **Worker supervisor:** dynamic spawn per new session (not fixed “2”); configurable cap (`SessionWorkerSupervisor`, `MAX_CONCURRENT_SESSIONS`).
- [x] **Isolation (hooks):** per-session `display_num` + `workspace_dir` on session rows and API; teardown on `DELETE` / app shutdown.
- [x] **Computer use integration:** `sampling_loop` runs in session worker after `POST .../messages` (background task); events persisted to `agent_messages`.
- [x] **Real-time:** SSE (`GET /sessions/{id}/events`) + replay buffer; WebSocket not implemented (optional later).
- [ ] **Concurrency:** two sessions run in parallel without blocking (manual + noted in README).
- [x] **VNC / noVNC:** session API exposes `vnc_raw_port`, `vnc_uri`, `novnc_url` when configured; README pattern for Docker ports (5900/6080).
- [x] **File management (minimal):** `POST/GET /sessions/{id}/files`, download by name, `SESSION_FILES_ROOT`.
- [x] **Docker Compose:** `docker-compose.yml` (Postgres + API), `Dockerfile.session_api`, override example, README + shot list.
- [x] **Web frontend:** `/demo/` HTML+JS (`frontend/`) — sessions, chat, SSE, uploads, noVNC link.
- [x] **README (English):** Author placeholder line 1; `docker compose` + `curl`; Mermaid sequence; link to video shot list (further polish before submit).
- [x] **Demo video script:** `computer-use-demo/docs/DEMO_VIDEO_SHOTLIST.md` (Usage Case 1 + 2 + parallel + sound reminder).
- [ ] **Human deliverables:** private repo, collaborators invited, video recorded with sound, completion email sent.

---

## Log (append newest first)

| Date | Author | What was implemented |
|------|--------|----------------------|
| 2026-04-17 | _(candidate)_ | **Phase F:** `Dockerfile.session_api`, `docker-compose.yml` (Postgres+API), `docker-compose.override.example.yml`, `asyncpg` in session requirements; README Author line 1, Compose + `curl` + Mermaid sequence, worker/display notes; `docs/DEMO_VIDEO_SHOTLIST.md`; `.gitignore` `docker-compose.override.yml`; `tests/phase_f_test.py`. |
| 2026-04-17 | _(candidate)_ | **Phase E:** VNC hints (`vnc_hints.py`, session responses); file routes `routers/session_files.py` + `SESSION_FILES_ROOT` / `MAX_UPLOAD_BYTES`; web UI `/demo/` (`frontend/index.html`, `app.js`); `tests/phase_e_test.py`. |
| 2026-04-17 | _(candidate)_ | **Phase D:** `session_service/agent_runner.py` (`execute_message_turn` → `sampling_loop` + DISPLAY/workspace hint); worker queue + `notify_user_message`; `BackgroundTasks` after `POST .../messages`; SSE `routers/stream_events.py` + replay buffer in `worker_runtime.py`; config for model/provider/tools/SSE poll; `create_app(..., agent_message_turn=...)` for tests; `tests/phase_d_test.py`. |
| 2026-04-17 | _(candidate)_ | **Phase C tests:** `tests/phase_c_test.py` (API: workers on/off, distinct displays, list metadata, workspace on disk, 503 cap + display exhaustion with no orphan rows, delete/teardown, display reuse); expanded `tests/worker_supervisor_test.py` (detach no-op, workspace after detach, `shutdown_all`). |
| 2026-04-17 | _(candidate)_ | **Phase C:** `session_service/worker_supervisor.py` — per-session asyncio worker placeholder, `DISPLAY` slot allocation, workspace dirs, cap + teardown; config (`ENABLE_SESSION_WORKERS`, `MAX_CONCURRENT_SESSIONS`, workspace root, display range); session model/API fields; tests default workers off; `tests/worker_supervisor_test.py` + session API tests for 503 cap and detach. |
| 2026-04-17 | _(candidate)_ | **Phase A:** Added `computer_use_demo/cli_spike.py` (CLI harness for `sampling_loop`); added `docs/PHASE_A_DISCOVERY.md` (ports, single-session notes, env vars, smoke commands); linked from `computer-use-demo/README.md`. |
| 2026-04-17 | _(candidate)_ | **Phase A tests:** `tests/cli_spike_test.py` — provider parsing, API key resolution, early `main()` exits without SDK import, subprocess `--help`, discovery doc presence, mocked `sampling_loop` args (3.11+); `cli_spike` early validation before heavy imports; `_load_loop_exports()` hook for tests. |
| 2026-04-17 | _(candidate)_ | **Phase B:** `session_service/` FastAPI app — async SQLAlchemy models, `GET /health`, session CRUD + message append/list with pagination, CORS + `DATABASE_URL`, `create_all` lifespan; `session_service_requirements.txt` + dev-requirements; `tests/session_service_test.py` (Starlette `TestClient`); README “Session API” section. |
| 2026-04-17 | _(candidate)_ | **Phase B tests expanded:** `tests/session_service_test.py` — 36 cases (CRUD, 404/422 paths, pagination bounds, OpenAPI `/openapi.json`, CORS wildcard + allowlist, message payload/schema, `CreateMessageBody` rejects whitespace-only `role`). |

---

## Notes / blockers

_(Optional: link PRs, commands that broke, decisions that diverged from the plan.)_

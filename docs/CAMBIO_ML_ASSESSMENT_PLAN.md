# CambioML Coding Challenge — Implementation Plan

**Assessment:** Claude Computer Use — scalable backend for agent session management  
**Confidentiality:** Treat all assessment materials as NDA-covered; do not redistribute.  
**This document:** Engineering plan only (no implementation in the commit that adds this file).

---

## 1. Goals (what “done” means)

| Area | Requirement |
|------|-------------|
| **Reuse** | Build on `computer-use-demo/` from this repo (Anthropic computer-use agent loop, tools, Docker baseline). |
| **Replace Streamlit** | Remove Streamlit as the primary UI; core control via **FastAPI**. |
| **APIs** | Session create/manage; send user messages to active sessions; list/retrieve history; VM/VNC access story for clients. |
| **Real-time** | **WebSocket** or **SSE** (or both where justified) for token/tool/progress events as the agent runs. |
| **Persistence** | Database for sessions, messages, tool calls/results (and any metadata needed for replay). |
| **Concurrency** | **Simultaneous** sessions without global locks that serialize unrelated work; **no race conditions** on shared state. |
| **Docker** | Images + **Compose** for local dev and a path to remote/prod deployment. |
| **Frontend** | **Simple HTML/JS** demo (or external static generator). **Not allowed:** Swagger UI, OpenAPI UI, Streamlit as the demo surface. (OpenAPI schema generation in FastAPI is fine for README/docs; just do not ship Swagger as the required demo UI.) |
| **Deliverables (human)** | Private GitHub repo; README per spec; collaborators; **5-minute demo video with sound**; email repo link when ready. |

---

## 2. Task list (master checklist)

Use this list for planning and tracking in-repo. For dated implementation notes, update [CAMBIO_ML_ASSESSMENT_PROGRESS.md](./CAMBIO_ML_ASSESSMENT_PROGRESS.md).

### Phase A — Discovery & spike

- [x] Read `computer-use-demo` (`loop.py`, `streamlit.py`, Docker/image); note ports and single-session assumptions.
- [x] Spike: invoke `sampling_loop` from a minimal harness (no Streamlit); document env vars, model id, and smoke-test command. (See [PHASE_A_DISCOVERY.md](./PHASE_A_DISCOVERY.md) and `python -m computer_use_demo.cli_spike`.)

### Phase B — FastAPI & persistence

- [x] FastAPI app layout: config, logging, CORS if needed, health route. (`session_service/` — `create_app`, `GET /health`, `CORS` from env.)
- [x] Database: schema (sessions, messages/events, optional turns); migrations or init scripts. (SQLAlchemy async + `create_all` in lifespan; tables `agent_sessions`, `agent_messages`.)
- [x] `POST /sessions`, `GET /sessions`, `GET /sessions/{id}`, `DELETE /sessions/{id}` implemented and tested. (`tests/session_service_test.py`)
- [x] `POST /sessions/{id}/messages`, `GET /sessions/{id}/messages` (pagination) implemented and tested.

### Phase C — Workers, isolation, concurrency

- [x] Supervisor: **dynamically** spawn a worker (asyncio task per session; placeholder until Phase D); cap via **config** (`MAX_CONCURRENT_SESSIONS`), not a hard-coded “only 2”.
- [x] Per-session isolation **hooks**: allocated `DISPLAY` index + workspace path stored on session and returned by API (Firefox/container wiring in Phase D/E).
- [x] Teardown: cancel worker + remove workspace on `DELETE` / shutdown; `POST /sessions` rolls back DB row on attach failure (503).
- [x] Concurrency: short `asyncio.Lock` only around registry mutation; `tests/worker_supervisor_test.py` exercises parallel `attach_worker` (not serialized by a long global lock).

### Phase D — Computer use integration & real-time streaming

- [x] Integrate existing `sampling_loop` + tools inside the worker (async worker queue per session; `execute_message_turn` in `session_service/agent_runner.py`).
- [x] Persist streamed events with stable ordering (`sequence` per session): `run_start`, `assistant_block`, `tool_result`, `api_error`, `run_error`, `run_complete` (+ existing user rows from `POST .../messages`).
- [x] Expose **SSE** (`GET /sessions/{id}/events`) with per-session subscriber queues + short replay buffer; other sessions are not blocked (separate workers / locks).

### Phase E — VNC, files, web frontend

- [x] Per-session VNC hints: `vnc_raw_port`, `vnc_uri`, optional `novnc_url` on session JSON when `SESSION_VNC_PUBLIC_HOSTNAME` (and optionally `NOVNC_HTTP_BASE`) are set; port = `VNC_PORT_BASE` + `display_num` (see README).
- [x] Minimal file APIs: `POST/GET /sessions/{id}/files`, `GET /sessions/{id}/files/{name}`; storage under `SESSION_FILES_ROOT/{session_id}/`; deleted with session.
- [x] Static **HTML + JS** frontend at **`/demo/`** (`frontend/`) — sessions, messages, uploads, SSE, noVNC link when URLs are configured (**no** Streamlit / Swagger / OpenAPI UI).

### Phase F — Docker & documentation

- [x] `Dockerfile.session_api` — slim API image (separate from full Ubuntu desktop `Dockerfile`).
- [x] `docker-compose.yml` + `docker-compose.override.example.yml`: Postgres + API; README documents worker/display vs. slim image.
- [x] README (English): **Author** placeholder line 1; `docker compose up`, `curl` examples, link to demo shot list.
- [x] README: **Mermaid** sequence (session create → message → worker → SSE → persist).
- [x] Demo video shot list: `computer-use-demo/docs/DEMO_VIDEO_SHOTLIST.md`.

### Phase G — Human deliverables

- [ ] Private GitHub repository with full source.
- [ ] Invite collaborators: **lingjiekong**, **ghamry03**, **goldmermaid**, **EnergentAI** (as GitHub users/orgs per instructions).
- [ ] Record demo video: repo overview → services up → Usage Case 1 (Dubai) → Usage Case 2 (Tokyo + New York side-by-side) → streaming + “new task” after complete.
- [ ] Reply to assessment email with private repo link (completion notice).

### Rubric self-check (before submit)

- [ ] **Usage Case 1:** New session → “Search the weather in Dubai” → Firefox + Google + summarized result in **real time**.
- [ ] **Usage Case 2:** Session A (Tokyo) **still running** while session B (New York) starts; both **parallel** (not queued); two browser tabs; **two Firefox contexts** visible; both stream results.
- [ ] Architecture is **not** a disguised fixed pool of 2; workers/contexts spawn dynamically within configured limits.

---

## 3. Hard evaluation constraints (must design for these explicitly)

### 3.1 Demo Usage Case 1 (Dubai weather)

- New chat session → prompt **“Search the weather in Dubai.”**
- Observe **Firefox** + **Google search** + **summarized result**, with updates in **real time**.

### 3.2 Demo Usage Case 2 (Tokyo + New York — **strict parallel**)

- **While** session A runs (“Search the weather in **Tokyo**”), start session B (“Search the weather in **New York**”) **without waiting** for A to finish.
- **Failure modes called out by assessors:** sequential queue; fixed pool of 2 workers only; “multiple displays” that are fake/demo-only without real architecture.
- **Pass bar:** architecture **dynamically allocates** an execution context (worker/process/container slot) per new session request, bounded only by configurable limits and host resources—not a hard-coded “only 2 sessions” product.
- **Visual:** two browser tabs (User A / User B), **two separate Firefox automation contexts** running **at the same time**, both streaming summaries in real time.

### 3.3 “Streamlit-like” behavior (without Streamlit)

- After submit: stream intermediate steps (model text, tool use, tool results, errors).
- After completion: UI returns to a state where the user can **enter a new task** in that session.

### 3.4 Documentation (English)

- README: **Author:** full name on **first line**; setup; how to run; env vars; architecture overview.
- **API documentation** (can be Markdown tables + example `curl`/`httpx`—not Swagger-as-product).
- **Sequence diagram(s)** (Mermaid in README is acceptable).

### 3.5 Video (5 minutes, with sound)

1. Repo / codebase overview  
2. Service launch + endpoints (without relying on forbidden demo UIs)  
3. Usage Case 1 + Usage Case 2 + streaming + post-task prompt behavior  

---

## 4. Current stack (baseline to reuse)

- **`computer-use-demo/computer_use_demo/loop.py`**: `sampling_loop` — Claude beta messages + computer/bash/edit tools.  
- **`computer-use-demo/computer_use_demo/streamlit.py`**: Today’s UI (to be replaced/superseded by API + static HTML demo).  
- **Docker / image**: existing VM-style environment (VNC, display ports, etc.) — reuse patterns; extend for **multi-session isolation**.

---

## 5. Target architecture (high level)

```text
[Static HTML/JS demo]  ──REST/WS/SSE──►  [FastAPI]
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
              [Session registry]  [DB]          [Worker supervisor]
                    │                 │                 │
                    └────────┬────────┘                 │
                             ▼                          ▼
                    messages / events            per-session agent runner
                    (CRUD, list, replay)         (subprocess or extra
                                                  container; own DISPLAY)
                             │
                             ▼
                    [Existing sampling_loop + tools]
```

**Design principles:**

1. **API process is not the agent process** for long runs: avoid blocking the event loop; isolate crashes (agent segfault / browser death) from the control plane.  
2. **One logical session ↔ one isolated execution context** (separate `DISPLAY`, separate profile dir, or separate container) so two Firefox instances cannot fight over the same X11 screen.  
3. **Dynamic workers:** supervisor starts a worker when a session is created (or on first message), up to `MAX_CONCURRENT_SESSIONS` from env (not a magic `2` in code). Default can be high; demo shows 2+ in parallel.  
4. **Streaming:** worker pushes events to a per-session async queue; FastAPI WebSocket or SSE reader consumes from that queue; same events persisted to DB (ordering + idempotency where needed).  
5. **Race-free shared state:** DB transactions for writes; in-memory maps guarded with `asyncio.Lock` per session id (not one global lock for all sessions).

---

## 6. API surface (draft — refine during implementation)

**REST (examples):**

- `POST /sessions` — create session; returns `session_id`, optional `vnc_url` / `vnc_port` / `websocket_path`.  
- `GET /sessions` — list sessions (filters: active, completed).  
- `GET /sessions/{id}` — metadata + status.  
- `GET /sessions/{id}/messages` — paginated chat history (user, assistant, tool_call, tool_result).  
- `POST /sessions/{id}/messages` — append user message and **kick off** agent turn (returns 202 + `turn_id` or blocks only until accepted).  
- `DELETE /sessions/{id}` — teardown worker + release resources.

**Real-time:**

- `GET /sessions/{id}/events` — **SSE** stream of JSON events, **or**  
- `WS /sessions/{id}/ws` — bidirectional (optional: client ping, server events).

**VNC:**

- Document how each session maps to **its own** noVNC URL or port (spawned sidecar or multi-service compose). If single legacy image is one-desktop-only, **document the gap** and implement **N replicas** or **N processes with N Xvfb** so assessors see true parallel Firefox.

**File management (appendix UI):**

- Minimal: `POST /sessions/{id}/files` multipart upload + `GET /sessions/{id}/files/{file_id}` or list endpoint; store on disk under session-scoped path + DB index.

---

## 7. Data model (draft)

- **Session:** `id`, `status` (created/running/completed/failed), `created_at`, `updated_at`, `worker_pid` or `worker_container_id`, `display_num`, `error_message`.  
- **Message / event:** `id`, `session_id`, `role` or `type` (user/assistant/tool_use/tool_result/system), `payload` (JSON), `sequence`, `created_at`.  
- Optional **Turn** table if you need grouping for retries.

Use a real DB in Docker (e.g. **PostgreSQL**); **SQLite** acceptable for dev if README clearly states prod uses Postgres.

---

## 8. Concurrency & worker model (critical path)

| Approach | Pros | Cons |
|----------|------|------|
| **Subprocess per session** on one VM | Dynamic; clear isolation with separate `DISPLAY` | Host resource limits; need Xvfb/x11vnc per display |
| **Sidecar container per session** (compose scale / Docker API) | Strong isolation | Heavier; orchestration complexity |
| **Fixed pool of 2** | Easy demo | **Explicit failure per rubric** |

**Chosen direction (to implement):** document in README — recommend **subprocess or container-per-session** with **supervisor** that spawns on `POST /sessions` (or first message), with **configurable** `MAX_CONCURRENT_SESSIONS`, and health checks + cleanup on delete.

---

## 9. Docker & Compose

- **Services:** `api` (FastAPI), `db`, optional `reverse-proxy`, optional **template** for per-session worker (if using compose scale, document `docker compose up --scale worker=N` vs dynamic API-driven spawn).  
- **Volumes:** Postgres data; per-session file storage.  
- **Ports:** API, VNC/noVNC per session strategy (port range or dynamic publish).  
- **Env:** `ANTHROPIC_API_KEY`, DB URL, concurrency limits, model id.

---

## 10. Frontend (allowed stack)

- Single-page **static** `index.html` + `app.js`: session list, “new task”, message list, SSE or WebSocket client, iframe or link for **noVNC** per session.  
- Serve via FastAPI `StaticFiles` or nginx.  
- **No** Streamlit / Swagger / OpenAPI browser UI as the demo.

---

## 11. Implementation phases (ordered)

1. **Spike:** Run existing `sampling_loop` from a non-Streamlit harness (script or minimal FastAPI route) to confirm API keys and tool behavior.  
2. **FastAPI skeleton:** health, session CRUD stubs, DB migrations.  
3. **Worker supervisor + session isolation:** dynamic spawn; env-driven max; teardown.  
4. **Integrate `sampling_loop`:** callbacks → event queue → WS/SSE + DB append.  
5. **History + replay APIs:** list messages; resume session.  
6. **VNC story:** per-session display + noVNC URL in API response + demo HTML.  
7. **File endpoints (minimal).**  
8. **Compose:** api + db + dev overrides; README.  
9. **Polish:** errors, timeouts, cancel session, structured logging.  
10. **README + Mermaid diagrams + demo script** for video.  
11. **Human steps:** private repo, collaborators, record video, email link.

---

## 12. Risks & mitigations

| Risk | Mitigation |
|------|------------|
| Upstream image assumes **one** desktop | Spawn additional Xvfb+VNC stacks or multiple container instances; document ports. |
| `sampling_loop` is async and long | Run in dedicated task/thread/process per session; never `await` two unrelated sessions on one shared lock. |
| DB writes from stream flood | Batch insert or write-ahead in worker; transaction per event if needed. |
| “Vibe coding” rejection | Keep design docs (this plan + README architecture) aligned with code; own tradeoffs explicitly. |

---

## 13. Out of scope (unless time permits)

- Kubernetes manifests (Compose + clear prod story is enough unless you already have k8s).  
- Auth/multi-tenant hardening (optional nice-to-have).  
- Full production observability (basic structured logs sufficient).

---

## 14. References (internal to repo)

- `computer-use-demo/README.md` — ports, Docker run.  
- `computer-use-demo/computer_use_demo/loop.py` — integration point.  
- `CLAUDE.md` — lint/test commands for Python subtree.

---

*End of plan. Check off **Section 2 (Task list)** here and/or update [CAMBIO_ML_ASSESSMENT_PROGRESS.md](./CAMBIO_ML_ASSESSMENT_PROGRESS.md) as tasks complete.*

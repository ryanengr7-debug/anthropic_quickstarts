# Phase A — Discovery notes (computer-use-demo)

This document captures what we learned from reading `loop.py`, `streamlit.py`, Docker/README, and from the **CLI spike** (`computer_use_demo.cli_spike`).

---

## 1. Ports and entrypoints (from README / image)

| Port | Service |
|------|---------|
| **8080** | Combined UI (Streamlit + embedded desktop) — primary “demo app” URL |
| **8501** | Streamlit only |
| **6080** | noVNC (`/vnc.html`) — desktop view |
| **5900** | Raw VNC |

Settings such as API key and custom system prompt persist under **`~/.anthropic/`** when that directory is mounted.

**Screen size:** `WIDTH` and `HEIGHT` env vars (see README).

---

## 2. Single-session assumptions (important for Phase C)

- **README (computer-use-demo):** components are “weakly separated”; the agent loop runs **inside the environment being controlled**; **one session at a time**; restart/reset between sessions if needed.
- **Streamlit:** global `st.session_state` holds messages, tools, and “in sampling loop” flag — one browser user implicitly maps to one conversation.
- **Desktop:** system prompt in `loop.py` assumes **`DISPLAY=:1`** and a single Ubuntu desktop (Firefox ESR, etc.). Concurrent **independent** Firefox sessions for multiple users will require **separate displays or containers** (see assessment plan Phase C).

---

## 3. How Streamlit calls the agent

File: `computer_use_demo/streamlit.py`

- Builds `messages` as a list of `BetaMessageParam`-shaped dicts (`role` + `content` list of blocks).
- On new user input, appends a user message whose `content` may include `BetaTextBlockParam` and optional interruption tool results.
- Awaits **`sampling_loop(...)`** with:
  - `model`, `provider`, `api_key`, `tool_version`, `max_tokens`, `thinking_budget`, `token_efficient_tools_beta`, `only_n_most_recent_images`, `system_prompt_suffix`
  - **`output_callback`**: renders assistant blocks (text, thinking, tool_use).
  - **`tool_output_callback(result, tool_id)`**: stores `ToolResult` per tool use id for richer UI than API tool_result alone.
  - **`api_response_callback(request, response, error)`**: debug HTTP tab.

The spike replaces UI callbacks with **logging to stdout**.

---

## 4. Environment variables (smoke test and normal runs)

| Variable | Role |
|----------|------|
| **`ANTHROPIC_API_KEY`** | Required for `API_PROVIDER=anthropic` (or place key in `~/.anthropic/api_key`). |
| **`API_PROVIDER`** | `anthropic` (default), `bedrock`, or `vertex` — same as Streamlit. |
| **`ANTHROPIC_MODEL`** | Optional; CLI `--model` default is `claude-sonnet-4-5-20250929`. |
| **`COMPUTER_USE_TOOL_VERSION`** | Optional; must match model capabilities (default `computer_use_20250124`). |
| **`SPIKE_PROMPT`** | Optional default user text for the CLI if `--prompt` omitted. |
| **`SPIKE_MAX_TOKENS`** | Optional cap for `--max-tokens` (default 8192). |
| **`ONLY_N_MOST_RECENT_IMAGES`** | Optional; passed through to `sampling_loop` (default 3). |
| **`CUSTOM_SYSTEM_PROMPT`** | Optional suffix appended to the built-in system prompt. |

Bedrock / Vertex need their respective credentials as documented in the main README.

---

## 5. Smoke test command (no Streamlit)

From the **`computer-use-demo/`** directory (with dependencies installed, e.g. after `./setup.sh`, or **inside the Docker image** where the desktop exists):

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
# Cheap path: model answers in text only (default prompt avoids tools)
python -m computer_use_demo.cli_spike

# Exercise computer tools (uses API + desktop; costs more)
python -m computer_use_demo.cli_spike --prompt "Take one screenshot and describe what you see in one sentence."

# Verbose HTTP logging
python -m computer_use_demo.cli_spike -v --prompt "Say hello in one sentence."
```

Exit code **2** means missing API key for Anthropic. A successful run logs assistant blocks and tool results until the model returns without further tool calls.

### Automated tests (Phase A)

From `computer-use-demo/`:

```bash
pytest tests/cli_spike_test.py -v
```

The suite covers CLI validation, API key loading, subprocess `--help`, and (on **Python 3.11+** with `anthropic` installed) mocked `sampling_loop` integration. On Python 3.10, two integration tests are **skipped** because `enum.StrEnum` is required by `computer_use_demo.tools` (match CI: Python 3.11.6 per `.github/workflows/tests.yaml`).

---

## 6. Code references

- Agent loop: `computer_use_demo/loop.py` — `sampling_loop`, `APIProvider`, `SYSTEM_PROMPT`.
- UI integration: `computer_use_demo/streamlit.py` — `sampling_loop` invocation and callbacks.
- Tool versions: `computer_use_demo/tools/groups.py` — `TOOL_GROUPS_BY_VERSION`.

---

*Phase A deliverable: this note + `python -m computer_use_demo.cli_spike`.*

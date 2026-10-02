# CLAUDE.md

Companion code for the **A2A Explained** video series (the sequel to MCP Explained).
The series repo next door owns the plan; this repo owns the code and the captures.

**State (2026-09-24):** `trial/` holds the implementation trial, done: the analyst
(`analyst.py`, `server.py`), one client script per video moment, the wiretap
(`tap.py`), the MCP bridge (`mcp_server.py`, `analyst_mcp.py`), the briefing agent
(`briefing.py`), the currency sample ported to the pinned SDK (`currency-agent/`),
and `captures/` with every run and its provenance. Video folders so far:
`04-first-agent/` (`ask.py` and the currency agent, unchanged from the trial) and
`05-analyst/` (the served analyst at its minimum: the trial's `server.py` without
the period check, the push wiring, or the trial plumbing), both 2026-09-25, and
`06-task-life/` (2026-10-02: `analyst.py` and `server.py` identical to
`05-analyst/`, plus the trial's `poll.py` and `stream.py`).
Each video's captures are re-run from its folder with the MCP series' capture
harness and moved next door. The rest of `trial/` is reshaped per video as 06
onward are authored. The sections below describe the
job as it was set; `trial/README.md` and `trial/captures/README.md` say what
exists, and `../a2a-explained/series-plan.md` carries what the trial settled.

**Read next door when you need it:** `../a2a-explained/series-plan.md` (the arc, the
examples, the verified protocol facts, the trial), `../a2a-explained/README.md` (how
the videos are produced, what the viewer already knows), `../a2a-explained/CLAUDE.md`
(session rules for the series repo).

## The first job: the implementation trial

Build the series' one running example and prove it can do what the videos promise,
**before any video is storyboarded.** Capture the real exchanges; every video later
replays these captures rather than recording anything live.

**The analyst** — a stock brief agent served over A2A with the pinned `a2a-sdk`:
given a ticker and a period, it fetches the price history (`yfinance`, as the MCP
series did), decides what is worth saying, and returns a short brief as an artifact.
It must visibly choose its own steps; a model with one lookup and no judgement is
the MCP stock tool with extra plumbing and does not earn its place. A deterministic
check requires the period before any model call — that is what triggers the
clarification. Keep it a brief, never advice.

**Five required runs**, in order, each captured with provenance (commit, model,
`a2a-sdk` version, date):

1. One genuine brief, with the agent's choices observable (what it fetched, what it
   said and why).
2. Observable task progress on that run: the task seen `submitted` → `working` →
   `completed` by polling `GetTask`, then the same via the streaming send with
   status and artifact events arriving as they happen.
3. One clarification: ask about a ticker with no period; the task stops in
   `input-required` with the agent's question.
4. The same task resumed and completed after the reply, on the same task and
   `contextId`.
5. A disconnect: the client drops while the agent is still working, processing
   continues on the server, then the client either reconnects and subscribes to the
   task and retrieves the brief, or receives it at a registered push-notification
   webhook. Try both; note which is simpler to show.

**Also lock the third-party agent** for videos 04 and 10: the A2A project's
currency-conversion sample from `a2aproject/a2a-samples`, run locally as a black box.
Criteria: it runs at the pinned SDK, it creates a Task for our message (not a direct
Message reply), and it asks back when the currency is missing. If it fails any of
these, find another sample by the same criteria.

**Report back** into `../a2a-explained/series-plan.md`, "Open items" and "Protocol
facts": the served-agent line count, whether the SDK's emitted JSON-RPC method
strings match spec v1.0 (`a2a.SendMessage` and family), whether the SDK serves the
card at `/.well-known/agent-card.json` by default, which mechanism run 5 settled on,
and the currency-sample verdict. Rewrite those sections to the new state; the series
plan carries no history.

## Conventions (copied from `../mcp-explained-code/`, read its README for the why)

- **One runnable folder per video state**, named for the video (`05-analyst/`,
  `06-07-analyst/`, …), each with `requirements.txt` (pinned exactly — the repo
  promises the environment the video was captured in), `.env.example`, and code in
  the exact form the video shows. Two videos share a folder only where the code is
  identical. The trial can start in a `trial/` folder and be reshaped into video
  folders once the plan settles.
- **Model provider:** any OpenAI-compatible endpoint via `.env` —
  `LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY` — using the `openai` client, exactly as
  the MCP code does. Default `.env.example` values there: OpenRouter with
  `anthropic/claude-sonnet-5`. Never commit `.env`.
- **Python 3.11+, venv per folder**, `pip install -r requirements.txt`.
- **Captures** live with the video repo (`../a2a-explained/videos/NN-slug/assets/
  captures/`), not here; until video folders exist, keep trial captures under
  `trial/captures/` with a README stating provenance, and move them later.
- **Code readable on screen:** a few dozen lines per file, plain names, no framework
  beyond the SDK. The viewer reads this code; write it to be read.
- Video 09 puts the analyst's lookup behind MCP: reuse the stock server from
  `../mcp-explained-code/06-stock-server/` as-is.
- Every video that shows code pins a commit of this repo; keep history clean enough
  to pin. GitHub remote: https://github.com/rt-adesai/a2a-explained-code

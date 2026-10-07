# A2A Explained — companion code

Runnable code for the **A2A Explained** video series, the sequel to
[MCP Explained](https://github.com/abhydesai/mcp-explained-code). Every video that
shows code will have its code here in full, in the exact form that video shows it:
clone the repo, `cd` into the video's folder, and run it.

Watch the videos on Clyep: [A2A Explained](https://clyep.io/series/a2a-explained/).

The series follows one running example, **the analyst**: a stock brief agent served
over the Agent2Agent protocol with the Python `a2a-sdk`. Ask it about a ticker over
a period and it fetches the price history, decides what is worth saying, and returns
a short brief as an artifact. Asked without a period, it asks back. The videos also
talk to an agent we did not write, the A2A project's currency-conversion sample,
run locally.

## Status

The implementation trial is done and the first video folders exist. Video folders
are carved out of `trial/` as each video is authored.

| Folder | What it holds |
|---|---|
| [`04-first-agent/`](./04-first-agent/) | Video 04: `ask.py`, our 36-line client, talking to the A2A project's currency-conversion sample, run locally as a black box |
| [`05-analyst/`](./05-analyst/) | Video 05: the analyst at its minimum, served behind its card (`server.py`, 54 lines, over `analyst.py`), and the same `ask.py` |
| [`06-task-life/`](./06-task-life/) | Video 06: the same served analyst, with the two clients that watch a task while it runs (`poll.py`, 38 lines, and `stream.py`, 34) |
| [`trial/`](./trial/) | The analyst (`analyst.py`, `server.py`), one client script per video moment (`ask.py`, `poll.py`, `stream.py`, `chat.py`, `reconnect.py`, `webhook.py`, `wire.py`), the currency agent ported to the pinned SDK, and `captures/` with every run and its provenance |

The convention is MCP Explained's: one runnable folder per video state, named for
the video, two videos sharing a folder only where the code between them is
identical. `trial/` stays as it is until each remaining video takes its folder.

## Setup pattern (all folders)

Every folder reads its configuration from a local `.env` file (never committed).
Copy the folder's `.env.example` to `.env`, fill in your key, then:

```bash
cd <folder>
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

The model is any OpenAI-compatible endpoint (`LLM_BASE_URL`, `LLM_MODEL`,
`LLM_API_KEY`); the examples default to OpenRouter. Dependencies are pinned
exactly, because the repo promises the environment each video was captured in.
The A2A SDK is `a2a-sdk` 1.1.5, which implements spec v1.0.

## Try the analyst

```bash
cd trial
python server.py                                   # terminal 1: the analyst, on port 9999
python ask.py http://127.0.0.1:9999 "How did Apple do over the last month?"   # terminal 2
python stream.py "How did Apple do over the last month, and was that just the market?"
python chat.py http://127.0.0.1:9999 "How did Apple do?" "the last month"
```

The first prints the card, the task and its brief. The second streams the task's
life, including the analyst deciding to fetch a market benchmark. The third stops
in `input-required`, answers the question, and completes the same task.

# What Goes Over the Wire

Companion code for the "What Goes Over the Wire" video of A2A Explained: video 06's
analyst and video 06's two clients, with a wiretap between them, so the bytes the
video reads are the bytes of the agent the viewer has already watched.

`analyst.py` (56 lines), `poll.py` (38 lines) and `stream.py` (34 lines) are
byte-identical to `06-task-life/`. `server.py` (58 lines) is 06's file plus one
thing: an optional port on the command line, because the tap needs the analyst
somewhere other than 9999. The card is untouched — it still advertises
`http://127.0.0.1:9999`, one skill, and `streaming` as its only capability, which
is what this video puts on screen first.

`tap.py` (53 lines) is carried from the implementation trial as it is. It starts
`server.py` on a hidden port (9997), listens on 9999 itself, and passes every byte
through in both directions untouched, copying each one into `wire.log`. It
pretty-prints JSON where it finds it — a request body, the payload of an SSE
`data:` line — and writes everything else (request lines, headers, chunk sizes,
blank lines) exactly as it crossed. Neither client knows it is there: they talk to
9999 as they always have.

`wire.log` (1174 lines) is the committed record of one sitting, captured 2026-10-03.
It is read on screen, so it belongs to this folder rather than to a gitignored
corner. The provenance is next door, in
`../a2a-explained/videos/08-the-wire/assets/captures/README.md`.

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                 # fill in LLM_API_KEY
python tap.py                        # terminal 1: analyst on 9997, tap on 9999
```

```bash
# terminal 2: the same question both ways, the plain one this time
python poll.py   "How did Apple do over the last month?"
python stream.py "How did Apple do over the last month?"
```

`wire.log` is rewritten each time the tap starts. The committed one holds, in order:
the card fetch and the card as served, `SendMessage` answered with a task that has a
state and no answer in it, thirteen `GetTask` round trips, then a second card fetch
and `SendStreamingMessage` answered as one chunked `text/event-stream` carrying five
events.

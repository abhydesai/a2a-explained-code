# When the Agent Asks Back

Companion code for the "When the Agent Asks Back" video of A2A Explained: the same
analyst as video 06, now able to stop a task and ask for what it is missing, and a
client that answers on the same task.

`analyst.py` (56 lines) is byte-identical to `06-task-life/`: nothing about the
model or the lookup changes. `ask.py` is the client from video 04, also unchanged.

`server.py` (74 lines) is 06's file plus twenty lines. A brief needs a period, so
`PERIOD` names the wordings a request can carry ("last month", "3 weeks", "year to
date", ...). On each message the executor takes the task the context already
holds, or opens one if this is the first message; gathers every user turn on the
task, this one included, into `asked`; and checks `asked` against `PERIOD` before
any model call. No period: the task goes to `input-required` carrying the
analyst's question, and the executor returns. A period: the task works as it did
in 06, and the whole conversation so far is what the analyst writes from.

`chat.py` (43 lines) sends a question with the plain call, prints the state and
the agent's question if there is one, then sends the reply as a second message on
the same task and context ids and prints what comes back. The reply is the
second command-line argument rather than an interactive prompt, so the run can be
captured.

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                 # fill in LLM_API_KEY
python server.py                     # terminal 1: the analyst, on port 9999
```

```bash
# terminal 2: a question with no period, and the answer to the question back
python chat.py "How did Apple do?" "the last month"
```

The first response comes back `input_required` at once, with "Which period should
the brief cover? For example: the last month." The reply completes the same task,
and the brief covers Apple over the last month: the ticker came from the first
turn, the period from the second.

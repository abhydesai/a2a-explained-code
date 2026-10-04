# One Agent, Many Agents

Companion code for the "One Agent, Many Agents" video of A2A Explained: a briefing
agent with two agents on its list, and one question that needs both.

`briefing.py` is the whole briefing agent, 67 lines. It reads the card of every
agent on its `CARDS` list and makes one client for each, the way `ask.py` does.
It also gives each card to its own model as a tool: the tool's name comes from the
card's name, its description is the card's description and skills, and its one
parameter is the message to send. When the model calls one, the briefing agent
sends that message to the agent, and hands the model back the text of the task's
artifact (or, if the task stopped, the agent's question). The loop around that is
the analyst's own tool loop, unchanged. The briefing agent serves no card: it is a
client of both agents, with a model of its own to decide who gets which part.

Neither agent on the list is in this folder, because neither changes: the analyst
runs from `../09-mcp-bridge/` (its lookup behind an MCP server, as video 09 left
it) and the currency agent from `../04-first-agent/currency-agent/` (the A2A
project's sample, as video 04 met it).

## Run

Each folder has its own venv and `.env` (see each folder's README):

```bash
cd ../09-mcp-bridge && source .venv/bin/activate && python server.py        # terminal 1, port 9999
cd ../04-first-agent/currency-agent && source .venv/bin/activate && python -m app   # terminal 2, port 10000
```

Then, from this folder:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                 # fill in LLM_API_KEY
python briefing.py "Summarize Apple's performance over the last month, and express the price change in euros."
```

It prints both cards, then each hand-off as it goes out (`->`, the message the model
wrote) and comes back (`<-`, the task's state and its result), then the briefing.

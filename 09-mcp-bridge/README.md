# Where A2A Meets MCP

Companion code for the "Where A2A Meets MCP" video of A2A Explained: video 06's
analyst with its price lookup moved behind an MCP server, and nothing on the A2A
side changed. Same card, same clients, same task contract — the swap happens
inside the agent's wall.

`analyst.py` (56 lines), `ask.py` (36 lines) and `stream.py` (34 lines) are
byte-identical to `06-task-life/`. `server.py` (58 lines) is 06's file plus one
thing: it imports the analyst by name instead of by `import`, so `ANALYST` on the
command line chooses which analyst runs. `CARD` is untouched — one skill,
`http://127.0.0.1:9999`, and `streaming` as its only capability, which is the
same card video 05 captured, byte for byte. That is the video's proof: the served
side the viewer has been watching since 05 does not know its lookup moved.

```python
# The analyst is analyst.py, or the one named in ANALYST (analyst_mcp,
# the same analyst with its lookup behind an MCP server).
write_brief = import_module(os.environ.get("ANALYST", "analyst")).write_brief
```

`mcp_server.py` (26 lines) is the stock server of MCP Explained in its own
pattern — same import, `MCPServer("stocks")`, one `@mcp.tool()`, `mcp.run()` —
with `price_history(ticker, period)` as the one function, the analyst's lookup
exactly as `analyst.py` had it.

`analyst_mcp.py` (41 lines) is `analyst.py` with that lookup discovered instead
of written. Out came the local `price_history` and the hand-written `TOOLS`; in
went `StdioServerParameters`, `list_tools` to ask the server what it offers, and
`call_tool` to run it. The one thing the analyst still adds is `reason`: it
appends that property to the schema the server describes, so each lookup still
says why it was made. Nothing else in the loop changed.

The MCP server is never started by hand. `analyst_mcp.py` starts it as a stdio
subprocess (`StdioServerParameters(command="python", args=["mcp_server.py"])`),
so the only command on screen is the A2A server.

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                 # fill in LLM_API_KEY
ANALYST=analyst_mcp python server.py # terminal 1: the lookup now comes over stdio
```

```bash
# terminal 2: the same card, the same clients as 06
curl -s http://127.0.0.1:9999/.well-known/agent-card.json
python ask.py http://127.0.0.1:9999 "How did Apple do over the last month?"
python stream.py "How did Apple do over the last month, and was that just the market?"
```

`python server.py` with no `ANALYST` runs the direct-lookup analyst of 05–08, for
the before-and-after the video shows. The two runs are two tasks with two ids;
nothing about them is the same task.

The captures of this folder's sitting, with their provenance, are next door in
`../a2a-explained/videos/09-mcp-bridge/assets/captures/`.

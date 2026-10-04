# Where A2A Meets MCP

Companion code for the "Where A2A Meets MCP" video of A2A Explained: video 06's
analyst with its price lookup moved behind an MCP server, and nothing on the A2A
side changed. Same card, same clients, same task contract — the swap happens
inside the agent's wall.

`analyst.py` (56 lines), `ask.py` (36 lines) and `stream.py` (34 lines) are
byte-identical to `06-task-life/`. `server.py` (54 lines) differs from 06's file
by one word:

```python
from analyst_mcp import write_brief     # 06 said: from analyst import write_brief
```

That is the whole change on the served side. `CARD` is untouched — one skill,
`http://127.0.0.1:9999`, and `streaming` as its only capability, which is the
same card video 05 captured, byte for byte. The agent the viewer has been
watching since 05 does not know its lookup moved.

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

`analyst.py` stays in the folder because the video reads it as the before, next to
`analyst_mcp.py`. Nothing imports it any more.

The MCP server is never started by hand. `analyst_mcp.py` starts it as a stdio
subprocess (`StdioServerParameters(command="python", args=["mcp_server.py"])`),
so the only command on screen is the A2A server.

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                 # fill in LLM_API_KEY
python server.py                     # terminal 1: the lookup now comes over stdio
```

```bash
# terminal 2: the same card, the same clients as 06
curl -s http://127.0.0.1:9999/.well-known/agent-card.json
python ask.py http://127.0.0.1:9999 "How did Apple do over the last month?"
python stream.py "How did Apple do over the last month, and was that just the market?"
```

The captures of this folder's sitting, with their provenance, are next door in
`../a2a-explained/videos/09-mcp-bridge/assets/captures/`.

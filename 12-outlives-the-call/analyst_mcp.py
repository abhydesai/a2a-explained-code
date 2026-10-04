"""The analyst with its lookup behind MCP: same model, same brief; the tool comes from a server."""
import json, os
from datetime import date
from mcp import Client, StdioServerParameters
from openai import AsyncOpenAI

SERVER = StdioServerParameters(command="python", args=["mcp_server.py"])
SYSTEM = (f"Today is {date.today():%A, %B %d, %Y}. You write short stock briefs. "
          "Fetch the price history you need. Fetch a second ticker (an index fund "
          "or a peer) only when the comparison earns a sentence. Then write three "
          "to five plain-text sentences on what the price did and what stands out. "
          "Describe; never advise.")
REASON = {"type": "string", "description": "Why this lookup, in a few words."}


async def write_brief(question, note):
    """Run the model until it answers; report each lookup it decides on via note()."""
    llm = AsyncOpenAI(base_url=os.environ["LLM_BASE_URL"], api_key=os.environ["LLM_API_KEY"])
    async with Client(SERVER) as client:
        tools = []
        for t in (await client.list_tools()).tools:      # the lookup, as the server describes it
            t.input_schema["properties"]["reason"] = REASON
            t.input_schema["required"].append("reason")
            tools.append({"type": "function", "function": {
                "name": t.name, "description": t.description, "parameters": t.input_schema}})

        messages = [{"role": "system", "content": SYSTEM},
                    {"role": "user", "content": question}]
        while True:
            resp = await llm.chat.completions.create(
                model=os.environ["LLM_MODEL"], messages=messages, tools=tools)
            msg = resp.choices[0].message
            messages.append(msg.model_dump(exclude_none=True))
            if not msg.tool_calls:
                return msg.content
            for call in msg.tool_calls:
                args = json.loads(call.function.arguments)
                await note(f"fetching {args['ticker']} over {args['period']}: {args.pop('reason')}")
                result = await client.call_tool(call.function.name, args)
                messages.append({"role": "tool", "tool_call_id": call.id,
                                 "content": result.content[0].text})

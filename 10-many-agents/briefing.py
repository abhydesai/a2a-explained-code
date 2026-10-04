"""A briefing agent: read the cards on its list, hand each agent its part, write the briefing.

    python briefing.py "<a question that needs more than one of the agents>"
"""
import asyncio, json, os, re, sys
import httpx
from dotenv import load_dotenv
from openai import AsyncOpenAI
from a2a.client import A2ACardResolver, ClientConfig, ClientFactory
from a2a.helpers import get_artifact_text, get_message_text, new_text_message
from a2a.types import Role, SendMessageRequest, TaskState

CARDS = ["http://127.0.0.1:9999", "http://localhost:10000"]
SYSTEM = ("You assemble short briefings. Other agents do the work: delegate each part of "
          "the question to the agent whose card fits, in plain words, then write the "
          "briefing from what they return. When a conversion is involved, say which "
          "exchange-rate date it used. Plain text, a short paragraph.")


def state(task):
    return TaskState.Name(task.status.state).removeprefix("TASK_STATE_").lower()


async def main(question):
    load_dotenv()
    llm = AsyncOpenAI(base_url=os.environ["LLM_BASE_URL"], api_key=os.environ["LLM_API_KEY"])
    async with httpx.AsyncClient(timeout=120) as http:
        factory = ClientFactory(ClientConfig(httpx_client=http, streaming=False))

        # One client per card; the model gets each card as a tool it can call.
        agents, tools = {}, []
        for url in CARDS:
            card = await A2ACardResolver(http, url).get_agent_card()
            print(f"agent: {card.name} -- {card.description}")
            name = re.sub(r"\W+", "_", card.name.lower())
            agents[name] = factory.create(card)
            skills = "; ".join(f"{s.name}: {s.description}" for s in card.skills)
            tools.append({"type": "function", "function": {
                "name": name, "description": f"{card.description} Skills: {skills}",
                "parameters": {"type": "object", "required": ["message"],
                               "properties": {"message": {"type": "string"}}}}})

        # Hand out work until the model stops delegating and writes the briefing.
        messages = [{"role": "system", "content": SYSTEM},
                    {"role": "user", "content": question}]
        while True:
            resp = await llm.chat.completions.create(
                model=os.environ["LLM_MODEL"], messages=messages, tools=tools)
            msg = resp.choices[0].message
            messages.append(msg.model_dump(exclude_none=True))
            if not msg.tool_calls:
                return print(f"\nbriefing:\n{msg.content}")
            for call in msg.tool_calls:
                text = json.loads(call.function.arguments)["message"]
                print(f"-> {call.function.name}: {text}")
                request = SendMessageRequest(message=new_text_message(text, role=Role.ROLE_USER))
                async for response in agents[call.function.name].send_message(request):
                    task = response.task
                if task.status.state == TaskState.TASK_STATE_COMPLETED:
                    result = "\n".join(get_artifact_text(a) for a in task.artifacts)
                else:
                    result = f"the agent asks: {get_message_text(task.status.message)}"
                print(f"<- {call.function.name} ({state(task)}): {result}")
                messages.append({"role": "tool", "tool_call_id": call.id, "content": result})


asyncio.run(main(sys.argv[1]))

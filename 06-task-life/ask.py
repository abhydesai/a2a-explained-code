"""Ask an A2A agent for one thing: read its card, send a message, print what comes back.

    python ask.py http://127.0.0.1:9999 "How did Apple do over the last month?"
"""
import asyncio, sys
import httpx
from a2a.client import A2ACardResolver, ClientConfig, ClientFactory
from a2a.helpers import get_artifact_text, get_message_text, new_text_message
from a2a.types import Role, SendMessageRequest, TaskState


def state(task):
    return TaskState.Name(task.status.state).removeprefix("TASK_STATE_").lower()


async def main(url, text):
    async with httpx.AsyncClient(timeout=120) as http:
        card = await A2ACardResolver(http, url).get_agent_card()
        print(f"agent: {card.name} -- {card.description}")
        for skill in card.skills:
            print(f"  skill {skill.id}: {skill.description}")

        client = ClientFactory(ClientConfig(httpx_client=http, streaming=False)).create(card)
        request = SendMessageRequest(message=new_text_message(text, role=Role.ROLE_USER))
        async for response in client.send_message(request):
            if response.HasField("message"):               # a direct reply, no task
                return print(f"message: {get_message_text(response.message)}")
            task = response.task
            print(f"task {task.id}: {state(task)}")
            if task.status.HasField("message"):
                print(f"  agent says: {get_message_text(task.status.message)}")
            for artifact in task.artifacts:
                print(f"  artifact {artifact.name}:\n{get_artifact_text(artifact)}")


asyncio.run(main(sys.argv[1], sys.argv[2]))

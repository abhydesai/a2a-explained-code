"""Send with the streaming call and print each event as it arrives.

    python stream.py "How did Apple do over the last month, and was that just the market?"
"""
import asyncio, sys
import httpx
from a2a.client import ClientConfig, create_client
from a2a.helpers import get_artifact_text, get_message_text, new_text_message
from a2a.types import Role, SendMessageRequest, TaskState

URL = "http://127.0.0.1:9999"


def name(state):
    return TaskState.Name(state).removeprefix("TASK_STATE_").lower()


async def main(text):
    http = httpx.AsyncClient(timeout=120)              # events can be seconds apart
    client = await create_client(URL, ClientConfig(httpx_client=http))
    request = SendMessageRequest(message=new_text_message(text, role=Role.ROLE_USER))
    async for event in client.send_message(request):
        if event.HasField("task"):
            print(f"task {event.task.id}: {name(event.task.status.state)}")
        elif event.HasField("status_update"):
            status = event.status_update.status
            note = get_message_text(status.message) if status.HasField("message") else ""
            print(f"status: {name(status.state)}  {note}")
        elif event.HasField("artifact_update"):
            artifact = event.artifact_update.artifact
            print(f"artifact {artifact.name}:\n{get_artifact_text(artifact)}")


asyncio.run(main(sys.argv[1]))

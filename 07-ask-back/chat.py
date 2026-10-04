"""Ask without a period, get asked back, answer on the same task.

    python chat.py "How did Apple do?" "the last month"
"""
import asyncio, sys
import httpx
from a2a.client import ClientConfig, create_client
from a2a.helpers import get_artifact_text, get_message_text, new_text_message
from a2a.types import Role, SendMessageRequest, TaskState

URL = "http://127.0.0.1:9999"


def state(task):
    return TaskState.Name(task.status.state).removeprefix("TASK_STATE_").lower()


async def send(client, text, task=None):
    message = new_text_message(text, role=Role.ROLE_USER,
                               task_id=task and task.id,
                               context_id=task and task.context_id)
    request = SendMessageRequest(message=message)
    async for response in client.send_message(request):
        task = response.task
    print(f"task {task.id} (context {task.context_id}): {state(task)}")
    if task.status.HasField("message"):
        print(f"  agent asks: {get_message_text(task.status.message)}")
    for artifact in task.artifacts:
        print(f"  artifact {artifact.name}:\n{get_artifact_text(artifact)}")
    return task


async def main(question, reply):
    http = httpx.AsyncClient(timeout=120)     # the plain send waits for the brief
    client = await create_client(URL, ClientConfig(httpx_client=http,
                                                   streaming=False))
    task = await send(client, question)
    if task.status.state == TaskState.TASK_STATE_INPUT_REQUIRED:
        print(f"> {reply}")                   # the second argument is the answer
        await send(client, reply, task)


asyncio.run(main(sys.argv[1], sys.argv[2]))

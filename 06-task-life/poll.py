"""Send, get the task back at once, then ask for it again until it is done.

    python poll.py "How did Apple do over the last month, and was that just the market?"
"""
import asyncio, sys
from a2a.client import ClientConfig, create_client
from a2a.helpers import get_artifact_text, new_text_message
from a2a.types import GetTaskRequest, Role, SendMessageRequest, TaskState

URL = "http://127.0.0.1:9999"
DONE = {TaskState.TASK_STATE_COMPLETED, TaskState.TASK_STATE_FAILED,
        TaskState.TASK_STATE_CANCELED, TaskState.TASK_STATE_REJECTED,
        TaskState.TASK_STATE_INPUT_REQUIRED}


def state(task):
    return TaskState.Name(task.status.state).removeprefix("TASK_STATE_").lower()


async def main(text):
    client = await create_client(URL, ClientConfig(streaming=False, polling=True))
    request = SendMessageRequest(message=new_text_message(text, role=Role.ROLE_USER))
    async for response in client.send_message(request):
        task = response.task
    print(f"task {task.id}: {state(task)}")

    seen = state(task)
    while task.status.state not in DONE:
        await asyncio.sleep(1)
        task = await client.get_task(GetTaskRequest(id=task.id))
        if state(task) != seen:
            seen = state(task)
            print(f"task {task.id}: {seen}")
    for artifact in task.artifacts:
        print(f"  artifact {artifact.name}:\n{get_artifact_text(artifact)}")


asyncio.run(main(sys.argv[1]))

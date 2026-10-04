"""Hang up while the analyst works, then come back for the brief.

    python reconnect.py "How did Apple do over the last month?" 3
    python reconnect.py "How did Apple do over the last month?" 40

The number is how many seconds the client stays away.
"""
import asyncio, sys
import httpx
from a2a.client import ClientConfig, create_client
from a2a.helpers import get_artifact_text, get_message_text, new_text_message
from a2a.types import (GetTaskRequest, Role, SendMessageRequest,
                       SubscribeToTaskRequest, TaskState)

URL = "http://127.0.0.1:9999"
ACTIVE = {TaskState.TASK_STATE_SUBMITTED, TaskState.TASK_STATE_WORKING}


def name(state):
    return TaskState.Name(state).removeprefix("TASK_STATE_").lower()


def show(event):                                        # as stream.py prints
    if event.HasField("task"):
        print(f"task {event.task.id}: {name(event.task.status.state)}")
    elif event.HasField("status_update"):
        status = event.status_update.status
        note = get_message_text(status.message) if status.HasField("message") else ""
        print(f"status: {name(status.state)}  {note}")
    elif event.HasField("artifact_update"):
        artifact = event.artifact_update.artifact
        print(f"artifact {artifact.name}:\n{get_artifact_text(artifact)}")


async def connect():
    http = httpx.AsyncClient(timeout=120)              # events can be seconds apart
    return await create_client(URL, ClientConfig(httpx_client=http))


async def main(text, away):
    client = await connect()
    request = SendMessageRequest(message=new_text_message(text, role=Role.ROLE_USER))
    async for event in client.send_message(request):
        if event.HasField("status_update"):            # the analyst is working
            task_id = event.status_update.task_id
            break
    await client.close()
    print(f"task {task_id}: working, hung up for {away}s")
    await asyncio.sleep(away)

    client = await connect()                            # a new connection
    task = await client.get_task(GetTaskRequest(id=task_id))
    print(f"back, GetTask says: {name(task.status.state)}")
    if task.status.state in ACTIVE:
        async for event in client.subscribe(SubscribeToTaskRequest(id=task_id)):
            show(event)
    else:                                               # finished: the brief is in it
        for artifact in task.artifacts:
            print(f"artifact {artifact.name}:\n{get_artifact_text(artifact)}")


asyncio.run(main(sys.argv[1], int(sys.argv[2])))

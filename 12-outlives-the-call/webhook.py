"""Give the analyst a webhook with the question, hang up, and be told at the webhook.

    python webhook.py "How did Apple do over the last month?"

The client serves its own webhook on port 9998, so this is two programs in one file.
"""
import asyncio, sys
import uvicorn
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.routing import Route
from a2a.client import ClientConfig, create_client
from a2a.helpers import new_text_message
from a2a.types import Role, SendMessageRequest, TaskPushNotificationConfig

URL = "http://127.0.0.1:9999"
HOOK = "http://127.0.0.1:9998/hook"
done = asyncio.Event()


async def hook(request):                                # the analyst calls this
    event = await request.json()
    kind = next(iter(event))
    print(f"webhook got {kind}  (token {request.headers['x-a2a-notification-token']})")
    if kind == "statusUpdate":
        state = event[kind]["status"]["state"]
        print(f"  state {state}")
        if state == "TASK_STATE_COMPLETED":
            done.set()
    elif kind == "artifactUpdate":
        artifact = event[kind]["artifact"]
        print(f"  artifact {artifact['name']}:\n{artifact['parts'][0]['text']}")
    return Response()


async def main(text):
    app = Starlette(routes=[Route("/hook", hook, methods=["POST"])])
    webhook = uvicorn.Server(uvicorn.Config(app, port=9998, log_level="warning"))
    serving = asyncio.create_task(webhook.serve())

    hookup = TaskPushNotificationConfig(url=HOOK, token="s3cret")
    client = await create_client(URL, ClientConfig(streaming=False, polling=True,
                                                   push_notification_config=hookup))
    request = SendMessageRequest(message=new_text_message(text, role=Role.ROLE_USER))
    async for response in client.send_message(request):
        task = response.task
    await client.close()
    print(f"task {task.id}: sent with the webhook, hung up")
    await done.wait()
    webhook.should_exit = True
    await serving


asyncio.run(main(sys.argv[1]))

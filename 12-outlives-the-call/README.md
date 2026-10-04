# A Task That Outlives the Call

Companion code for the "A Task That Outlives the Call" video of A2A Explained, the
series finale: the caller hangs up while the analyst is still working, and the brief
still reaches it, either because it comes back for it or because the analyst calls
it.

`analyst_mcp.py` (41 lines) and `mcp_server.py` (26 lines) are byte-identical to
`09-mcp-bridge/`. `server.py` (58 lines) is 09's file with push notifications
switched on, and nothing else changed:

- the card's capabilities say `push_notifications=True` beside `streaming=True`;
- the request handler gets a place to keep the webhooks clients give it
  (`InMemoryPushNotificationConfigStore`) and a sender that POSTs each of a task's
  updates to them (`BasePushNotificationSender`, with an `httpx` client of its own).

`reconnect.py` (62 lines) is the client that comes back. It sends with the streaming
call, hangs up as soon as the task is `working`, waits, and connects again. Then it
asks for the task first (`GetTask`), because it cannot know whether the task is still
going: if it is, it subscribes (`SubscribeToTask`), which replays the task's current
state and then streams what follows, printed the way `06-task-life/stream.py` prints;
if it has finished, the brief is already in the task. The fetch has to come first:
the protocol and the SDK both refuse a subscription to a task that has ended.

`webhook.py` (54 lines) is the client that is told. It serves a webhook of its own on
port 9998, sends the question with that address and a token, and hangs up; the
analyst POSTs every update to the webhook with the token in the
`X-A2A-Notification-Token` header. It is two programs in one file, so the video shows
its run, not its code.

Both tasks live in the server's `InMemoryTaskStore`: they outlive the client's
connection, not a restart of the server. Keeping tasks across restarts is a durable
store, ordinary service work this folder does not do.

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                 # fill in LLM_API_KEY
python server.py                     # terminal 1
```

```bash
# terminal 2
python reconnect.py "How did Apple do over the last month?" 3    # back while it works
python reconnect.py "How did Apple do over the last month?" 40   # back after it finished
python webhook.py "How did Apple do over the last month?"
```

The captures of this folder's sitting, with their provenance, are next door in
`../a2a-explained/videos/12-outlives-the-call/assets/captures/`.

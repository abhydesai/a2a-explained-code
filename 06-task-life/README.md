# A Task Is Not a Return Value

Companion code for the "A Task Is Not a Return Value" video of A2A Explained: the
same analyst as video 05, asked a question that takes it longer and makes its
choices visible, and two clients that watch the task while it runs.

`analyst.py` (56 lines) and `server.py` (54 lines) are byte-identical to
`05-analyst/`: nothing on the served side changes for this video. `ask.py` is the
client from video 04, also unchanged.

What is new are two clients, one per way of following a task:

`poll.py` (38 lines) sends with the plain call configured to come back as soon as
the task exists, prints the state it got, then asks for the task again once a
second until it reaches a state it cannot leave. The states are visible; the
analyst's reasons are not, because a status it already reported as `working` reads
the same the next time you ask.

`stream.py` (34 lines) sends with the streaming call and prints each event as it
arrives: the task, each working status with the analyst's note, the artifact, and
the completed status. Its own `httpx` client carries a longer timeout, because the
SDK's default gives up after five seconds of silence and the analyst takes about
twelve seconds to write.

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                 # fill in LLM_API_KEY
python server.py                     # terminal 1: the analyst, on port 9999
```

```bash
# terminal 2, the same question both ways
python poll.py   "How did Apple do over the last month, and was that just the market?"
python stream.py "How did Apple do over the last month, and was that just the market?"
```

The second clause is what makes the analyst's judgement visible: it fetches Apple,
then decides the comparison earns a benchmark, fetches SPY, and says why in each
case. The brief answers both halves of the question.

A third way to learn that a task finished — a push notification to a webhook you
registered — is named in the video and built in the last one.

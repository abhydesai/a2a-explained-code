"""A wiretap for the wire between a client and the analyst.

The client normally talks to the analyst at port 9999. Run the tap instead: it
starts the real analyst on a hidden port, takes 9999 itself, passes every byte
through untouched, and copies both directions into wire.log -- JSON bodies
unfolded so a frame reads as JSON, everything else (headers, chunk sizes, SSE
lines) as it crossed.

    python tap.py                # then run any client against http://127.0.0.1:9999
"""
import asyncio, json, subprocess, sys

HIDDEN = 9997
analyst = subprocess.Popen([sys.executable, "server.py", str(HIDDEN)])
log = open("wire.log", "w")


def unfold(chunk):
    """Pretty-print JSON where it appears: a request body, or the payload of an SSE line."""
    head, sep, body = chunk.partition("\r\n\r\n")
    lines = []
    for line in (head + sep + body).splitlines() if sep else chunk.splitlines():
        label, _, payload = line.partition("data: ")
        try:
            body = json.dumps(json.loads(payload or line), indent=2)
            lines.append(label + "data: " + body if payload else body)
        except ValueError:
            lines.append(line)
    return "\n".join(lines)


async def relay(source, sink, arrow):
    while chunk := await source.read(65536):
        sink.write(chunk)
        await sink.drain()
        print(arrow, unfold(chunk.decode(errors="replace")), sep="\n", end="\n\n", file=log, flush=True)
    sink.close()


async def handle(client_reader, client_writer):
    agent_reader, agent_writer = await asyncio.open_connection("127.0.0.1", HIDDEN)
    await asyncio.gather(relay(client_reader, agent_writer, "--> to agent"),
                         relay(agent_reader, client_writer, "<-- from agent"))


async def main():
    await asyncio.sleep(2)                                 # let the analyst come up
    server = await asyncio.start_server(handle, "127.0.0.1", 9999)
    async with server:
        await server.serve_forever()


asyncio.run(main())

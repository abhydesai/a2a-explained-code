"""Serve the analyst over A2A: a card at its address, a task per message."""
import re
import uvicorn
from dotenv import load_dotenv
from starlette.applications import Starlette
from a2a.helpers import (get_message_text, new_task_from_user_message,
                         new_text_part)
from a2a.server.agent_execution import AgentExecutor
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.types import (AgentCapabilities, AgentCard, AgentInterface,
                       AgentSkill, Role, TaskState)
from analyst import write_brief

CARD = AgentCard(
    name="Stock Analyst",
    description="Writes a short brief on one stock over one period, "
                "from its price history.",
    version="0.1.0",
    default_input_modes=["text/plain"], default_output_modes=["text/plain"],
    capabilities=AgentCapabilities(streaming=True),
    supported_interfaces=[AgentInterface(
        url="http://127.0.0.1:9999", protocol_binding="JSONRPC",
        protocol_version="1.0")],
    skills=[AgentSkill(
        id="stock-brief", name="Stock brief", tags=["stocks"],
        description="Given a ticker and a period, fetch the price history "
                    "and write a few sentences on what happened.",
        examples=["How did Apple do over the last month?"])],
)
# The wordings a brief can be asked for; anything else needs a question back.
PERIOD = re.compile(
    r"\b(\d+ ?(day|week|month|year)s?"
    r"|(last|past) (\w+ )?(week|month|quarter|year)s?"
    r"|year to date|ytd)\b", re.I)


class Analyst(AgentExecutor):
    async def execute(self, context, queue):
        task = context.current_task
        if task is None:                      # first message: open a task
            task = new_task_from_user_message(context.message)
            await queue.enqueue_event(task)
        updater = TaskUpdater(queue, task.id, task.context_id)
        turns = {m.message_id: get_message_text(m)
                 for m in task.history if m.role == Role.ROLE_USER}
        turns[context.message.message_id] = context.get_user_input()
        asked = "\n".join(turns.values())     # every turn, this one included

        if not PERIOD.search(asked):          # before any model call
            await updater.requires_input(updater.new_agent_message(
                [new_text_part("Which period should the brief cover? "
                               "For example: the last month.")]))
            return

        await updater.start_work()
        async def note(text):
            message = updater.new_agent_message([new_text_part(text)])
            await updater.update_status(TaskState.TASK_STATE_WORKING, message)
        brief = await write_brief(asked, note)
        await updater.add_artifact([new_text_part(brief)], name="brief")
        await updater.complete()

    async def cancel(self, context, queue):
        raise NotImplementedError


load_dotenv()
handler = DefaultRequestHandler(
    agent_executor=Analyst(), task_store=InMemoryTaskStore(), agent_card=CARD)
app = Starlette(routes=create_agent_card_routes(CARD)
                + create_jsonrpc_routes(handler, "/"))
uvicorn.run(app, host="127.0.0.1", port=9999)

"""The analyst: a model that fetches what it needs, then writes a short brief."""
import asyncio, json, os
from datetime import date
import yfinance as yf
from openai import AsyncOpenAI

SYSTEM = (f"Today is {date.today():%A, %B %d, %Y}. You write short stock briefs. "
          "Fetch the price history you need. Fetch a second ticker (an index fund "
          "or a peer) only when the comparison earns a sentence. Then write three "
          "to five plain-text sentences on what the price did and what stands out. "
          "Describe; never advise.")


def price_history(ticker: str, period: str) -> str:
    """Daily closes for a ticker over a period: 5d, 1mo, 3mo, 6mo, 1y or ytd."""
    stock = yf.Ticker(ticker)
    closes = stock.history(period=period)["Close"].dropna()   # today has no close yet
    if closes.empty:
        return f"no data for {ticker} over {period}"
    currency = stock.history_metadata.get("currency", "")
    change = (closes.iloc[-1] / closes.iloc[0] - 1) * 100
    sampled = closes.iloc[:: max(1, len(closes) // 8)]
    return (f"{ticker.upper()} {period}, in {currency}: "
            f"start {closes.index[0]:%Y-%m-%d} close {closes.iloc[0]:.2f}, "
            f"end {closes.index[-1]:%Y-%m-%d} close {closes.iloc[-1]:.2f} ({change:+.1f}%); "
            f"high close {closes.max():.2f} on {closes.idxmax():%Y-%m-%d}, "
            f"low close {closes.min():.2f} on {closes.idxmin():%Y-%m-%d}. Some closes along the way: "
            + ", ".join(f"{d:%b %d} {c:.2f}" for d, c in sampled.items()))


TOOLS = [{"type": "function", "function": {
    "name": "price_history", "description": price_history.__doc__,
    "parameters": {"type": "object", "properties": {
        "ticker": {"type": "string"}, "period": {"type": "string"},
        "reason": {"type": "string", "description": "Why this lookup, in a few words."},
    }, "required": ["ticker", "period", "reason"]},
}}]


async def write_brief(question, note):
    """Run the model until it answers; report each lookup it decides on via note()."""
    llm = AsyncOpenAI(base_url=os.environ["LLM_BASE_URL"], api_key=os.environ["LLM_API_KEY"])
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": question}]
    while True:
        resp = await llm.chat.completions.create(
            model=os.environ["LLM_MODEL"], messages=messages, tools=TOOLS)
        msg = resp.choices[0].message
        messages.append(msg.model_dump(exclude_none=True))
        if not msg.tool_calls:
            return msg.content
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments)
            await note(f"fetching {args['ticker']} over {args['period']}: {args.pop('reason')}")
            result = await asyncio.to_thread(price_history, **args)
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

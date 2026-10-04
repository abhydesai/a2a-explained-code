"""An MCP server that gives a model one thing it cannot know: a stock's price history."""
import yfinance as yf
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("stocks")


@mcp.tool()
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


mcp.run()

import json
import logging
import time
from typing import Any

from fastmcp import FastMCP
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.server.middleware.error_handling import RetryMiddleware
from fastmcp.server.middleware.rate_limiting import RateLimitingMiddleware

from mcp_instana import settings

logger = logging.getLogger(__name__)

# Create the MCP server instance
mcp = FastMCP(
    name="Instana MCP Server",
    # Configure behaviors for duplicate names
    on_duplicate_tools="error",
    on_duplicate_resources="error",
    on_duplicate_prompts="error",
)


# Helper to safely stringify arguments without exploding logs
def _safe_dump(obj: Any, max_len: int = 100) -> str:
    try:
        s = json.dumps(obj, default=str)
    except Exception:
        try:
            s = str(obj)
        except Exception:
            s = "<unserializable>"
    if len(s) > max_len:
        return s[:max_len] + "...(truncated)"
    return s


# Logging middleware
class LoggingMiddleware(Middleware):
    """Middleware that logs all MCP operations."""

    async def on_message(self, context: MiddlewareContext, call_next):
        try:
            method = getattr(context, "method", None) or (context.message or {}).get(
                "method"
            )
            source = getattr(context, "source", None)
            msg = getattr(context, "message", None) or {}

            tool_name = None
            tool_args = None

            # If this is a "tools/call", attempt to extract the tool name
            if method == "tools/call":
                tool_name = msg.name
                tool_args = msg.arguments

            # Log beginning
            if tool_name:
                logger.info(
                    f"Invoking tool: {tool_name}, by method {method}) from {source}"
                )
                if tool_args is not None:
                    logger.debug(
                        f"Tool name: '{tool_name}'; args: {_safe_dump(tool_args)}"
                    )
            else:
                logger.info(f"Processing {method} from {source}")

        except Exception as e:
            # Logging should never break the pipeline
            logger.exception(
                "LoggingMiddleware failed to inspect the inbound message: %s", e
            )

        # call the next middleware / handler and measure duration
        start = time.perf_counter()
        try:
            result = await call_next(context)
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000

        # Post-processing logs
        try:
            if tool_name:
                logger.info(f"Completed tool '{tool_name}' in {elapsed_ms:.1f}ms")
            else:
                logger.info(f"Completed {method} in {elapsed_ms:.1f}ms")
        except Exception:
            # swallow any logging errors
            pass

        return result


# Tag-based tool filtering middleware
class TagBasedToolFilterMiddleware(Middleware):
    async def on_list_tools(self, context: MiddlewareContext, call_next):
        """
        Intercept the list_tools response and filter by allowed categories.
        Each tool is expected to have tags among the categories of .
        """
        result = await call_next(context)

        if not settings.global_tool_categories:
            logger.info("List all tools without filtering")
            return result
        else:
            filtered = []
            for tool in result:
                if bool(set(settings.global_tool_categories) & set(tool.tags)):
                    filtered.append(tool)
            logger.info(
                f"List tools filtered by categories: {settings.global_tool_categories}, total {len(filtered)} tools"
            )
            return filtered


def run(mode: str, port: int):
    """Configure and run the MCP server."""

    # Adding logging middleware
    logger.info("Adding LoggingMiddleware")
    mcp.add_middleware(LoggingMiddleware())

    # Adding TagBasedToolFilterMiddleware middleware
    logger.info("Adding TagBasedToolFilterMiddleware")
    mcp.add_middleware(TagBasedToolFilterMiddleware())

    # Adding rate limiting (allows controlled bursts)
    logger.info("Adding RateLimitingMiddleware")
    mcp.add_middleware(
        RateLimitingMiddleware(max_requests_per_second=100.0, burst_capacity=20)
    )

    # Adding automatic retry with exponential backoff
    logger.info("Adding RetryMiddleware")
    mcp.add_middleware(
        RetryMiddleware(max_retries=3, retry_exceptions=(ConnectionError, TimeoutError))
    )

    if mode == "streamable-http":
        logger.info(f"Starting MCP server in streamable-http mode on port {port}")
        mcp.run(transport="http", host="0.0.0.0", port=port)
    else:
        logger.info("Starting MCP server in stdio mode")
        mcp.run()

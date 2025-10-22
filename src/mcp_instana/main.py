"""
Model Context Protocol (MCP) Server for IBM Instana

Supports stdio and Streamable HTTP transports.
"""

import argparse
import logging
import os
import sys

from dotenv import load_dotenv

from mcp_instana import server, settings
from mcp_instana.tools import *  # noqa: F403
from mcp_instana.utils import setup_logging

load_dotenv()

setup_logging()

logger = logging.getLogger("mcp_instana.main")


def validate_credentials() -> bool:
    """Validate that Instana credentials are provided for stdio mode."""
    # For stdio mode, validate INSTANA_API_TOKEN and INSTANA_BASE_URL
    token = os.getenv("INSTANA_API_TOKEN") or ""
    base_url = os.getenv("INSTANA_BASE_URL") or ""
    return not (not token or not base_url)


def main():
    """Main entry point for Instana MCP server."""
    try:
        # Create and configure the MCP server
        parser = argparse.ArgumentParser(
            description="Instana MCP Server", add_help=False
        )
        parser.add_argument(
            "-h",
            "--help",
            action="store_true",
            dest="help",
            help="Show this help message and exit",
        )
        parser.add_argument(
            "--transport",
            type=str,
            choices=["streamable-http", "stdio"],
            metavar="<mode>",
            help="Set the transport mode: streamable-http, stdio. Defaults to stdio if not specified.",
        )
        parser.add_argument(
            "--tools",
            type=str,
            metavar="<categoriy1,category2,...>",
            help="Comma-separated list of tool categories to enable: infra,app,events,automation,website. If not provided, all tools are enabled.",
        )
        parser.add_argument(
            "--port",
            type=int,
            default=int(os.getenv("PORT", "8080")),
            help="Port to listen on (default: 8080, can be overridden with PORT env var)",
        )
        # Check for help arguments before parsing
        if len(sys.argv) > 1 and any(
            arg in ["-h", "--h", "--help", "-help"] for arg in sys.argv[1:]
        ):
            # Check if help is combined with other arguments
            help_args = ["-h", "--h", "--help", "-help"]
            other_args = [arg for arg in sys.argv[1:] if arg not in help_args]

            if other_args:
                logger.error(
                    "Argument -h/--h/--help/-help: not allowed with other arguments"
                )
                sys.exit(2)

            # Show help and exit
            try:
                logger.info("Available options:")
                for action in parser._actions:
                    # Only print options that start with '--' and have a help string
                    if (
                        any(opt.startswith("--") for opt in action.option_strings)
                        and action.help
                    ):
                        # Find the first long option
                        long_opt = next(
                            (
                                opt
                                for opt in action.option_strings
                                if opt.startswith("--")
                            ),
                            None,
                        )
                        metavar = action.metavar or ""
                        opt_str = f"{long_opt} {metavar}".strip()
                        logger.info(f"{opt_str:<24} {action.help}")
                sys.exit(0)
            except Exception as e:
                logger.error(f"Error displaying help: {e}")
                sys.exit(0)  # Still exit with 0 for help

        args = parser.parse_args()

        # Retrieve the tool categories if specified
        settings.global_tool_categories = args.tools.split(",") if args.tools else None
        logger.info(
            f"Enabled tool categories: {settings.global_tool_categories or 'all'}"
        )

        # In stdio mode, the credentials must be provided via environment variables
        settings.global_mcp_mode = args.transport or "stdio"
        if args.transport == "stdio" or args.transport is None:
            if not validate_credentials():
                logger.error(
                    "Error: Instana credentials are required for stdio mode but not provided. Please set INSTANA_API_TOKEN and INSTANA_BASE_URL environment variables."
                )
                sys.exit(1)

        # Start the MCP server
        try:
            server.run(args.transport, args.port)
        except Exception as e:
            logger.error(f"Failed to create MCP server: {e}")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.error("Unhandled exception in main", exc_info=True)
        sys.exit(1)

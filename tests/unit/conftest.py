"""
Shared fixtures for unit tests
"""

from types import SimpleNamespace
from unittest.mock import PropertyMock, patch

import pytest
from fastmcp import Context, FastMCP


@pytest.fixture
def fake_mcp_server():
    fake_mcp_server = FastMCP("Fake MCP Server")
    return fake_mcp_server


@pytest.fixture
def fake_ctx(fake_mcp_server: FastMCP) -> Context:
    ctx = Context(fake_mcp_server)

    # Create a fake request object
    fake_request = SimpleNamespace(
        headers={
            "instana-api-token": "fake-token",
            "instana-base-url": "https://fake.instana-api.com",
        }
    )

    # Create a fake request_context object
    fake_request_context = SimpleNamespace(request=fake_request)

    # Patch the read-only property
    with patch.object(
        type(ctx),
        "request_context",
        new_callable=PropertyMock(return_value=fake_request_context),
    ):
        yield ctx

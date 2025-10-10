"""
Unit tests for demo top performance tools.
"""

from unittest.mock import MagicMock, patch

import pytest
from mcp_instana.tools.trending.top_performance import (
    list_top_applications_by_performance,
)


@patch(
    "instana_client.ApplicationMetricsApi.get_application_data_metrics_v2",
)
@pytest.mark.asyncio
async def test_list_top_applications_by_performance_with_defaults(api, fake_ctx):
    """Test list_top_applications_by_performance with only metric parameter."""

    # Create the mock response of the corresponding APIs' call
    # Note: there might be more than one API call in a tool function
    expected_result = {"metrics": "test_data"}
    mock_response = MagicMock()
    mock_response.to_dict.return_value = expected_result

    # Execute the tool function
    api.return_value = mock_response
    actual_result = await list_top_applications_by_performance.fn(ctx=fake_ctx)

    # Assert the results
    api.assert_called_once()
    assert actual_result == expected_result

"""
Top performance tools for Instana MCP.

This module provides top performance insights for applications, services, endpoints, websites, mobile apps, host.
"""

import inspect
import os
from ast import Dict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import instana_client
from dotenv import load_dotenv
from fastmcp import Context
from fastmcp.exceptions import ToolError
from instana_client.configuration import Configuration
from instana_client.models.get_application_metrics import GetApplicationMetrics
from instana_client.models.metric_api_result import MetricAPIResult
from mcp_instana.server import mcp
from mcp_instana.utils import BaseInstanaClient, instana_api_client_instance

load_dotenv()


@mcp.tool(
    name="list_top_applications_by_performance",
    description="list top n applications measured by specific metric performance: latency, traffic, or error_rate.",
    tags={"trending", "tool"},
)
async def list_top_applications_by_performance(
    metric: str | None = "latency",
    to_time_ms: int | None = None,
    duration_ms: int | None = 60 * 60 * 1000,
    top_n: int | None = 10,
    aggregation: str | None = "MEAN",
    order: str | None = "desc",
    ctx: Context | None = None,
) -> Dict[str, Any] | None:
    """
    List top n applications by performance measured by available golden signals: latency, traffic, and error_rate.

    Args:
        metric (int): The golden signal/metric to measure performance. Options: letency, traffic, error_rate.
        to_time_ms (int): to timestamp in milliseconds, for example: 1618081200000. Defaults to now.
        duration_ms (str): the duration in milliseconds towards to_time, defaults to last 1 hour (3600000 ms).
        top_n (int): The number of top applications to return, defaults to 10.
        aggregation (str): The aggregation method to use. Options include "MEAN", "P95", "P99".
        order (str): The order of the results, either "asc" for ascending or "desc" for descending. Defaults to "desc".
        ctx (Context): The FastMCP context object.
    """
    if to_time_ms is None:
        now = datetime.now(timezone.utc)
        to_time = int(now.timestamp() * 1000)

    with instana_api_client_instance() as api_client_instance:  # pyright: ignore[reportPrivateImportUsage]
        get_application_metrics = {
            "includeInternal": True,
            "includeSynthetic": True,
            "metrics": [{"aggregation": aggregation, "metric": metric}],
            "timeFrame": {"to": to_time, "windowSize": duration_ms},
        }

        try:
            # Get Application Data Metrics
            result = api_client_instance.get_application_data_metrics_v2(
                get_application_metrics=get_application_metrics  # pyright: ignore[reportArgumentType]
            )

            return result.to_dict()

        except Exception as e:
            await ctx.error(
                f"Error calling tool {inspect.currentframe().f_code.co_name}: {e}"
            )
            raise ToolError(
                f"Instana API call [get_application_data_metrics_v2] error: {e}"
            )

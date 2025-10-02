"""
Unit tests for demo tools module.
"""

from mcp_instana.tools.log import demo_tools


def test_add():
    """Test that add returns the right value."""
    # Verify that common Unix utilities are in the allowed list
    assert demo_tools.add.fn(2, 3) == 5

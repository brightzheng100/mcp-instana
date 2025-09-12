from server import mcp


@mcp.tool(
    name="add_two_numbers",
    description="add two numbers and return the value.",
    tags={"infra"}
)
def add(a: float, b: float) -> float:
    """Adds two numbers and return the value."""
    return a + b

@mcp.tool(
    name="subtract_two_numbers",
    description="subtract two numbers and return the value.",
    tags={"app"},
    enabled=False
)
def subtract(a: float, b: float) -> float:
    """Subtract two numbers and return the value."""
    return a - b

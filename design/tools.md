# Tools

Let's be clear: **Tools != Application APIs.**

There are tools, including the component within the FastMCP, [here](https://gofastmcp.com/integrations/openapi), to easily convert OpenAPI-compliant APIs to be MCP tools.

But MCP tools are one-layer higher than just backend RESTful APIs that expose functions as executable capabilities for the MCP client.
MCP tools offer LLM-friendly context so that the LLMs would easily discover, intercept, and orchestrate in a much streamlined and efficient way.

## Key Design Principles

### Use `@tool` decorator

To simplify the way to expose the right functions as MCP tools, using `@tool` decorator is a must.

### Provide proper decorator arguments

There are a few important decorator arguments that we must provide:

- `name` (MUST HAVE): This is what is displayed in the MCP client, so it must be precise and human-friendly name of the tool. Please note that, as of writing, some MCP clients would validate the `name` to comply with `[a-z0-9_-]` so we should specify the name for programmatic or logical use, in snake case format.

- `description` (SHOULD HAVE): A detailed description for the tool.

- `tags` (MUST HAVE): See [Use tags](#use-tags) below.

### Use tags

Tags offer a way to filter and/or organize the tools.

As of now, there are a list of available categories, including "infra", "app", "events", "automation", "website", "log", that should be used to tag the tools.

Along the development, there might be more tags to be added as part of the standardization.

### Control visibility of the tools if needed

There are two layers of control for the tools' visibility:

**1. Starting the MCP server with specific tools' categories, by tags**

For example, when starting the MCP server with `--tools app,infra`, only tools tagged with either `app` or `infra` will be discovered by MCP client.

**2. By explicitly disabling the tools**

With the `@tool` decorator, it's possible to explicitly disable specific tools with `enabled=False`.

By default, all `@tool` decorated functions will become the enabled tools.


## Example

```python
from server import mcp

@mcp.tool(
    name="add_two_numbers",
    description="add two numbers and return the value.",
    tags={"infra", "tool"}
)
def add(a: float, b: float) -> float:
    """Adds two numbers and return the value."""
    return a + b
```


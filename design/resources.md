# Resources & Templates

Resources represent data or files that an MCP client can read to further enrich the prompt context.
And resource templates extend this concept by allowing clients to request dynamically generated resources based on parameters passed in the URI.

When using FastMCP, both static and dynamic resources can be defined by simply using the `@mcp.resource` decorator.

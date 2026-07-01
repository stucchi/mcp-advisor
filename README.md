# MCP Advisor

<!-- mcp-name: io.github.stucchi/mcp-advisor -->

<p align="center">
  <img src="assets/icon.png" alt="MCP Advisor" width="200">
</p>

An MCP server that lets your AI assistant browse, search, and discover MCP servers from the [MCP Advisor](https://stucchi.github.io/mcp-advisor-app/) registry.

The registry data is a static snapshot of the official MCP registry, refreshed
regularly and published to the web. All search and lookup runs locally in the
package — there is no account, no tracking, and no backend to depend on.

## Installation

```bash
# Run directly (recommended)
uvx mcp-advisor

# Or install globally
pip install mcp-advisor
```

## Usage

### With Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcp-advisor": {
      "command": "uvx",
      "args": ["mcp-advisor"]
    }
  }
}
```

### With Cursor

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "mcp-advisor": {
      "command": "uvx",
      "args": ["mcp-advisor"]
    }
  }
}
```

### Standalone

```bash
uvx mcp-advisor                              # stdio transport (default)
uvx mcp-advisor --transport sse              # SSE transport
uvx mcp-advisor --data-url http://localhost:8000   # custom snapshot source (or a local dir)
```

## Tools

| Tool | Description |
|------|-------------|
| `search_servers` | Search MCP servers with filters (query, transport, registry type, tag, sort) |
| `get_server_details` | Get full details about a specific server |
| `get_install_instructions` | Get install config for Claude Desktop, Cursor, opencode, or generic |
| `get_trending_servers` | Get trending servers by GitHub stars and recent activity |
| `get_registry_stats` | Get registry statistics |
| `browse_tags` | List all tags with server counts |

## License

MIT - Luca Stucchi

# MCP Advisor

<!-- mcp-name: io.github.stucchi/mcp-advisor -->

<p align="center">
  <img src="assets/icon.png" alt="MCP Advisor" width="200">
</p>

An MCP server that lets your AI assistant browse, search, and discover MCP servers from the [MCP Advisor](https://mcp-advisor.com) registry.

## Installation

```bash
pip install mcp-advisor
```

## Usage

### With Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcp-advisor": {
      "command": "mcp-advisor"
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
      "command": "mcp-advisor"
    }
  }
}
```

### Standalone

```bash
mcp-advisor                          # stdio transport (default)
mcp-advisor --transport sse          # SSE transport
mcp-advisor --api-token YOUR_TOKEN   # authenticated (for starring)
```

## Tools

| Tool | Description |
|------|-------------|
| `search_servers` | Search MCP servers with filters (query, transport, registry type, tag, sort) |
| `get_server_details` | Get full details about a specific server |
| `get_install_instructions` | Get install config for Claude Desktop, Cursor, or generic |
| `star_server` | Star a server (requires auth token) |
| `unstar_server` | Remove a star (requires auth token) |
| `list_starred_servers` | List your starred servers (requires auth token) |
| `get_trending_servers` | Get trending servers by star count |
| `get_registry_stats` | Get registry statistics |
| `browse_tags` | List all tags with server counts |

## License

MIT - Luca Stucchi

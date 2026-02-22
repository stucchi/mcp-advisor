"""MCP tool implementations — calls the MCP Advisor REST API over HTTP."""
import httpx

# Configured at startup via `configure()`
_api_url: str = "https://mcpadvisor.stucchi.consulting"
_api_token: str | None = None


def configure(api_url: str, api_token: str | None = None):
    global _api_url, _api_token
    _api_url = api_url.rstrip("/")
    _api_token = api_token


def _headers() -> dict[str, str]:
    h: dict[str, str] = {}
    if _api_token:
        h["Authorization"] = f"Bearer {_api_token}"
    return h


async def _get(path: str, params: dict | None = None) -> dict:
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(
            f"{_api_url}{path}", params=params, headers=_headers()
        )
        resp.raise_for_status()
        return resp.json()


async def _post(path: str) -> dict:
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(f"{_api_url}{path}", headers=_headers())
        resp.raise_for_status()
        return resp.json()


async def _delete(path: str) -> dict:
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.delete(f"{_api_url}{path}", headers=_headers())
        resp.raise_for_status()
        return resp.json()


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


async def search_servers(
    query: str | None = None,
    transport: str | None = None,
    registry_type: str | None = None,
    tag: str | None = None,
    sort: str = "stars",
    limit: int = 10,
) -> dict:
    """Search for MCP servers with optional filters.

    Args:
        query: Free-text search query
        transport: Filter by transport type (stdio, http, sse)
        registry_type: Filter by package registry (npm, pypi, oci)
        tag: Filter by tag name
        sort: Sort by: stars, newest, updated, relevance
        limit: Max results to return (1-50)
    """
    params: dict[str, str] = {"page_size": str(min(max(limit, 1), 50)), "sort": sort}
    if query:
        params["q"] = query
    if transport:
        params["transport"] = transport
    if registry_type:
        params["registry_type"] = registry_type
    if tag:
        params["tag"] = tag
    return await _get("/api/v1/servers", params)


async def get_server_details(name: str) -> dict:
    """Get detailed information about a specific MCP server.

    Args:
        name: The server name (e.g., 'io.github.org/my-server')
    """
    return await _get(f"/api/v1/servers/{name}")


async def get_install_instructions(
    name: str, client: str = "claude-desktop"
) -> dict:
    """Get install instructions for an MCP server tailored to a specific client.

    Args:
        name: The server name
        client: Target client: claude-desktop, cursor, or generic
    """
    detail = await _get(f"/api/v1/servers/{name}")

    instructions = []
    for pkg in detail.get("packages", []):
        rt = pkg.get("registry_type", "")
        tp = pkg.get("transport", "")
        pkg_name = pkg.get("package_name") or name

        if rt == "npm" and tp == "stdio":
            config = {"mcpServers": {name: {"command": "npx", "args": ["-y", pkg_name]}}}
        elif rt == "pypi" and tp == "stdio":
            config = {"mcpServers": {name: {"command": "uvx", "args": [pkg_name]}}}
        elif tp in ("http", "sse"):
            instructions.append({
                "type": client,
                "description": f"Remote MCP server ({tp})",
                "note": "Configure with the server URL provided by the operator",
            })
            continue
        else:
            continue

        if client == "claude-desktop":
            instructions.append({
                "type": "claude-desktop",
                "description": "Add to ~/Library/Application Support/Claude/claude_desktop_config.json",
                "config": config,
            })
        elif client == "cursor":
            instructions.append({
                "type": "cursor",
                "description": "Add to .cursor/mcp.json in your project root",
                "config": config,
            })
        else:
            instructions.append({"type": "generic", "config": config})

    return {"server": name, "client": client, "instructions": instructions}


async def star_server(name: str) -> dict:
    """Star an MCP server (requires authentication via --api-token).

    Args:
        name: The server name to star
    """
    return await _post(f"/api/v1/servers/{name}/star")


async def unstar_server(name: str) -> dict:
    """Remove a star from an MCP server.

    Args:
        name: The server name to unstar
    """
    return await _delete(f"/api/v1/servers/{name}/star")


async def list_starred_servers() -> dict:
    """List your starred MCP servers (requires authentication via --api-token)."""
    return await _get("/api/v1/me/stars")


async def get_trending_servers(limit: int = 10) -> dict:
    """Get trending MCP servers sorted by star count and recent activity.

    Args:
        limit: Max results (1-50)
    """
    return await _get("/api/v1/servers/trending", {"limit": str(min(max(limit, 1), 50))})


async def get_registry_stats() -> dict:
    """Get overall statistics about the MCP server registry."""
    return await _get("/api/v1/stats")


async def browse_tags() -> dict:
    """List all available tags with their server counts."""
    return await _get("/api/v1/tags")

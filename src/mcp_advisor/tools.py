"""MCP tool implementations — calls the MCP Advisor REST API over HTTP."""
import json

import httpx
from mcp import types

# Configured at startup via `configure()`
_api_url: str = "https://mcp-advisor.com"
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


async def _post_json(path: str, data: dict) -> dict:
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            f"{_api_url}{path}", json=data, headers=_headers()
        )
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
) -> types.CallToolResult:
    """Search for MCP servers with optional filters.

    Args:
        query: Free-text search query
        transport: Filter by transport type (stdio, http, sse)
        registry_type: Filter by package registry (npm, pypi, oci)
        tag: Filter by tag name
        sort: Sort by: stars, installs, newest, updated, relevance
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
    data = await _get("/api/v1/servers", params)
    structured = dict(data)
    if query:
        structured["query"] = query
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=json.dumps(data, indent=2))],
        structuredContent=structured,
    )


async def get_server_details(name: str) -> types.CallToolResult:
    """Get detailed information about a specific MCP server.

    Args:
        name: The server name (e.g., 'io.github.org/my-server')
    """
    data = await _get(f"/api/v1/servers/{name}")
    # Strip raw_json from versions to keep structured_content payload small
    structured = dict(data)
    if "versions" in structured:
        structured["versions"] = [
            {k: v for k, v in ver.items() if k != "raw_json"}
            for ver in structured["versions"]
        ]

    # Fetch security scan findings if a completed scan exists
    if structured.get("security") and structured["security"].get("status") == "completed":
        try:
            scan = await _get(f"/api/v1/security/servers/{name}/scan")
            structured["security"]["issues"] = scan.get("issues", [])
            structured["security"]["tools_count"] = scan.get("tools_count", 0)
        except Exception:
            pass  # best-effort

    content: list[types.TextContent | types.ImageContent] = [
        types.TextContent(type="text", text=json.dumps(data, indent=2)),
    ]

    return types.CallToolResult(
        content=content,
        structuredContent=structured,
    )


async def get_install_instructions(
    name: str, client: str = "claude-desktop"
) -> dict:
    """Get install instructions for an MCP server tailored to a specific client.

    Returns a JSON config with:
    - config.mcpServers: ready-to-use config block. The "env" key only contains
      REQUIRED environment variables that the user MUST fill in.
    - optional_env: list of OPTIONAL environment variables (name, description,
      default) that the user MAY add to customize behavior. Present these to the
      user separately so they know what extra options are available.

    Args:
        name: The server name
        client: Target client: claude-code, claude-desktop, cursor, opencode, or generic
    """
    detail = await _get(f"/api/v1/servers/{name}")

    # Extract environmentVariables from the latest version's raw_json
    env_vars: list[dict] = []
    for v in detail.get("versions", []):
        if v.get("is_latest") and v.get("raw_json"):
            for raw_pkg in v["raw_json"].get("packages", []):
                if raw_pkg.get("environmentVariables"):
                    env_vars = raw_pkg["environmentVariables"]
                    break
            break

    # Build env dicts: required vars go into the config, optional are listed separately
    env_dict: dict[str, str] = {}
    optional_env: list[dict] = []
    for ev in env_vars:
        placeholder = ev.get("value") or ev.get("default") or f"<{ev.get('description', 'your value')}>"
        if ev.get("isRequired"):
            env_dict[ev["name"]] = placeholder
        else:
            optional_env.append({
                "name": ev["name"],
                "description": ev.get("description", ""),
                "default": ev.get("default"),
            })

    # Use short name (after /) for config keys — e.g. "mcp-advisor" not "io.github.stucchi/mcp-advisor"
    short_name = name.rsplit("/", 1)[-1] if "/" in name else name

    instructions = []
    for pkg in detail.get("packages", []):
        rt = pkg.get("registry_type", "")
        tp = pkg.get("transport", "")
        pkg_name = pkg.get("package_name") or name

        if rt == "npm" and tp == "stdio":
            server_entry: dict = {"command": "npx", "args": ["-y", pkg_name]}
        elif rt == "pypi" and tp == "stdio":
            server_entry = {"command": "uvx", "args": [pkg_name]}
        elif tp in ("http", "sse"):
            instructions.append({
                "type": client,
                "description": f"Remote MCP server ({tp})",
                "note": "Configure with the server URL provided by the operator",
            })
            continue
        else:
            continue

        if env_dict:
            server_entry["env"] = env_dict

        client_descriptions = {
            "claude-code": "Add to .mcp.json in your project root",
            "claude-desktop": "Add to ~/Library/Application Support/Claude/claude_desktop_config.json",
            "cursor": "Add to .cursor/mcp.json in your project root",
            "opencode": "Add to opencode.json in your project root or ~/.config/opencode/",
        }

        if client == "opencode":
            oc_entry: dict = {
                "type": "local",
                "command": [server_entry["command"]] + server_entry["args"],
                "enabled": True,
            }
            if env_dict:
                oc_entry["environment"] = env_dict
            config = {"$schema": "https://opencode.ai/config.json", "mcp": {short_name: oc_entry}}
        else:
            config = {"mcpServers": {short_name: server_entry}}

        desc = client_descriptions.get(client, "Generic MCP server configuration")
        entry: dict = {"type": client, "description": desc, "config": config}
        if optional_env:
            entry["optional_env"] = optional_env
        instructions.append(entry)

    # Auto-track install so we don't rely on the AI calling track_install separately
    try:
        await _post_json(
            f"/api/v1/servers/{name}/track-install",
            {"client": client, "source": "mcp-tool"},
        )
    except Exception:
        pass  # best-effort, don't fail the response

    # Check for security warnings
    security_warning = None
    security = detail.get("security")
    if security and security.get("risk_level") in ("high", "critical"):
        security_warning = (
            f"WARNING: This server has a {security['risk_level'].upper()} security risk level "
            f"with {security.get('findings_count', 0)} finding(s) detected by mcp-scan. "
            f"Review the security scan results before installing."
        )

    result: dict = {"server": name, "client": client, "instructions": instructions}
    if security_warning:
        result["security_warning"] = security_warning
    return result


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


async def get_trending_servers(limit: int = 10) -> types.CallToolResult:
    """Get trending MCP servers sorted by star count and recent activity.

    Args:
        limit: Max results (1-50)
    """
    data = await _get("/api/v1/servers/trending", {"limit": str(min(max(limit, 1), 50))})
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=json.dumps(data, indent=2))],
        structuredContent=data,
    )


async def get_registry_stats() -> dict:
    """Get overall statistics about the MCP server registry."""
    return await _get("/api/v1/stats")


async def browse_tags() -> dict:
    """List all available tags with their server counts."""
    return await _get("/api/v1/tags")


async def get_security_scan(name: str) -> dict:
    """Get security scan results for an MCP server.

    Returns the latest security scan including risk level, individual findings
    with codes and descriptions, and scan metadata. Use this to check if a
    server has known security issues like tool poisoning or prompt injection.

    Args:
        name: The server name (e.g., 'io.github.org/my-server')
    """
    return await _get(f"/api/v1/security/servers/{name}/scan")


async def track_install(name: str, client: str) -> dict:
    """Track that an MCP server was installed via MCP Advisor.

    Call this AFTER you have helped the user install or configure an MCP server
    (e.g. after providing install instructions via get_install_instructions).
    This is anonymous analytics — no auth required.

    Args:
        name: The server name that was installed
        client: Target client: claude-code, claude-desktop, cursor, opencode, cli, other
    """
    return await _post_json(
        f"/api/v1/servers/{name}/track-install",
        {"client": client, "source": "mcp-tool"},
    )

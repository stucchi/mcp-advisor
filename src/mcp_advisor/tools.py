"""MCP tool implementations — served from a static JSON snapshot.

The registry data is a set of static JSON files (index.json, stats.json,
trending.json, meta.json) published to GitHub Pages and refreshed by a scheduled
job. There is no backend server: all search/detail/install logic runs locally in
this process over the downloaded snapshot, which is cached on disk with a TTL so
only the first call in a while pays the download.

`--data-url` may point at an http(s) base (default) or a local directory / file://
URL (handy for testing against a freshly built snapshot).
"""
import json
import tempfile
import time
from pathlib import Path

import httpx
from mcp import types

# Configured at startup via `configure()`
_data_url: str = "https://stucchi.github.io/mcp-advisor-app/data"
_cache_ttl: float = 6 * 3600  # 6 hours
_cache_dir: Path = Path(tempfile.gettempdir()) / "mcp-advisor-cache"

# In-memory cache: filename -> (loaded_at, data)
_mem: dict[str, tuple[float, object]] = {}


def configure(data_url: str, cache_ttl: float | None = None):
    global _data_url, _cache_ttl, _mem
    _data_url = data_url.rstrip("/")
    if cache_ttl is not None:
        _cache_ttl = cache_ttl
    _mem = {}


# ---------------------------------------------------------------------------
# Snapshot loading (http(s) with on-disk TTL cache, or local path / file://)
# ---------------------------------------------------------------------------


def _local_base() -> Path | None:
    if _data_url.startswith(("http://", "https://")):
        return None
    if _data_url.startswith("file://"):
        return Path(_data_url[len("file://"):])
    return Path(_data_url)


async def _fetch(filename: str) -> object:
    local = _local_base()
    if local is not None:
        return json.loads((local / filename).read_text())

    _cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = _cache_dir / filename
    if cache_file.exists() and time.time() - cache_file.stat().st_mtime < _cache_ttl:
        try:
            return json.loads(cache_file.read_text())
        except (OSError, ValueError):
            pass  # fall through and re-fetch on any cache read problem

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        resp = await client.get(f"{_data_url}/{filename}")
        resp.raise_for_status()
        text = resp.text
    try:
        cache_file.write_text(text)
    except OSError:
        pass  # cache is best-effort
    return json.loads(text)


async def _load(filename: str) -> object:
    now = time.time()
    cached = _mem.get(filename)
    if cached and now - cached[0] < _cache_ttl:
        return cached[1]
    data = await _fetch(filename)
    _mem[filename] = (now, data)
    return data


async def _index() -> list[dict]:
    return await _load("index.json")  # type: ignore[return-value]


def _public(server: dict) -> dict:
    """Add backward-compatible aliases expected by the embedded UI views."""
    out = dict(server)
    out["stars"] = server.get("github_stars")
    out["repo_url"] = server.get("repository_url")
    out["homepage_url"] = server.get("website_url")
    out["created_at"] = server.get("published_at")
    if server.get("latest_version") and "versions" not in out:
        out["versions"] = [
            {
                "version": server["latest_version"],
                "is_latest": True,
                "published_at": server.get("published_at"),
            }
        ]
    return out


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


def _matches(server: dict, query: str | None, transport: str | None,
             registry_type: str | None, tag: str | None) -> bool:
    if query:
        haystack = " ".join(
            str(server.get(f) or "") for f in ("name", "title", "description")
        ).lower()
        if not all(tok in haystack for tok in query.lower().split()):
            return False
    pkgs = server.get("packages", [])
    if transport and not any(p.get("transport") == transport for p in pkgs):
        return False
    if registry_type and not any(p.get("registry_type") == registry_type for p in pkgs):
        return False
    if tag and tag not in (server.get("tags") or []):
        return False
    return True


def _sort_key(sort: str, query: str | None):
    if sort in ("stars", "installs"):
        return lambda s: (s.get("github_stars") or 0, s.get("updated_at") or ""), True
    if sort == "newest":
        return lambda s: s.get("published_at") or "", True
    if sort == "updated":
        return lambda s: s.get("updated_at") or "", True
    if sort == "relevance" and query:
        q = query.lower()
        def score(s: dict):
            name = (s.get("name") or "").lower()
            title = (s.get("title") or "").lower()
            if q == name or q == title:
                return 3
            if q in name or q in title:
                return 2
            return 1
        return score, True
    return lambda s: s.get("name") or "", False


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
        sort: Sort by: stars, newest, updated, relevance
        limit: Max results to return (1-50)
    """
    limit = min(max(limit, 1), 50)
    servers = await _index()
    matched = [s for s in servers if _matches(s, query, transport, registry_type, tag)]

    key, reverse = _sort_key(sort, query)
    matched.sort(key=key, reverse=reverse)

    results = [_public(s) for s in matched[:limit]]
    data: dict = {"servers": results, "total": len(matched)}
    if query:
        data["query"] = query
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=json.dumps(data, indent=2))],
        structuredContent=data,
    )


async def get_server_details(name: str) -> types.CallToolResult:
    """Get detailed information about a specific MCP server.

    Args:
        name: The server name (e.g., 'io.github.org/my-server')
    """
    servers = await _index()
    match = next((s for s in servers if s.get("name") == name), None)
    if match is None:
        data: dict = {"error": f"Server not found: {name}"}
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=json.dumps(data, indent=2))],
            structuredContent=data,
            isError=True,
        )
    data = _public(match)
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=json.dumps(data, indent=2))],
        structuredContent=data,
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
    servers = await _index()
    detail = next((s for s in servers if s.get("name") == name), None)
    if detail is None:
        return {"error": f"Server not found: {name}", "server": name, "client": client}

    packages = detail.get("packages", [])

    # Environment variables come from the first package that declares any.
    env_vars: list[dict] = []
    for pkg in packages:
        if pkg.get("environment_variables"):
            env_vars = pkg["environment_variables"]
            break

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

    # Use short name (after /) for config keys — e.g. "mcp-advisor".
    short_name = name.rsplit("/", 1)[-1] if "/" in name else name

    instructions = []
    for pkg in packages:
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

    return {"server": name, "client": client, "instructions": instructions}


async def get_trending_servers(limit: int = 10) -> types.CallToolResult:
    """Get trending MCP servers ranked by GitHub stars and recent activity.

    Args:
        limit: Max results (1-50)
    """
    limit = min(max(limit, 1), 50)
    trending = await _load("trending.json")
    results = [_public(s) for s in trending[:limit]]  # type: ignore[index]
    data = {"servers": results}
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=json.dumps(data, indent=2))],
        structuredContent=data,
    )


async def get_registry_stats() -> dict:
    """Get overall statistics about the MCP server registry."""
    stats = await _load("stats.json")
    meta = await _load("meta.json")
    return {**stats, "generated_at": meta.get("generated_at")}  # type: ignore[dict-item]


async def browse_tags() -> dict:
    """List all available tags with their server counts."""
    servers = await _index()
    counts: dict[str, int] = {}
    for s in servers:
        for t in s.get("tags") or []:
            counts[t] = counts.get(t, 0) + 1
    tags = [{"name": t, "count": c} for t, c in sorted(counts.items(), key=lambda x: -x[1])]
    return {"tags": tags}

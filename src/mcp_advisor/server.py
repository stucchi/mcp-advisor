"""MCP Advisor — browse and discover MCP servers from your AI assistant."""
import argparse

from mcp.server.fastmcp import FastMCP

from mcp_advisor import tools
from mcp_advisor.views import DETAIL_VIEW_HTML, SEARCH_VIEW_HTML

_SEARCH_VIEW_URI = "ui://mcp-advisor/search.html"
_DETAIL_VIEW_URI = "ui://mcp-advisor/detail.html"


def build_server(data_url: str) -> FastMCP:
    """Create and return a configured FastMCP server instance."""
    tools.configure(data_url)

    mcp = FastMCP("MCP Advisor")

    # --- UI resources ---------------------------------------------------
    _csp = {"resourceDomains": [
        "https://unpkg.com",
        "https://raw.githubusercontent.com",
        "https://avatars.githubusercontent.com",
    ]}

    @mcp.resource(
        _SEARCH_VIEW_URI,
        mime_type="text/html;profile=mcp-app",
        meta={"ui": {"csp": _csp}},
    )
    def search_view() -> str:
        return SEARCH_VIEW_HTML

    @mcp.resource(
        _DETAIL_VIEW_URI,
        mime_type="text/html;profile=mcp-app",
        meta={"ui": {"csp": _csp}},
    )
    def detail_view() -> str:
        return DETAIL_VIEW_HTML

    # --- Tools with UI --------------------------------------------------
    _search_meta = {
        "ui": {"resourceUri": _SEARCH_VIEW_URI},
        "ui/resourceUri": _SEARCH_VIEW_URI,
    }
    _detail_meta = {
        "ui": {"resourceUri": _DETAIL_VIEW_URI},
        "ui/resourceUri": _DETAIL_VIEW_URI,
    }

    mcp.tool(name="search_servers", meta=_search_meta)(tools.search_servers)
    mcp.tool(name="get_server_details", meta=_detail_meta)(tools.get_server_details)
    mcp.tool(name="get_trending_servers", meta=_search_meta)(tools.get_trending_servers)

    # --- Tools without UI -----------------------------------------------
    mcp.tool(name="get_install_instructions")(tools.get_install_instructions)
    mcp.tool(name="get_registry_stats")(tools.get_registry_stats)
    mcp.tool(name="browse_tags")(tools.browse_tags)

    return mcp


def main():
    parser = argparse.ArgumentParser(
        prog="mcp-advisor",
        description="MCP server to browse, search, and discover MCP servers",
    )
    parser.add_argument(
        "--data-url",
        "--api-url",  # deprecated alias
        dest="data_url",
        default="https://stucchi.github.io/mcp-advisor-app/data",
        help="Base URL (or local dir) of the registry snapshot "
             "(default: https://stucchi.github.io/mcp-advisor-app/data)",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="MCP transport (default: stdio)",
    )
    args = parser.parse_args()

    mcp = build_server(args.data_url)
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()

"""MCP Advisor — browse and discover MCP servers from your AI assistant."""
import argparse

from mcp.server.fastmcp import FastMCP

from mcp_advisor import tools


def build_server(api_url: str, api_token: str | None = None) -> FastMCP:
    """Create and return a configured FastMCP server instance."""
    tools.configure(api_url, api_token)

    mcp = FastMCP("MCP Advisor")

    mcp.tool(name="search_servers")(tools.search_servers)
    mcp.tool(name="get_server_details")(tools.get_server_details)
    mcp.tool(name="get_install_instructions")(tools.get_install_instructions)
    mcp.tool(name="star_server")(tools.star_server)
    mcp.tool(name="unstar_server")(tools.unstar_server)
    mcp.tool(name="list_starred_servers")(tools.list_starred_servers)
    mcp.tool(name="get_trending_servers")(tools.get_trending_servers)
    mcp.tool(name="get_registry_stats")(tools.get_registry_stats)
    mcp.tool(name="browse_tags")(tools.browse_tags)
    mcp.tool(name="track_install")(tools.track_install)

    return mcp


def main():
    parser = argparse.ArgumentParser(
        prog="mcp-advisor",
        description="MCP server to browse, search, and discover MCP servers",
    )
    parser.add_argument(
        "--api-url",
        default="https://mcp-advisor.com",
        help="Base URL of the MCP Advisor API (default: https://mcp-advisor.com)",
    )
    parser.add_argument(
        "--api-token",
        default=None,
        help="JWT token for authenticated operations (star/unstar)",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="MCP transport (default: stdio)",
    )
    args = parser.parse_args()

    mcp = build_server(args.api_url, args.api_token)
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()

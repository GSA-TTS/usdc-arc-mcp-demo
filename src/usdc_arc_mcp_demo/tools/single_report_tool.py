from typing import Any, Literal

from ..api_client import get


def register_tools(mcp):
    @mcp.tool
    async def get_report(
        scope: Literal["reports", "agencies", "domain"],
        report_name: str,
        agency: str | None = None,
        domain: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> Any:
        """Fetches a report based on the given parameters.

        Args:
            scope (Literal): The scope of the report ("reports", "agencies", or "domain").
            report_name (str): The type of report (e.g., site, download, os, traffic-source).
            agency (Optional[str]): The agency slug (required if scope is "agencies").
            domain (Optional[str]): The domain name (required if scope is "domain").
            after (Optional[str]): Start date (YYYY-MM-DD).
            before (Optional[str]): End date (YYYY-MM-DD).
            limit (Optional[int]): Number of results to return per page.
            page (Optional[int]): Page number for pagination.

        Returns:
            Any: The fetched report data.
        """
        if scope == "reports":
            path = f"/reports/{report_name}/data"
        elif scope == "agencies":
            if not agency:
                raise ValueError("Missing 'agency' when scope is 'agencies'")
            path = f"/agencies/{agency}/reports/{report_name}/data"
        elif scope == "domain":
            if not domain:
                raise ValueError("Missing 'domain' when scope is 'domain'")
            path = f"/domain/{domain}/reports/{report_name}/data"
        else:
            raise ValueError(f"Unsupported scope: {scope}")

        params = {}
        if after is not None:
            params["after"] = after
        if before is not None:
            params["before"] = before
        if limit is not None:
            params["limit"] = limit
        if page is not None:
            params["page"] = page

        return await get(path, params)

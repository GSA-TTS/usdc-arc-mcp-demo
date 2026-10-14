from collections.abc import Callable
from typing import Any

from ..api_client import get
from ..constants import MCP_TOOL_LIST_LIMIT, REPORT_GROUP_BY, AggregationLevel
from ..models.aggregation_models import (
    AgencyReportParams,
    DomainReportParams,
    QueryParams,
    ReportParams,
)
from ..utils import aggregate_by_period, fetch_all_pages


async def fetch_and_aggregate(
    get_func: Callable,
    path: str,
    params: QueryParams | None,
    aggregation_level: AggregationLevel | None,
    report_name: str,
):
    """
    Fetch data using the provided get function and path, then aggregate if an aggregation level is specified.

    Args:
        get_func: Function to fetch data (e.g., get).
        path: API endpoint path.
        params: Query parameters for the request.
        aggregation_level: Level of aggregation to apply (if any).
        report_name: Name of the report being fetched.
    Returns:
        Fetched (and possibly aggregated) data.
    """
    query_params = params.model_dump(exclude_none=True) if params is not None else {}
    if aggregation_level:
        data = await fetch_all_pages(get_func, path, query_params)
        group_by_params = REPORT_GROUP_BY.get(report_name, {})
        return aggregate_by_period(
            data=data,
            period=aggregation_level,
            value_key=group_by_params.get("value_key", ""),
            group_by=group_by_params.get("group_by", None),
        )[:MCP_TOOL_LIST_LIMIT]
    return await get_func(path, query_params)


def register_tools(mcp):
    @mcp.tool
    async def get_aggregate_government_wide_report(report_params: ReportParams) -> Any:
        """
        Fetches a government wide report based on the given parameters.

        Args:
            params (ReportParams): The parameters for the report.

        Returns:
            Any: The fetched report data.
        """
        path = f"/reports/{report_params.report_name}/data"
        return await fetch_and_aggregate(
            get,
            path,
            report_params.query_params,
            report_params.aggregation_level,
            report_params.report_name,
        )

    @mcp.tool
    async def get_aggregate_agency_report(
        agency_report_params: AgencyReportParams,
    ) -> Any:
        """
        Fetch a report for a specific agency from DAP.

        Args:
            params (AgencyReportParams): The parameters for the agency report.

        Returns:
            Any: The fetched report data for the specific agency.
        """
        path = f"/agencies/{agency_report_params.agency}/reports/{agency_report_params.report_name}/data"
        return await fetch_and_aggregate(
            get,
            path,
            agency_report_params.query_params,
            agency_report_params.aggregation_level,
            agency_report_params.report_name,
        )

    @mcp.tool
    async def get_aggregate_domain_report(
        domain_report_params: DomainReportParams,
    ) -> Any:
        """
        Fetch a report for a specific domain from DAP.

        Args:
            params (DomainReportParams): The parameters for the domain report.

        Returns:
            Any: The fetched report data for the specific domain.
        """
        path = f"/domain/{domain_report_params.domain}/reports/{domain_report_params.report_name}/data"
        return await fetch_and_aggregate(
            get,
            path,
            domain_report_params.query_params,
            domain_report_params.aggregation_level,
            domain_report_params.report_name,
        )

from typing import Any

from ..api_client import get
from ..models.multiple_reports_models import (
    AgencyReportParams,
    DomainReportParams,
    ReportParams,
)


def register_tools(mcp):
    @mcp.tool
    async def get_government_wide_report(report_params: ReportParams) -> Any:
        """
        Fetches a government wide report based on the given parameters.

        Args:
            params (ReportParams): The parameters for the report.

        Returns:
            Any: The fetched report data.
        """
        path = f"/reports/{report_params.report_name}/data"
        query_params = (
            report_params.query_params.model_dump(exclude_none=True)
            if report_params.query_params is not None
            else {}
        )
        return await get(path, query_params)

    @mcp.tool
    async def get_agency_report(agency_report_params: AgencyReportParams) -> Any:
        """
        Fetch a report for a specific agency from DAP.

        Args:
            params (AgencyReportParams): The parameters for the agency report.

        Returns:
            Any: The fetched report data for the specific agency.
        """
        path = f"/agencies/{agency_report_params.agency}/reports/{agency_report_params.report_name}/data"
        query_params = (
            agency_report_params.query_params.model_dump(exclude_none=True)
            if agency_report_params.query_params is not None
            else {}
        )
        return await get(path, query_params)

    @mcp.tool
    async def get_domain_report(domain_report_params: DomainReportParams) -> Any:
        """
        Fetch a report for a specific domain from DAP.

        Args:
            params (DomainReportParams): The parameters for the domain report.

        Returns:
            Any: The fetched report data for the specific domain.
        """
        path = f"/domain/{domain_report_params.domain}/reports/{domain_report_params.report_name}/data"
        query_params = (
            domain_report_params.query_params.model_dump(exclude_none=True)
            if domain_report_params.query_params is not None
            else {}
        )
        return await get(path, query_params)

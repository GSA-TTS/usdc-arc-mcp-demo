from pydantic import BaseModel, Field, field_validator

from ..constants import AggregationLevel


class QueryParams(BaseModel):
    after: str | None = Field(None, description="Start date (YYYY-MM-DD)")
    before: str | None = Field(None, description="End date (YYYY-MM-DD)")
    page: int | None = Field(None, description="Page number for pagination")


class BaseReportParams(BaseModel):
    report_name: str = Field(
        ..., description="Report type (e.g., site, download, os, traffic-source)"
    )
    query_params: QueryParams | None = Field(
        ..., description="Additional query parameters"
    )
    aggregation_level: AggregationLevel | None = Field(
        ...,
        description="Aggregation level. If not specified, will be daily"
        " (e.g, weekly, monthly, yearly)",
    )


class ReportParams(BaseReportParams):
    """Parameters for global reports."""


class AgencyReportParams(BaseReportParams):
    agency: str = Field(..., description="Agency slug (e.g., nasa, gsa, nih)")


class DomainReportParams(BaseReportParams):
    domain: str = Field(..., description="Domain name (e.g., gsa.gov, nasa.gov)")
    report_name: str = Field(
        ...,
        description="Report type (can only be site, domain, download, second-level)",
    )

    @field_validator("report_name")
    @classmethod
    def validate_report_name(cls, v):
        allowed = ["site", "domain", "download", "second-level"]
        if v not in allowed:
            raise ValueError(f"report_name must be one of: {allowed}")
        return v

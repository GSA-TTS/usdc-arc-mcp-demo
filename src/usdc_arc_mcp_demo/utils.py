import asyncio
from collections import defaultdict
from collections.abc import Callable
from datetime import datetime
from typing import Any

from .constants import MAX_PAGE_SIZE, AggregationLevel


def aggregate_by_period(
    data: list[dict[str, Any]],
    period: AggregationLevel,
    value_key: str = "visits",
    date_key: str = "date",
    group_by: list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Aggregates data points by week, month, or year, and optionally by multiple fields.

    Args:
        data: List of data points (dicts).
        date_key: Key in dict for the date (YYYY-MM-DD).
        period: AggregationLevel (WEEKLY, MONTHLY, YEARLY).
        value_key: Key for the value to aggregate.
        group_by: Optional list of keys to further group by (e.g., ['source', 'session_default_channel_group']).
    Returns:
        List of aggregated dicts with keys: period, value_key, and group_by fields.
    """
    buckets = defaultdict(list)
    for item in data:
        dt = datetime.strptime(item[date_key], "%Y-%m-%d")
        if period == AggregationLevel.WEEKLY:
            bucket = f"{dt.isocalendar()[0]}-W{dt.isocalendar()[1]}"
        elif period == AggregationLevel.MONTHLY:
            bucket = f"{dt.year}-{dt.month:02d}"
        elif period == AggregationLevel.YEARLY:
            bucket = str(dt.year)
        else:
            raise ValueError("period must be 'week', 'month', or 'year'")
        key = [bucket]
        if group_by:
            for g in group_by:
                key.append(item.get(g, ""))
        buckets[tuple(key)].append(item[value_key])

    # Build list of dicts
    results = []
    for key_tuple, values in buckets.items():
        entry = {"period": key_tuple[0], value_key: sum(values)}
        if group_by:
            for i, g in enumerate(group_by):
                entry[g] = key_tuple[i + 1]
        results.append(entry)
    # Sort by value_key descending
    results.sort(key=lambda x: x[value_key], reverse=True)
    return results


async def fetch_all_pages(
    get_func: Callable,
    endpoint: str,
    params: dict[str, Any],
    page_param: str = "page",
    page_size_param: str = "limit",
    concurrency: int = 5,
) -> list[Any]:
    """
    Fetches all pages from an API endpoint in parallel until no results are returned.

    Args:
        get_func: Async function to fetch a page (should accept endpoint and params).
        endpoint: API endpoint.
        params: Dict of base params.
        page_param: Name of the page parameter.
        page_size_param: Name of the page size parameter.
        max_page_size: Maximum page size to request.
        concurrency: Number of concurrent requests.

    Returns:
        List of all results.
    """
    results = []
    page = 1
    finished = False

    async def fetch_page(p):
        page_params = params.copy()
        page_params[page_param] = p
        page_params[page_size_param] = MAX_PAGE_SIZE
        resp = await get_func(endpoint, page_params)
        return resp

    while not finished:
        tasks = [fetch_page(p) for p in range(page, page + concurrency)]
        pages = await asyncio.gather(*tasks)
        for data in pages:
            if not data:
                finished = True
                break
            results.extend(data)
        page += concurrency
        if all(not d for d in pages):
            break
    return results

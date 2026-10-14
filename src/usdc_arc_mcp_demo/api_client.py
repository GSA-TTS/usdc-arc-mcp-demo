import os
from typing import Any

import httpx

API_BASE = "https://api.gsa.gov/analytics/dap/v2"


async def get(endpoint: str, params: dict[str, Any] | None = None) -> Any:
    headers = {"x-api-key": os.getenv("DAP_API_KEY", "DEMO_KEY")}

    url = f"{API_BASE}{endpoint}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, headers=headers, params=params)
        resp.raise_for_status()
        return resp.json()

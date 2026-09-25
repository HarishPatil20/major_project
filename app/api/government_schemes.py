import os
import time
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query

load_dotenv()

app = FastAPI(
    title="Smart Crop Advisory - Government Schemes API",
    description="Live Government agriculture data from data.gov.in",
    version="1.0.0",
)

API_KEY = os.getenv("GOV_SCHEMES_API_KEY", "").strip()
API_URL = os.getenv("GOV_SCHEMES_API_URL", "").strip()

TIMEOUT_SECONDS = int(
    os.getenv("GOV_SCHEMES_TIMEOUT_SECONDS", "15")
)

CACHE_SECONDS = int(
    os.getenv("GOV_SCHEMES_CACHE_SECONDS", "900")
)

_cache_data = None
_cache_time = 0.0


def get_cached_data():
    global _cache_data, _cache_time

    if _cache_data is not None:
        if time.time() - _cache_time < CACHE_SECONDS:
            return _cache_data

    return None


def set_cached_data(data):
    global _cache_data, _cache_time

    _cache_data = data
    _cache_time = time.time()


def normalize_records(payload):
    """
    Convert data.gov.in response into a clean application response.
    No artificial scheme records are created.
    """

    records = payload.get("records", [])

    if not isinstance(records, list):
        raise ValueError("Invalid records format received from data.gov.in")

    result = []

    for record in records:
        if not isinstance(record, dict):
            continue

        district = (
            record.get("district")
            or record.get("DISTRICT")
            or record.get("District")
        )

        beneficiaries = (
            record.get("number_of_beneficiaries")
            or record.get("NUMBER OF BENEFICIARIES")
            or record.get("Number of Beneficiaries")
        )

        serial_no = (
            record.get("sl_no")
            or record.get("SL NO")
            or record.get("Sl No")
        )

        result.append(
            {
                "scheme_name": "PM-KISAN",
                "district": district,
                "beneficiaries": beneficiaries,
                "serial_no": serial_no,
            }
        )

    return result


@app.get("/api/government-schemes")
async def get_government_schemes(
    district: Optional[str] = Query(
        default=None,
        description="Optional district filter"
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=1000
    ),
    refresh: bool = Query(
        default=False,
        description="Force refresh from data.gov.in"
    ),
):
    if not API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Government API key is not configured."
        )

    if not API_URL:
        raise HTTPException(
            status_code=500,
            detail="Government API URL is not configured."
        )

    cached = None if refresh else get_cached_data()

    try:

        if cached is not None:

            records = cached

        else:

            params = {
                "api-key": API_KEY,
                "format": "json",
                "offset": 0,
                "limit": limit,
            }

            if district:
                params["filters[district]"] = district.strip()

            async with httpx.AsyncClient(
                timeout=TIMEOUT_SECONDS
            ) as client:

                response = await client.get(
                    API_URL,
                    params=params,
                )

            if response.status_code == 401:
                raise HTTPException(
                    status_code=502,
                    detail="Government API authentication failed."
                )

            if response.status_code == 403:
                raise HTTPException(
                    status_code=502,
                    detail="Government API access was denied."
                )

            if response.status_code >= 500:
                raise HTTPException(
                    status_code=502,
                    detail="Government data service is temporarily unavailable."
                )

            response.raise_for_status()

            payload = response.json()

            records = normalize_records(payload)

            set_cached_data(records)

        return {
            "success": True,
            "source": "data.gov.in",
            "dataset": "Districtwise Number of Beneficiaries under PM KISAN",
            "resource_id": "47a0970a-9fef-427d-8cdd-767085fda87b",
            "count": len(records),
            "filters": {
                "district": district,
                "limit": limit,
            },
            "schemes": records,
        }

    except HTTPException:
        raise

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Government API request timed out."
        )

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Unable to connect to government data service: {str(exc)}"
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Invalid response from government data service: {str(exc)}"
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected server error: {str(exc)}"
        )


@app.get("/api/government-schemes/health")
async def health_check():
    return {
        "status": "ok",
        "service": "government-schemes-api",
        "source": "data.gov.in",
    }
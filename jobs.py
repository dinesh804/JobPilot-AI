from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from job_search import search_jobs


router = APIRouter()


# ============================================================
# REQUEST SCHEMA
# ============================================================

class JobSearchRequest(BaseModel):
    query: str
    location: str = "India"
    country: str = "in"
    results_per_page: int = 10


# ============================================================
# SEARCH JOBS API
# ============================================================

@router.post("/search")
def search_jobs_api(request: JobSearchRequest):

    try:

        jobs = search_jobs(
            query=request.query,
            location=request.location,
            country=request.country,
            results_per_page=request.results_per_page,
        )

        return {
            "status": "success",
            "query": request.query,
            "location": request.location,
            "count": len(jobs),
            "jobs": [
                job.model_dump()
                for job in jobs
            ],
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
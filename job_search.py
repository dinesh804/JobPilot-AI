import os
from pathlib import Path

import requests
from dotenv import load_dotenv

from job_schema import Job


# ============================================================
# ENVIRONMENT
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")


# ============================================================
# ADZUNA JOB SEARCH
# ============================================================

def search_jobs(
    query: str,
    location: str,
    country: str = "in",
    results_per_page: int = 10,
) -> list[Job]:

    """
    Search jobs using the Adzuna API
    and convert results into Job objects.
    """

    # --------------------------------------------------------
    # Validate credentials
    # --------------------------------------------------------

    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        raise ValueError(
            "ADZUNA_APP_ID or ADZUNA_APP_KEY is missing from .env"
        )

    # --------------------------------------------------------
    # API URL
    # --------------------------------------------------------

    url = (
        f"https://api.adzuna.com/v1/api/jobs/"
        f"{country}/search/1"
    )

    # --------------------------------------------------------
    # Request parameters
    # --------------------------------------------------------

    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "what": query,
        "where": location,
        "results_per_page": results_per_page,
        "content-type": "application/json",
    }

    # --------------------------------------------------------
    # API request
    # --------------------------------------------------------

    response = requests.get(
        url,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    # --------------------------------------------------------
    # Convert Adzuna results → Job objects
    # --------------------------------------------------------

    jobs: list[Job] = []

    for item in data.get("results", []):

        # ====================================================
        # COMPANY
        # ====================================================

        company_data = item.get("company") or {}

        company_name = company_data.get(
            "display_name",
            "Unknown Company",
        )

        # ====================================================
        # LOCATION
        # ====================================================

        location_data = item.get("location") or {}

        job_location = location_data.get(
            "display_name",
            location,
        )

        # ====================================================
        # SALARY
        # ====================================================

        salary_min = item.get("salary_min")
        salary_max = item.get("salary_max")

        if salary_min is not None and salary_max is not None:

            salary = (
                f"{salary_min} - {salary_max}"
            )

        elif salary_min is not None:

            salary = str(salary_min)

        elif salary_max is not None:

            salary = str(salary_max)

        else:

            salary = None

        # ====================================================
        # EMPLOYMENT TYPE
        # ====================================================

        employment_type = item.get(
            "contract_type"
        )

        # ====================================================
        # APPLICATION URL
        # ====================================================

        job_url = item.get(
            "redirect_url"
        )

        # ====================================================
        # CREATE JOB
        # ====================================================

        job = Job(
            title=item.get(
                "title",
                "Unknown Job",
            ),

            company=company_name,

            location=job_location,

            employment_type=employment_type,

            salary=salary,

            source="Adzuna",

            url=job_url,

            description=item.get(
                "description"
            ),

            experience_required=None,

            experience_level=None,

            required_skills=[],

            preferred_skills=[],

            match_score=0.0,

            matching_skills=[],

            missing_skills=[],

            recommendation=None,

            recommendation_reason=None,
        )

        jobs.append(job)

    return jobs
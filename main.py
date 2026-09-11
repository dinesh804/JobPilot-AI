from fastapi import FastAPI

from jobs import router as jobs_router


app = FastAPI(
    title="JobPilot AI",
    description="Agentic AI Job Discovery & Career Assistant",
    version="1.0.0",
)


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "JobPilot AI",
    }


app.include_router(
    jobs_router,
    prefix="/api/jobs",
    tags=["Jobs"],
)
from pydantic import BaseModel, Field
from typing import Optional


class Job(BaseModel):
    title: str
    company: str
    location: str

    employment_type: Optional[str] = None
    salary: Optional[str] = None

    source: Optional[str] = None
    url: Optional[str] = None

    description: Optional[str] = None

    experience_required: Optional[str] = None
    experience_level: Optional[str] = None

    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)

    match_score: float = 0.0
    matching_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)

    recommendation: Optional[str] = None
    recommendation_reason: Optional[str] = None
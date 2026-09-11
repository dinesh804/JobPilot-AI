from pydantic import BaseModel, Field
from typing import Optional


class PersonalInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None


class Education(BaseModel):
    degree: Optional[str] = None
    institution: Optional[str] = None
    field_of_study: Optional[str] = None
    graduation_year: Optional[str] = None
    grade: Optional[str] = None


class Experience(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    location: Optional[str] = None
    duration: Optional[str] = None
    responsibilities: list[str] = Field(default_factory=list)


class Project(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    technologies: list[str] = Field(default_factory=list)


class Skills(BaseModel):
    programming: list[str] = Field(default_factory=list)
    machine_learning: list[str] = Field(default_factory=list)
    deep_learning: list[str] = Field(default_factory=list)
    genai: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    databases: list[str] = Field(default_factory=list)
    cloud: list[str] = Field(default_factory=list)
    devops: list[str] = Field(default_factory=list)
    data_tools: list[str] = Field(default_factory=list)
    other: list[str] = Field(default_factory=list)


class CandidateProfile(BaseModel):
    personal_info: PersonalInfo = Field(default_factory=PersonalInfo)

    summary: Optional[str] = None

    education: list[Education] = Field(default_factory=list)

    skills: Skills = Field(default_factory=Skills)

    experience: list[Experience] = Field(default_factory=list)

    projects: list[Project] = Field(default_factory=list)

    certifications: list[str] = Field(default_factory=list)

    achievements: list[str] = Field(default_factory=list)

    research: list[str] = Field(default_factory=list)

    languages: list[str] = Field(default_factory=list)

    target_roles: list[str] = Field(default_factory=list)
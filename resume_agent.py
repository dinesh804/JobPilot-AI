from typing import TypedDict, Optional

from pydantic import BaseModel, Field

from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END

from resume_schema import (
CandidateProfile,
PersonalInfo,
Education,
Skills,
Experience,
Project,
)

from test_contract_praser import extract_contact_info

# ============================================================

# 1. LLM

# ============================================================

llm = ChatOllama(
model="llama3.2:latest",
temperature=0
)

# ============================================================

# 2. FOCUSED EXTRACTION SCHEMAS

# ============================================================

class IdentityEducation(BaseModel):
    personal_info: PersonalInfo = Field(
        default_factory=PersonalInfo
    )

    education: list[Education] = Field(
        default_factory=list
    )

class SkillsExperience(BaseModel):

    skills: Skills = Field(
        default_factory=Skills
    )

    experience: list[Experience] = Field(
        default_factory=list
    )
    

class ProjectsResearch(BaseModel):


    summary: Optional[str] = None

    projects: list[Project] = Field(
        default_factory=list
    )

    certifications: list[str] = Field(
        default_factory=list
    )

    research: list[str] = Field(
        default_factory=list
    )

    achievements: list[str] = Field(
        default_factory=list
    )

    languages: list[str] = Field(
        default_factory=list
    )

    target_roles: list[str] = Field(
        default_factory=list
    )


# ============================================================

# 3. STRUCTURED LLMs

# ============================================================

identity_llm = llm.with_structured_output(
IdentityEducation
)

skills_llm = llm.with_structured_output(
SkillsExperience
)

projects_llm = llm.with_structured_output(
ProjectsResearch
)

# ============================================================

# 4. LANGGRAPH STATE

# ============================================================

class ResumeState(TypedDict):

    resume_text: str

    identity_education: IdentityEducation | None

    skills_experience: SkillsExperience | None

    projects_research: ProjectsResearch | None

    candidate_profile: CandidateProfile | None

    error: str | None

    quality_passed: bool

    retry_count: int


# ============================================================

# 5. NODE 1

# IDENTITY + EDUCATION

# ============================================================

def extract_identity_education(state: ResumeState):


    resume_text = state["resume_text"]

    print("\n" + "-" * 60)
    print("STEP 1: Identity + Education")
    print("-" * 60)

    # --------------------------------------------------------
    # 1. Deterministic contact extraction
    # --------------------------------------------------------

    try:

        contact = extract_contact_info(
            resume_text
        )

        personal_info = PersonalInfo(
            name=contact.get("name"),
            email=contact.get("email"),
            phone=contact.get("phone"),
            location=contact.get("location")
        )

        print("Contact parser: SUCCESS")

    except Exception as e:

        error_message = (
            f"Contact extraction failed: "
            f"{type(e).__name__}: {e}"
        )

        print("❌ " + error_message)

        personal_info = PersonalInfo()

    # --------------------------------------------------------
    # 2. Education extraction
    # --------------------------------------------------------

    education_prompt = f"""
    ```

    You are an expert ATS resume education extraction system.

    Your task is to extract ONLY academic education
    information from the resume.

    # RESUME:

    {resume_text}

    ============================================================

    RULES:

    1. Extract every academic education entry explicitly present.
    2. Do NOT extract certifications as education.
    3. Do NOT invent information.
    4. degree = actual degree.
    5. institution = actual university, college, or institute.
    6. field_of_study = actual field or specialization.
    7. graduation_year = only if explicitly present.
    8. grade = actual CGPA, percentage, or grade.
    9. If a field is unavailable, leave it empty.
    10. Preserve the information accurately.

    Examples of education:

    M.Sc Applied Data Science
    SRM Institute of Science and Technology
    CGPA: 8.48

    B.Sc Computer Science
    Example University
    CGPA: 8.5

    Return only the structured education information.
    """

    try:

        print("Education LLM: running...")

        result = identity_llm.invoke(
            education_prompt
        )

        final_result = IdentityEducation(
            personal_info=personal_info,
            education=result.education
        )

        print(
            f"Education entries: "
            f"{len(final_result.education)}"
        )

        print("Identity + Education: ✅ SUCCESS")

        return {
            "identity_education": final_result
        }

    except Exception as e:

        error_message = (
            f"Identity/Education extraction failed: "
            f"{type(e).__name__}: {e}"
        )

        print("\n❌ " + error_message)

        return {
            "identity_education": None,
            "error": error_message
        }


# ============================================================

# 6. NODE 2

# SKILLS + EXPERIENCE

# ============================================================

def extract_skills_experience(state: ResumeState):


    resume_text = state["resume_text"]

    print("\n" + "-" * 60)
    print("STEP 2: Skills + Experience")
    print("-" * 60)

    prompt = f"""
    ```

    You are an expert ATS resume parser.

    Extract ONLY:

    1. Technical skills
    2. Professional experience
    3. Internship experience
    4. Research experience when it represents actual work/research experience

    # RESUME:

    {resume_text}

    ============================================================

    SKILL CATEGORIES:

    Programming:
    Python, SQL, Java, C++, JavaScript, etc.

    Machine Learning:
    Scikit-Learn, XGBoost, LightGBM, CatBoost,
    PyCaret, Optuna, etc.

    Deep Learning:
    TensorFlow, Keras, PyTorch, CNN, RNN,
    GAN, etc.

    Generative AI:
    LLMs, RAG, LangChain, LangGraph,
    LangSmith, Prompt Engineering,
    Vector Databases, AI Agents, MCP, etc.

    Frameworks:
    FastAPI, Streamlit, Flask, Django,
    LangChain, LangGraph, etc.

    Databases:
    FAISS, Chroma, Qdrant, MongoDB,
    PostgreSQL, SQLite, SQLAlchemy, etc.

    Cloud:
    AWS, Azure, Azure OpenAI, GCP, etc.

    DevOps:
    Docker, Kubernetes, GitHub Actions,
    MLflow, Prometheus, Grafana, etc.

    Data Tools:
    Pandas, NumPy, Power BI, Tableau,
    Matplotlib, etc.

    Other:
    Other relevant technical tools.

    IMPORTANT RULES:

    1. Extract ONLY information explicitly present.
    2. NEVER invent skills.
    3. NEVER invent experience.
    4. Do not omit technical skills clearly listed.
    5. Human languages such as English or Tamil are NOT skills.
    6. Human languages belong only in languages, which is handled separately.
    7. Preserve company names exactly.
    8. Preserve role titles accurately.
    9. Preserve locations when available.
    10. Preserve durations when available.
    11. Preserve responsibilities accurately.
    12. Do not turn project names into professional experience.
    13. Do not turn certifications into experience.
    14. Do not create experience that does not exist.

    Return only the structured information.
    """


    try:

        print("Skills/Experience LLM: running...")

        result = skills_llm.invoke(
            prompt
        )

        # ----------------------------------------------------
        # Defensive validation
        # ----------------------------------------------------

        if result is None:

            raise ValueError(
                "LLM returned None"
            )

        print(
            "Skills/Experience LLM: SUCCESS"
        )

        total_skills = (
            len(result.skills.programming)
            + len(result.skills.machine_learning)
            + len(result.skills.deep_learning)
            + len(result.skills.genai)
            + len(result.skills.frameworks)
            + len(result.skills.databases)
            + len(result.skills.cloud)
            + len(result.skills.devops)
            + len(result.skills.data_tools)
            + len(result.skills.other)
        )

        print(
            f"Technical skills extracted: "
            f"{total_skills}"
        )

        print(
            f"Experience entries extracted: "
            f"{len(result.experience)}"
        )

        return {
            "skills_experience": result
        }

    except Exception as e:

        error_message = (
            f"Skills/Experience extraction failed: "
            f"{type(e).__name__}: {e}"
        )

        print("\n❌ " + error_message)

        return {
            "skills_experience": None,
            "error": error_message
        }


# ============================================================

# 7. NODE 3

# PROJECTS + RESEARCH + ACHIEVEMENTS

# ============================================================

def extract_projects_research(state: ResumeState):


    resume_text = state["resume_text"]

    print("\n" + "-" * 60)
    print("STEP 3: Projects + Research")
    print("-" * 60)

    prompt = f"""
    ```

    You are an expert resume parser.

    Extract the following information:

    1. Professional summary
    2. Projects
    3. Research publications
    4. Certifications
    5. Achievements
    6. Human languages
    7. Realistic target job roles

    # RESUME:

    {resume_text}

    ============================================================

    PROJECT RULES:

    1. Extract ONLY explicitly stated projects.
    2. Every project must have its actual name.
    3. Extract project descriptions when available.
    4. Extract technologies separately.
    5. Do not invent technologies.
    6. Preserve technologies exactly where possible.
    7. Do not create projects that do not exist.

    Examples of technologies:

    Python
    FastAPI
    LangChain
    LangGraph
    FAISS
    Chroma
    Qdrant
    Docker
    Azure OpenAI
    TensorFlow
    Keras
    CNN
    PyTorch
    XGBoost
    Scikit-Learn
    Streamlit

    RESEARCH RULES:

    1. Preserve actual research paper titles.
    2. Do not invent research papers.
    3. Do not convert project names into research papers.

    CERTIFICATION RULES:

    1. Preserve actual certification names.
    2. Do not invent certifications.

    ACHIEVEMENT RULES:

    1. Preserve actual achievements.
    2. Do not invent awards or rankings.

    LANGUAGE RULES:

    1. Extract ONLY human languages.
    2. Examples: English, Tamil, Hindi.
    3. Do NOT place programming languages here.

    TARGET ROLE RULES:

    Choose realistic roles based ONLY on the resume.

    Possible examples:

    AI Engineer
    Machine Learning Engineer
    Generative AI Engineer
    Data Scientist
    MLOps Engineer
    Data Analyst
    Python Developer

    Do not create unrealistic roles.

    Return only structured information.
    """


    try:

        print(
            "Projects/Research LLM: running..."
        )

        result = projects_llm.invoke(
            prompt
        )

        if result is None:

            raise ValueError(
                "LLM returned None"
            )

        print(
            "Projects/Research LLM: SUCCESS"
        )

        print(
            f"Projects extracted: "
            f"{len(result.projects)}"
        )

        print(
            f"Research entries: "
            f"{len(result.research)}"
        )

        print(
            f"Certifications: "
            f"{len(result.certifications)}"
        )

        print(
            f"Achievements: "
            f"{len(result.achievements)}"
        )

        return {
            "projects_research": result
        }

    except Exception as e:

        error_message = (
            f"Projects/Research extraction failed: "
            f"{type(e).__name__}: {e}"
        )

        print("\n❌ " + error_message)

        return {
            "projects_research": None,
            "error": error_message
        }


# ============================================================

# 8. MERGE NODE

# ============================================================

def merge_profile(state: ResumeState):


    identity = state.get(
        "identity_education"
    )

    skills_exp = state.get(
        "skills_experience"
    )

    projects = state.get(
        "projects_research"
    )

    print("\n")
    print("=" * 60)
    print("🔍 RESUME EXTRACTION DEBUG")
    print("=" * 60)

    print(
        "Identity + Education:",
        "✅ SUCCESS" if identity else "❌ FAILED"
    )

    print(
        "Skills + Experience:",
        "✅ SUCCESS" if skills_exp else "❌ FAILED"
    )

    print(
        "Projects + Research:",
        "✅ SUCCESS" if projects else "❌ FAILED"
    )

    # --------------------------------------------------------
    # If one extraction failed
    # --------------------------------------------------------

    if not identity:

        print(
            "❌ Identity/Education extraction failed."
        )

    if not skills_exp:

        print(
            "❌ Skills/Experience extraction failed."
        )

    if not projects:

        print(
            "❌ Projects/Research extraction failed."
        )

    if not identity or not skills_exp or not projects:

        existing_error = state.get(
            "error"
        )

        return {
            "candidate_profile": None,
            "error": (
                existing_error
                or
                "One or more extraction nodes failed."
            )
        }

    # --------------------------------------------------------
    # Build CandidateProfile
    # --------------------------------------------------------

    try:

        profile = CandidateProfile(
            personal_info=identity.personal_info,

            summary=projects.summary,

            education=identity.education,

            skills=skills_exp.skills,

            experience=skills_exp.experience,

            projects=projects.projects,

            certifications=projects.certifications,

            achievements=projects.achievements,

            research=projects.research,

            languages=projects.languages,

            target_roles=projects.target_roles,
        )

        print(
            "\n✅ CandidateProfile successfully created."
        )

        return {
            "candidate_profile": profile
        }

    except Exception as e:

        error_message = (
            f"CandidateProfile creation failed: "
            f"{type(e).__name__}: {e}"
        )

        print(
            "\n❌ " + error_message
        )

        return {
            "candidate_profile": None,
            "error": error_message
        }


# ============================================================

# 9. QUALITY CHECK

# ============================================================

def quality_check(state: ResumeState):


    profile = state.get(
        "candidate_profile"
    )

    print("\n")
    print("=" * 60)
    print("🔎 QUALITY CHECK")
    print("=" * 60)

    if profile is None:

        print(
            "❌ Candidate profile is empty."
        )

        return {
            "quality_passed": False,
            "error": "Candidate profile is empty."
        }

    problems = []

    # --------------------------------------------------------
    # Identity
    # --------------------------------------------------------

    if not profile.personal_info.name:

        problems.append(
            "Candidate name missing"
        )

    # --------------------------------------------------------
    # Education
    # --------------------------------------------------------

    if not profile.education:

        problems.append(
            "Education missing"
        )

    # --------------------------------------------------------
    # Skills
    # --------------------------------------------------------

    skills = profile.skills

    total_skills = (
        len(skills.programming)
        + len(skills.machine_learning)
        + len(skills.deep_learning)
        + len(skills.genai)
        + len(skills.frameworks)
        + len(skills.databases)
        + len(skills.cloud)
        + len(skills.devops)
        + len(skills.data_tools)
        + len(skills.other)
    )

    if total_skills == 0:

        problems.append(
            "Skills missing"
        )

    # --------------------------------------------------------
    # Experience / Projects
    # --------------------------------------------------------

    if (
        not profile.experience
        and
        not profile.projects
    ):

        problems.append(
            "Both experience and projects are missing"
        )

    # --------------------------------------------------------
    # Quality result
    # --------------------------------------------------------

    if problems:

        error_message = (
            " | ".join(problems)
        )

        print(
            "❌ QUALITY CHECK FAILED"
        )

        print(
            "Problems:",
            error_message
        )

        return {
            "quality_passed": False,
            "error": error_message
        }

    print(
        "✅ QUALITY CHECK PASSED"
    )

    print(
        f"Name     : "
        f"{profile.personal_info.name}"
    )

    print(
        f"Education: "
        f"{len(profile.education)}"
    )

    print(
        f"Skills   : "
        f"{total_skills}"
    )

    print(
        f"Projects : "
        f"{len(profile.projects)}"
    )

    print(
        f"Experience: "
        f"{len(profile.experience)}"
    )

    return {
        "quality_passed": True
    }


# ============================================================

# 10. RETRY NODE

# ============================================================

def retry_extraction(state: ResumeState):


    retry_count = state.get(
        "retry_count",
        0
    )

    new_retry_count = (
        retry_count + 1
    )

    print("\n")
    print("=" * 60)
    print(
        f"🔄 RETRYING RESUME EXTRACTION "
        f"({new_retry_count}/1)"
    )
    print("=" * 60)

    return {
        "retry_count": new_retry_count,

        # Clear previous extraction results
        "identity_education": None,

        "skills_experience": None,

        "projects_research": None,

        "candidate_profile": None,

        "quality_passed": False,

        "error": None
    }

# ============================================================

# 11. ROUTING

# ============================================================

def route_after_quality_check(
state: ResumeState
):


    if state["quality_passed"]:

        return "end"

    if state.get(
        "retry_count",
        0
    ) < 1:

        return "retry"

    return "end"


# ============================================================

# 12. BUILD GRAPH

# ============================================================

def build_resume_graph():


    graph = StateGraph(
        ResumeState
    )

    # --------------------------------------------------------
    # Nodes
    # --------------------------------------------------------

    graph.add_node(
        "extract_identity_education",
        extract_identity_education
    )

    graph.add_node(
        "extract_skills_experience",
        extract_skills_experience
    )

    graph.add_node(
        "extract_projects_research",
        extract_projects_research
    )

    graph.add_node(
        "merge_profile",
        merge_profile
    )

    graph.add_node(
        "quality_check",
        quality_check
    )

    graph.add_node(
        "retry_extraction",
        retry_extraction
    )

    # --------------------------------------------------------
    # Main pipeline
    # --------------------------------------------------------

    graph.add_edge(
        START,
        "extract_identity_education"
    )

    graph.add_edge(
        "extract_identity_education",
        "extract_skills_experience"
    )

    graph.add_edge(
        "extract_skills_experience",
        "extract_projects_research"
    )

    graph.add_edge(
        "extract_projects_research",
        "merge_profile"
    )

    graph.add_edge(
        "merge_profile",
        "quality_check"
    )

    # --------------------------------------------------------
    # Conditional quality routing
    # --------------------------------------------------------

    graph.add_conditional_edges(
        "quality_check",

        route_after_quality_check,

        {
            "retry":
                "retry_extraction",

            "end":
                END
        }
    )

    # --------------------------------------------------------
    # Retry
    # --------------------------------------------------------

    graph.add_edge(
        "retry_extraction",
        "extract_identity_education"
    )

    return graph.compile()


# ============================================================

# 13. COMPILE GRAPH

# ============================================================

resume_graph = build_resume_graph()

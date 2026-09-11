import streamlit as st
import tempfile
import os
import time
import hashlib

from resume_praser import extract_text_from_pdf
from resume_agent import resume_graph
from jobagent import job_discovery_graph


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="JobPilot AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 18px;
        color: #666;
        margin-bottom: 25px;
    }

    .job-card {
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #ddd;
        margin-bottom: 15px;
    }

    .score {
        font-size: 26px;
        font-weight: 700;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🚀 JobPilot AI</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
    Agentic AI Job Discovery & Career Assistant
    </div>
    """,
    unsafe_allow_html=True,
)

st.write(
    "Upload your resume and JobPilot will analyze your profile, "
    "search jobs, calculate matching scores, and recommend relevant opportunities."
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("⚙️ JobPilot Settings")

st.sidebar.markdown("---")

target_role = st.sidebar.text_input(
    "🎯 Target Job Role",
    value="Machine Learning Engineer",
)

location = st.sidebar.text_input(
    "📍 Location",
    value="India",
)

results_count = st.sidebar.slider(
    "💼 Number of Jobs",
    min_value=5,
    max_value=20,
    value=10,
)

st.sidebar.markdown("---")

st.sidebar.info(
    """
    **Current Job Source**

    🔎 Adzuna

    **AI Engine**

    🤖 Ollama

    **Framework**

    LangGraph
    """
)


# ============================================================
# SESSION STATE
# ============================================================

if "candidate_profile" not in st.session_state:
    st.session_state.candidate_profile = None

if "matched_jobs" not in st.session_state:
    st.session_state.matched_jobs = []

if "resume_filename" not in st.session_state:
    st.session_state.resume_filename = None

if "pipeline_times" not in st.session_state:
    st.session_state.pipeline_times = {}

if "pipeline_completed" not in st.session_state:
    st.session_state.pipeline_completed = False


# ============================================================
# CACHED PDF EXTRACTION
# ============================================================

@st.cache_data(show_spinner=False)
def extract_resume_cached(file_bytes: bytes) -> str:

    """
    Extract resume text.

    Streamlit caches this result based on the PDF bytes.
    """

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf",
    ) as temp_file:

        temp_file.write(file_bytes)

        temp_path = temp_file.name

    try:

        text = extract_text_from_pdf(temp_path)

        return text

    finally:

        if os.path.exists(temp_path):
            os.remove(temp_path)


# ============================================================
# RESUME UPLOAD
# ============================================================

st.subheader("📄 Upload Your Resume")

uploaded_file = st.file_uploader(
    "Choose your resume PDF",
    type=["pdf"],
    help="Upload a text-based PDF resume.",
)


# ============================================================
# MAIN PIPELINE
# ============================================================

if uploaded_file:

    st.success(
        f"✅ Resume uploaded: **{uploaded_file.name}**"
    )

    file_bytes = uploaded_file.getvalue()

    file_hash = hashlib.md5(file_bytes).hexdigest()

    st.caption(
        f"Resume ID: `{file_hash[:10]}`"
    )

    st.markdown("---")

    # ========================================================
    # RUN BUTTON
    # ========================================================

    run_pipeline = st.button(
        "🔍 Find Matching Jobs",
        type="primary",
        use_container_width=True,
    )

    # ========================================================
    # PIPELINE
    # ========================================================

    if run_pipeline:

        # Reset previous results

        st.session_state.candidate_profile = None
        st.session_state.matched_jobs = []
        st.session_state.pipeline_times = {}
        st.session_state.pipeline_completed = False

        total_start = time.perf_counter()

        try:

            # ==================================================
            # STEP 1 — PDF EXTRACTION
            # ==================================================

            step_start = time.perf_counter()

            with st.status(
                "📄 Extracting resume...",
                expanded=True,
            ) as status:

                resume_text = extract_resume_cached(
                    file_bytes
                )

                extraction_time = (
                    time.perf_counter() - step_start
                )

                st.write(
                    f"Extracted **{len(resume_text):,} characters**"
                )

                st.write(
                    f"⏱️ Time: **{extraction_time:.2f}s**"
                )

                if not resume_text:

                    status.update(
                        label="❌ Resume extraction failed",
                        state="error",
                    )

                    st.error(
                        "Could not extract text from the PDF."
                    )

                    st.stop()

                status.update(
                    label="✅ Resume extracted",
                    state="complete",
                )

            st.session_state.pipeline_times[
                "Resume Extraction"
            ] = extraction_time


            # ==================================================
            # STEP 2 — RESUME AGENT
            # ==================================================

            step_start = time.perf_counter()

            with st.status(
                "🤖 Resume Agent analyzing profile...",
                expanded=True,
            ) as status:

                resume_result = resume_graph.invoke(
                    {
                        "resume_text": resume_text,

                        "identity_education": None,

                        "skills_experience": None,

                        "projects_research": None,

                        "candidate_profile": None,

                        "error": None,

                        "quality_passed": False,

                        "retry_count": 0,
                    }
                )

                resume_time = (
                    time.perf_counter() - step_start
                )

                st.write(
                    f"⏱️ Time: **{resume_time:.2f}s**"
                )

                candidate_profile = (
                    resume_result.get(
                        "candidate_profile"
                    )
                )

                if candidate_profile is None:

                    status.update(
                        label="❌ Resume Agent failed",
                        state="error",
                    )

                    st.error(
                        "Resume Agent could not create a candidate profile."
                    )

                    error_message = resume_result.get(
                        "error"
                    )

                    if error_message:

                        st.code(
                            str(error_message)
                        )

                    st.stop()

                status.update(
                    label="✅ Resume analyzed",
                    state="complete",
                )

            st.session_state.candidate_profile = (
                candidate_profile
            )

            st.session_state.pipeline_times[
                "Resume Agent"
            ] = resume_time


            # ==================================================
            # STEP 3 — DISPLAY PROFILE
            # ==================================================

            st.success(
                "🎉 Resume successfully analyzed!"
            )

            st.markdown("---")

            st.subheader(
                "👤 Candidate Profile"
            )

            col1, col2 = st.columns(2)

            # --------------------------------------------------
            # PERSONAL INFORMATION
            # --------------------------------------------------

            with col1:

                st.markdown(
                    "### 🧑 Personal Information"
                )

                personal = (
                    candidate_profile.personal_info
                )

                st.write(
                    f"**Name:** "
                    f"{personal.name or 'Not found'}"
                )

                st.write(
                    f"**Email:** "
                    f"{personal.email or 'Not found'}"
                )

                st.write(
                    f"**Phone:** "
                    f"{personal.phone or 'Not found'}"
                )

                st.write(
                    f"**Location:** "
                    f"{personal.location or 'Not found'}"
                )


            # --------------------------------------------------
            # EDUCATION
            # --------------------------------------------------

            with col2:

                st.markdown(
                    "### 🎓 Education"
                )

                if candidate_profile.education:

                    for education in (
                        candidate_profile.education
                    ):

                        st.write(
                            f"**Degree:** "
                            f"{education.degree or 'Not found'}"
                        )

                        st.write(
                            f"**Institution:** "
                            f"{education.institution or 'Not found'}"
                        )

                        st.write(
                            f"**Field:** "
                            f"{education.field_of_study or 'Not found'}"
                        )

                        st.write(
                            f"**Year:** "
                            f"{education.graduation_year or 'Not found'}"
                        )

                        st.markdown("---")

                else:

                    st.warning(
                        "No education information detected."
                    )


            # ==================================================
            # SKILLS
            # ==================================================

            st.subheader("🧠 Skills")

            skills = candidate_profile.skills

            skill_categories = {
                "Programming": skills.programming,
                "Machine Learning": skills.machine_learning,
                "Deep Learning": skills.deep_learning,
                "GenAI": skills.genai,
                "Frameworks": skills.frameworks,
                "Databases": skills.databases,
                "Cloud": skills.cloud,
                "DevOps": skills.devops,
                "Data Tools": skills.data_tools,
                "Other": skills.other,
            }

            skill_columns = st.columns(3)

            column_index = 0

            for category, category_skills in (
                skill_categories.items()
            ):

                if category_skills:

                    with skill_columns[
                        column_index % 3
                    ]:

                        st.markdown(
                            f"**{category}**"
                        )

                        for skill in category_skills:

                            st.write(
                                f"• {skill}"
                            )

                    column_index += 1


            # ==================================================
            # PROJECTS
            # ==================================================

            if candidate_profile.projects:

                st.subheader(
                    "🛠️ Projects"
                )

                for project in (
                    candidate_profile.projects
                ):

                    with st.expander(
                        project.name
                        or "Project"
                    ):

                        if project.description:

                            st.write(
                                project.description
                            )

                        if project.technologies:

                            st.write(
                                "**Technologies:** "
                                + ", ".join(
                                    project.technologies
                                )
                            )


            # ==================================================
            # EXPERIENCE
            # ==================================================

            if candidate_profile.experience:

                st.subheader(
                    "💼 Experience"
                )

                for experience in (
                    candidate_profile.experience
                ):

                    with st.expander(
                        f"{experience.role or 'Role'} "
                        f"— "
                        f"{experience.company or 'Company'}"
                    ):

                        if experience.location:

                            st.write(
                                f"📍 {experience.location}"
                            )

                        if experience.duration:

                            st.write(
                                f"⏱️ {experience.duration}"
                            )

                        if experience.responsibilities:

                            for responsibility in (
                                experience.responsibilities
                            ):

                                st.write(
                                    f"• {responsibility}"
                                )


            # ==================================================
            # STEP 4 — JOB DISCOVERY
            # ==================================================

            st.markdown("---")

            step_start = time.perf_counter()

            with st.status(
                f"🔎 Searching {target_role} jobs...",
                expanded=True,
            ) as status:

                job_result = (
                    job_discovery_graph.invoke(
                        {
                            "candidate":
                                candidate_profile,

                            "search_query":
                                target_role,

                            "jobs": [],

                            "analyzed_jobs": [],

                            "matched_jobs": [],

                            # If your graph supports these,
                            # they can be used later.
                            "location": location,

                            "results_count":
                                results_count,
                        }
                    )
                )

                job_time = (
                    time.perf_counter()
                    - step_start
                )

                st.write(
                    f"⏱️ Time: **{job_time:.2f}s**"
                )

                matched_jobs = (
                    job_result.get(
                        "matched_jobs",
                        []
                    )
                )

                status.update(
                    label="✅ Job discovery completed",
                    state="complete",
                )


            st.session_state.matched_jobs = (
                matched_jobs
            )

            st.session_state.pipeline_times[
                "Job Discovery"
            ] = job_time


            # ==================================================
            # TOTAL TIME
            # ==================================================

            total_time = (
                time.perf_counter()
                - total_start
            )

            st.session_state.pipeline_times[
                "Total"
            ] = total_time

            st.session_state.pipeline_completed = True


            # ==================================================
            # RESULTS
            # ==================================================

            st.markdown("---")

            st.subheader(
                f"💼 Recommended Jobs "
                f"({len(matched_jobs)})"
            )


            if not matched_jobs:

                st.warning(
                    "No matching jobs were found."
                )

            else:

                # ----------------------------------------------
                # SUMMARY
                # ----------------------------------------------

                scores = [
                    job.match_score
                    for job in matched_jobs
                ]

                best_score = (
                    max(scores)
                    if scores
                    else 0
                )

                avg_score = (
                    sum(scores) / len(scores)
                    if scores
                    else 0
                )

                c1, c2, c3 = st.columns(3)

                with c1:

                    st.metric(
                        "Jobs Found",
                        len(matched_jobs),
                    )

                with c2:

                    st.metric(
                        "Best Match",
                        f"{best_score:.1f}%",
                    )

                with c3:

                    st.metric(
                        "Average Match",
                        f"{avg_score:.1f}%",
                    )


                st.markdown("---")


                # ----------------------------------------------
                # JOB CARDS
                # ----------------------------------------------

                for index, job in enumerate(
                    matched_jobs[
                        :results_count
                    ],
                    start=1,
                ):

                    with st.container(
                        border=True
                    ):

                        col_a, col_b = (
                            st.columns(
                                [4, 1]
                            )
                        )

                        # --------------------------------------
                        # JOB INFORMATION
                        # --------------------------------------

                        with col_a:

                            st.markdown(
                                f"### {index}. "
                                f"{job.title}"
                            )

                            st.write(
                                f"🏢 **{job.company}**"
                            )

                            st.write(
                                f"📍 **{job.location}**"
                            )

                            if job.employment_type:

                                st.write(
                                    f"💼 **Type:** "
                                    f"{job.employment_type}"
                                )

                            if job.salary:

                                st.write(
                                    f"💰 **Salary:** "
                                    f"{job.salary}"
                                )

                            if job.source:

                                st.caption(
                                    f"Source: {job.source}"
                                )


                        # --------------------------------------
                        # MATCH SCORE
                        # --------------------------------------

                        with col_b:

                            st.metric(
                                "Match",
                                f"{job.match_score:.1f}%"
                            )


                        # --------------------------------------
                        # SKILLS
                        # --------------------------------------

                        if job.matching_skills:

                            st.write(
                                "✅ **Matching Skills:** "
                                + ", ".join(
                                    job.matching_skills
                                )
                            )

                        if job.missing_skills:

                            st.write(
                                "❌ **Missing Skills:** "
                                + ", ".join(
                                    job.missing_skills
                                )
                            )


                        # --------------------------------------
                        # RECOMMENDATION
                        # --------------------------------------

                        if job.recommendation:

                            st.write(
                                f"🤖 **Recommendation:** "
                                f"{job.recommendation}"
                            )

                        if job.recommendation_reason:

                            st.info(
                                job.recommendation_reason
                            )


                        # --------------------------------------
                        # DESCRIPTION
                        # --------------------------------------

                        if job.description:

                            with st.expander(
                                "📋 View Job Description"
                            ):

                                st.write(
                                    job.description
                                )


                        # --------------------------------------
                        # APPLY
                        # --------------------------------------

                        if job.url:

                            st.link_button(
                                "🚀 Apply Now",
                                job.url,
                                use_container_width=True,
                            )

                        else:

                            st.warning(
                                "Application URL unavailable."
                            )


            # ==================================================
            # PERFORMANCE
            # ==================================================

            st.markdown("---")

            st.subheader(
                "⚡ Pipeline Performance"
            )

            times = (
                st.session_state.pipeline_times
            )

            if times:

                performance_cols = st.columns(
                    len(times)
                )

                for column, (
                    name,
                    duration
                ) in zip(
                    performance_cols,
                    times.items(),
                ):

                    with column:

                        st.metric(
                            name,
                            f"{duration:.2f}s"
                        )


        # ======================================================
        # ERROR HANDLING
        # ======================================================

        except Exception as e:

            st.error(
                "❌ JobPilot encountered an error."
            )

            st.exception(e)


# ============================================================
# SHOW PREVIOUS RESULTS
# ============================================================

elif (
    st.session_state.pipeline_completed
    and st.session_state.candidate_profile
):

    st.info(
        "Previous results are available in this session. "
        "Upload a new resume or click the button to run again."
    )
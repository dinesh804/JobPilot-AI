from resume_praser import extract_text_from_pdf
from resume_agent import resume_graph
from jobagent import job_discovery_graph
# ============================================================
# JOBPILOT AI
# Resume → Candidate Profile → Job Search → Analysis → Matching
# ============================================================
# ============================================================
# 1. LOAD RESUME
# ============================================================

resume_path = "resume.pdf"

resume_text = extract_text_from_pdf(
    resume_path
)


# ============================================================
# 2. RUN RESUME AGENT
# ============================================================

print("\n")
print("=" * 75)
print("📄 JOBPILOT AI")
print("=" * 75)

print("\n📄 Running Resume Agent...")


resume_result = resume_graph.invoke({

    "resume_text": resume_text,

    "identity_education": None,

    "skills_experience": None,

    "projects_research": None,

    "candidate_profile": None,

    "error": None,

    "quality_passed": False,

    "retry_count": 0
})


# ============================================================
# 3. GET CANDIDATE PROFILE
# ============================================================

candidate_profile = (
    resume_result["candidate_profile"]
)


if candidate_profile is None:

    print("\n❌ Candidate profile was not created.")

    print(
        "Resume agent error:",
        resume_result.get("error")
    )

    raise SystemExit(1)


print("\n" + "=" * 75)
print("✅ CANDIDATE PROFILE CREATED")
print("=" * 75)


# ============================================================
# 4. SHOW BASIC CANDIDATE INFORMATION
# ============================================================

personal_info = (
    candidate_profile.personal_info
)

candidate_name = (
    personal_info.name
    or "Candidate"
)

candidate_location = (
    personal_info.location
    or "Not specified"
)


print(
    f"\n👤 Candidate : {candidate_name}"
)

print(
    f"📍 Location  : {candidate_location}"
)


# ============================================================
# 5. RUN JOB DISCOVERY AGENT
# ============================================================

print("\n")
print("=" * 75)
print("🚀 RUNNING JOB DISCOVERY AGENT")
print("=" * 75)


job_result = job_discovery_graph.invoke({

    # IMPORTANT:
    # jobagent.AgentState expects "candidate"
    "candidate": candidate_profile,

    "search_query": "Machine Learning Engineer",

    "jobs": [],

    "analyzed_jobs": [],

    "matched_jobs": []
})


# ============================================================
# 6. GET MATCHED JOBS
# ============================================================

matched_jobs = (
    job_result["matched_jobs"]
)


if not matched_jobs:

    print("\n❌ No jobs found.")

    raise SystemExit(0)


# ============================================================
# 7. JOBPILOT RESULTS
# ============================================================

print("\n")
print("=" * 75)
print("🔥 JOBPILOT RESULTS")
print("=" * 75)

print(
    f"\n🎯 Search Query : Machine Learning Engineer"
)

print(
    f"📊 Jobs Found   : {len(matched_jobs)}"
)

print(
    f"🏆 Showing      : Top {min(15, len(matched_jobs))} Matches"
)


# ============================================================
# 8. DISPLAY TOP 15 JOBS
# ============================================================

for index, job in enumerate(
    matched_jobs[:15],
    start=1
):

    print("\n")

    print("━" * 75)

    print(
        f"#{index}  {job.title}"
    )

    print("━" * 75)


    # --------------------------------------------------------
    # COMPANY
    # --------------------------------------------------------

    print(
        f"🏢 Company        : "
        f"{job.company or 'Not specified'}"
    )


    # --------------------------------------------------------
    # LOCATION
    # --------------------------------------------------------

    print(
        f"📍 Location       : "
        f"{job.location or 'Not specified'}"
    )


    # --------------------------------------------------------
    # SALARY
    # --------------------------------------------------------

    print(
        f"💰 Salary         : "
        f"{job.salary or 'Not specified'}"
    )


    # --------------------------------------------------------
    # EXPERIENCE
    # --------------------------------------------------------

    print(
        f"🎓 Experience     : "
        f"{job.experience_required or 'Not specified'}"
    )


    # --------------------------------------------------------
    # EXPERIENCE LEVEL
    # --------------------------------------------------------

    print(
        f"📈 Level          : "
        f"{job.experience_level or 'Unknown'}"
    )


    # --------------------------------------------------------
    # MATCH SCORE
    # --------------------------------------------------------

    print(
        f"🎯 Match Score    : "
        f"{job.match_score:.1f}%"
    )


    # --------------------------------------------------------
    # RECOMMENDATION
    # --------------------------------------------------------

    print(
        f"🚦 Recommendation : "
        f"{job.recommendation or 'CONSIDER'}"
    )


    # --------------------------------------------------------
    # MATCHING SKILLS
    # --------------------------------------------------------

    if job.matching_skills:

        matching_skills = (
            ", ".join(
                job.matching_skills
            )
        )

    else:

        matching_skills = (
            "No matching skills identified"
        )


    print(
        f"✅ Matching Skills: "
        f"{matching_skills}"
    )


    # --------------------------------------------------------
    # MISSING SKILLS
    # --------------------------------------------------------

    if job.missing_skills:

        missing_skills = (
            ", ".join(
                job.missing_skills
            )
        )

    else:

        missing_skills = (
            "No major skill gaps identified"
        )


    print(
        f"❌ Missing Skills : "
        f"{missing_skills}"
    )


    # --------------------------------------------------------
    # REASON
    # --------------------------------------------------------

    print(
        f"💡 Reason         : "
        f"{job.recommendation_reason or 'No reason available'}"
    )


    # --------------------------------------------------------
    # APPLICATION URL
    # --------------------------------------------------------

    print(
        f"🔗 Apply          : "
        f"{job.url or 'URL not available'}"
    )


# ============================================================
# 9. END
# ============================================================

print("\n")
print("=" * 75)
print("✅ JOBPILOT JOB DISCOVERY COMPLETED")
print("=" * 75)

print(
    "\nResume → AI Profile → Job Search → "
    "Job Analysis → AI Matching → Ranking"
)

print("\n🚀 JobPilot AI is ready for the next stage.")
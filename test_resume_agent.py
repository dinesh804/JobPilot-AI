from resume_praser import extract_text_from_pdf
from resume_agent import resume_graph


pdf_path = "resume.pdf"

resume_text = extract_text_from_pdf(pdf_path)

print("Resume extracted successfully.")
print(f"Characters extracted: {len(resume_text)}")

print("\nRunning Resume Agent V3...\n")


initial_state = {
    "resume_text": resume_text,

    "identity_education": None,

    "skills_experience": None,

    "projects_research": None,

    "candidate_profile": None,

    "error": None,

    "quality_passed": False,

    "retry_count": 0
}


result = resume_graph.invoke(initial_state)


if result["error"]:

    print("ERROR:")
    print(result["error"])

else:

    print("Resume analysis completed!\n")

    profile = result["candidate_profile"]

    print(
        profile.model_dump_json(
            indent=2
        )
    )
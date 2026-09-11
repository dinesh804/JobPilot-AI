from resume_praser import extract_text_from_pdf

resume_text = extract_text_from_pdf("resume.pdf")

print("=" * 70)
print("SEARCHING FOR PROJECT SECTION")
print("=" * 70)

keywords = [
    "PROJECT",
    "RESEARCH",
    "RAG-Based",
    "AI-Powered",
    "Nutrient",
    "Dementia"
]

for keyword in keywords:

    print(f"\n--- {keyword} ---")

    index = resume_text.lower().find(keyword.lower())

    if index == -1:
        print("NOT FOUND")
    else:
        start = max(0, index - 300)
        end = min(len(resume_text), index + 1500)

        print(resume_text[start:end])
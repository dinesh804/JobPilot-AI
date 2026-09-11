
from resume_praser import extract_text_from_pdf
from test_contract_praser import extract_contact_info


resume_text = extract_text_from_pdf("resume.pdf")

contact = extract_contact_info(resume_text)

print("\nCONTACT INFORMATION")
print("=" * 50)

for key, value in contact.items():
    print(f"{key}: {value}")
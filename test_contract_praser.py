import re


def extract_contact_info(resume_text: str) -> dict:
    """
    Extract basic contact information from resume text
    using deterministic rules.
    """

    lines = [
        line.strip()
        for line in resume_text.splitlines()
        if line.strip()
    ]

    name = None
    email = None
    phone = None
    location = None

    # ==================================================
    # EMAIL
    # ==================================================

    email_match = re.search(
        r'[\w\.-]+@[\w\.-]+\.\w+',
        resume_text
    )

    if email_match:
        email = email_match.group(0)

    # ==================================================
    # PHONE
    # ==================================================

    phone_match = re.search(
        r'(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)',
        resume_text
    )

    if phone_match:
        phone = phone_match.group(0)

    # ==================================================
    # NAME
    # ==================================================

    # Look at the first few non-empty lines.
    # Resume names are commonly placed at the top.

    for line in lines[:5]:

        # Skip obvious headings
        if line.upper() in {
            "RESUME",
            "CURRICULUM VITAE",
            "CV"
        }:
            continue

        # Skip lines containing email
        if "@" in line:
            continue

        # Skip lines containing phone numbers
        if re.search(r'\d{7,}', line):
            continue

        # Skip professional title lines
        lower_line = line.lower()

        if any(keyword in lower_line for keyword in [
            "engineer",
            "developer",
            "scientist",
            "analyst",
            "student",
            "designer",
            "manager",
            "consultant",
            "specialist"
        ]):
            continue

        # Candidate name check
        if re.fullmatch(
            r"[A-Za-z][A-Za-z .'-]{1,50}",
            line
        ):
            name = line
            break

    # ==================================================
    # LOCATION
    # ==================================================

    # Check the first few lines for known location names.
    # Extract only the location instead of the entire
    # contact-information line.

    for line in lines[:10]:

        lower_line = line.lower()

        if "tamil nadu, india" in lower_line:
            location = "Tamil Nadu, India"
            break

        if "tamil nadu" in lower_line:
            location = "Tamil Nadu"
            break

        if "tiruchirappalli" in lower_line:
            location = "Tiruchirappalli, Tamil Nadu, India"
            break

        if "trichy" in lower_line:
            location = "Trichy, Tamil Nadu, India"
            break

        if "chennai" in lower_line:
            location = "Chennai, Tamil Nadu, India"
            break

        if "bangalore" in lower_line:
            location = "Bangalore, India"
            break

        if "bengaluru" in lower_line:
            location = "Bengaluru, India"
            break

        if "hyderabad" in lower_line:
            location = "Hyderabad, India"
            break

        if "delhi" in lower_line:
            location = "Delhi, India"
            break

        if "mumbai" in lower_line:
            location = "Mumbai, India"
            break

    # ==================================================
    # RETURN
    # ==================================================

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "location": location
    }


# ======================================================
# TEST
# ======================================================

if __name__ == "__main__":

    from resume_praser import extract_text_from_pdf

    resume_text = extract_text_from_pdf("resume.pdf")

    contact = extract_contact_info(resume_text)

    print("\nCONTACT INFORMATION")
    print("=" * 50)

    for key, value in contact.items():
        print(f"{key}: {value}")
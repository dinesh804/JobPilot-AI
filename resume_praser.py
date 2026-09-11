import pymupdf


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from all pages of a PDF resume.
    """

    document = pymupdf.open(file_path)

    text = ""

    for page in document:
        text += page.get_text()

    document.close()

    return text.strip()


if __name__ == "__main__":
    pdf_path = "resume.pdf"

    text = extract_text_from_pdf(pdf_path)

    print("Resume extracted successfully.")
    print(f"Characters extracted: {len(text)}")

    print("\n" + "=" * 60)
    print("EXTRACTED RESUME TEXT")
    print("=" * 60)

    print(text)
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    return "\n".join(page.get_text() for page in doc)

def extract_text_from_uploads(uploaded_files) -> dict[str,str]:
    extracted_texts_results = {}
    for file in uploaded_files:
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            extracted_texts_results[file.name] = "\n".join(p.get_text() for p in doc)
    return extracted_texts_results

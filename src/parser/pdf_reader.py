import pdfplumber

def extract_words_from_pdf(pdf_path):
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            words = page.extract_words()
            if words:
                yield words
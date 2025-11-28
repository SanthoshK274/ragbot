import PyPDF2
from tqdm import tqdm
import os

def extract_text_from_pdf(pdf_path):
    text = ""
    if hasattr(pdf_path, 'read'):
        # It's a file-like object (e.g., Streamlit upload)
        reader = PyPDF2.PdfReader(pdf_path)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    else:
        # It's a file path
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    return text

def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i+chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks

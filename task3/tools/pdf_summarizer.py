"""PDF loading and Q&A tools using PyPDF2."""

from PyPDF2 import PdfReader
from langchain_core.tools import tool

# Holds the currently loaded PDF's text in memory
pdf_storage = {"text": "", "filename": ""}


@tool
def load_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file and store it for later queries.
    Must be called before using query_pdf.
    """
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        if not text.strip():
            return "Error: Could not extract any text from this PDF."

        pdf_storage["text"] = text
        pdf_storage["filename"] = file_path.split("\\")[-1].split("/")[-1]

        word_count = len(text.split())
        page_count = len(reader.pages)
        return (
            f"Loaded '{pdf_storage['filename']}' "
            f"({page_count} pages, {word_count} words). "
            f"You can now ask questions about it using query_pdf."
        )
    except FileNotFoundError:
        return f"Error: File not found at '{file_path}'."
    except Exception as e:
        return f"Error loading PDF: {e}"


@tool
def query_pdf(question: str) -> str:
    """
    Answer a question about the currently loaded PDF.
    The PDF must be loaded first with load_pdf.
    """
    if not pdf_storage["text"]:
        return "Error: No PDF loaded yet. Please upload a PDF first."

    # Truncate to ~8000 chars to stay within context limits
    text = pdf_storage["text"][:8000]
    return (
        f"PDF Content from '{pdf_storage['filename']}':\n\n"
        f"{text}\n\n"
        f"---\nBased on the above content, please answer: {question}"
    )

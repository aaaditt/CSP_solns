"""
PDF Summarizer Tool
Extracts text from uploaded PDFs and answers questions about them.
Uses PyPDF2 for text extraction, stores text in memory for Q&A.
"""

from PyPDF2 import PdfReader
from langchain_core.tools import tool

# Simple in-memory storage for the current PDF text
pdf_storage = {"text": "", "filename": ""}


@tool
def load_pdf(file_path: str) -> str:
    """
    Loads a PDF file and extracts its text.
    Call this FIRST before asking questions about a PDF.
    Takes the file path as input.
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

        # Store for later queries
        pdf_storage["text"] = text
        pdf_storage["filename"] = file_path.split("\\")[-1].split("/")[-1]

        word_count = len(text.split())
        page_count = len(reader.pages)
        return (
            f"Successfully loaded '{pdf_storage['filename']}' "
            f"({page_count} pages, {word_count} words). "
            f"You can now ask questions about it using the query_pdf tool."
        )
    except FileNotFoundError:
        return f"Error: File not found at '{file_path}'."
    except Exception as e:
        return f"Error loading PDF: {e}"


@tool
def query_pdf(question: str) -> str:
    """
    Answers a question about the currently loaded PDF.
    The PDF must be loaded first using load_pdf.
    Use this to summarize, find key points, or answer specific questions.

    Examples:
      'Summarize this document'
      'What are the key takeaways?'
      'What does it say about security?'
    """
    if not pdf_storage["text"]:
        return "Error: No PDF loaded yet. Please upload a PDF first."

    # Return the PDF text so the LLM can reason over it
    # We truncate to ~8000 chars to stay within context limits
    text = pdf_storage["text"][:8000]
    return (
        f"PDF Content from '{pdf_storage['filename']}':\n\n"
        f"{text}\n\n"
        f"---\nBased on the above content, please answer: {question}"
    )

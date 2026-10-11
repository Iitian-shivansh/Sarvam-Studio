import os
import pypdf
from typing import Dict, Any, Optional
from sarvamai import SarvamAI


class DocumentParser:
    """
    Parses and extracts structured content from documents (PDF, TXT, Markdown)
    for generating research-grounded podcasts.
    """

    def __init__(self, client: Optional[SarvamAI] = None):
        self.client = client or SarvamAI()

    def parse_file(self, file_path: str, max_chars: int = 15000) -> Dict[str, Any]:
        """
        Parses a document file and returns extracted text, page count, and title.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document file not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        title = os.path.splitext(os.path.basename(file_path))[0].replace("_", " ").title()

        if ext == ".pdf":
            return self._parse_pdf(file_path, title, max_chars)
        elif ext in (".txt", ".md"):
            return self._parse_text(file_path, title, max_chars)
        else:
            raise ValueError(f"Unsupported file format '{ext}'. Supported: .pdf, .txt, .md")

    def _parse_pdf(self, file_path: str, title: str, max_chars: int) -> Dict[str, Any]:
        """Extracts text from PDF using pypdf with fallback."""
        text_content = []
        page_count = 0

        with open(file_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            page_count = len(reader.pages)

            for i, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                if page_text.strip():
                    text_content.append(f"--- Page {i + 1} ---\n{page_text}")
                if sum(len(t) for t in text_content) >= max_chars:
                    break

        full_text = "\n\n".join(text_content).strip()

        # If PDF was scanned (zero or minimal text extracted)
        if len(full_text) < 50:
            full_text = f"[Scanned PDF document '{title}' with {page_count} pages. Content extracted for podcast discussion.]"

        return {
            "title": title,
            "file_type": "pdf",
            "page_count": page_count,
            "text": full_text[:max_chars],
        }

    def _parse_text(self, file_path: str, title: str, max_chars: int) -> Dict[str, Any]:
        """Extracts text from text/markdown file."""
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        return {
            "title": title,
            "file_type": "text",
            "page_count": 1,
            "text": content[:max_chars],
        }

    def extract_podcast_talking_points(self, document_text: str, topic_hint: str = "") -> str:
        """
        Uses Sarvam-105B to extract key controversies, data points, and storylines
        from the document to fuel a natural 2-host podcast conversation.
        """
        prompt = f"""You are a podcast researcher. Analyze the following document and extract the 3-5 most fascinating talking points, surprising facts, and debate angles for a two-host podcast conversation.

TOPIC HINT: {topic_hint or "General Overview"}

DOCUMENT CONTENT:
\"\"\"
{document_text[:6000]}
\"\"\"

Format your response as concise bullet points:
- Key Insight & Hook:
- Surprising Fact or Data Point:
- Debate / Contrasting Perspective:
- Real-world Impact / Story:
"""
        response = self.client.chat.completions(
            model="sarvam-105b-conversations",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()

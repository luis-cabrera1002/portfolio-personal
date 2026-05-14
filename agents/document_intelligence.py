import anthropic
import pdfplumber
import os
from config import ANTHROPIC_API_KEY


class DocumentIntelligence:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = "claude-opus-4-7"

    def extract_text(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            with pdfplumber.open(file_path) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)
        elif ext in (".txt", ".md"):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def analyze_document(self, text: str, doc_type: str = "financial_report") -> str:
        text_snippet = text[:8000]
        prompt = f"""Analiza el siguiente documento financiero ({doc_type}) y extrae información clave:

{text_snippet}

Proporciona en español:
1. Resumen ejecutivo (3-5 puntos)
2. Métricas financieras clave mencionadas
3. Perspectivas y guía futura (forward guidance)
4. Riesgos y factores negativos mencionados
5. Catalizadores positivos
6. Sentimiento general del documento: POSITIVO / NEUTRAL / NEGATIVO
7. Implicaciones para inversores
"""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

    def compare_documents(self, texts: list[str], labels: list[str]) -> str:
        combined = "\n\n---\n\n".join(
            f"DOCUMENTO: {label}\n{text[:3000]}" for label, text in zip(labels, texts)
        )
        prompt = f"""Compara los siguientes documentos financieros y destaca diferencias clave:

{combined}

Responde en español con análisis comparativo, cambios importantes y tendencias."""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1536,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

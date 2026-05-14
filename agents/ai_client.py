import anthropic
from config import ANTHROPIC_API_KEY, GOOGLE_API_KEY, GEMINI_MODEL


def get_ai_response(prompt: str, max_tokens: int = 1000) -> str:
    """
    Cliente unificado de IA. Usa Gemini si está disponible,
    sino Anthropic, sino respuesta de fallback.
    """
    # Intentar Gemini primero (google-genai, la API actual)
    if GOOGLE_API_KEY:
        try:
            from google import genai
            client = genai.Client(api_key=GOOGLE_API_KEY)
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
            )
            return response.text
        except Exception as e:
            print(f"Gemini error: {e}")

    # Fallback a Anthropic
    if ANTHROPIC_API_KEY:
        try:
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            msg = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text
        except Exception as e:
            print(f"Anthropic error: {e}")

    # Fallback sin IA
    return "Análisis no disponible: configura GOOGLE_API_KEY en .env (gratuito en aistudio.google.com)"

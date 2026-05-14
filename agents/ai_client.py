import os

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")


def get_ai_response(prompt: str, max_tokens: int = 1000) -> str:
    # Re-read on every call in case vars load late (e.g. Render cold start)
    api_key = os.environ.get("GOOGLE_API_KEY") or GOOGLE_API_KEY

    if api_key and api_key.strip():
        try:
            from google import genai
            client = genai.Client(api_key=api_key.strip())
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
            )
            return response.text
        except Exception as e:
            error_msg = str(e)
            print(f"Gemini error: {error_msg}")
            if "quota" in error_msg.lower() or "429" in error_msg:
                try:
                    client2 = genai.Client(api_key=api_key.strip())
                    response2 = client2.models.generate_content(
                        model="gemini-1.5-flash",
                        contents=prompt,
                    )
                    return response2.text
                except Exception as e2:
                    print(f"Gemini fallback error: {e2}")

    anthropic_key = os.environ.get("ANTHROPIC_API_KEY") or ANTHROPIC_API_KEY
    if anthropic_key and anthropic_key.strip():
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=anthropic_key.strip())
            msg = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text
        except Exception as e:
            print(f"Anthropic error: {e}")

    return "⚠️ IA no disponible temporalmente. Los datos de mercado funcionan con normalidad."

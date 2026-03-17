from google import genai
from app.core.config import get_settings

settings = get_settings()

client = genai.Client(api_key=settings.GOOGLE_API_KEY)

# This will print every model your key can currently use
print("Available Models:")
for model in client.models.list():
    print(f"- {model.name}")


def generate_answer(prompt: str) -> str:
    # Try using the specific versioned model name
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text
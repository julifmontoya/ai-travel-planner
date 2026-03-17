# app/services/embedding_service.py

from google import genai
from app.core.config import get_settings

settings = get_settings()

client = genai.Client(api_key=settings.GOOGLE_API_KEY)


def get_valid_embedding_model() -> str:
    """
    Dynamically finds a model that supports embeddings.
    """
    try:
        for model in client.models.list():
            actions = getattr(model, "supported_actions", [])
            methods = getattr(model, "supported_methods", [])

            if "embedContent" in actions or "embedContent" in methods:
                print(f"✅ Using embedding model: {model.name}")
                return model.name

    except Exception as e:
        print(f"❌ Error listing models: {e}")

    # ❌ No fallback to invalid models
    raise ValueError("No embedding model available for this API key")


# Initialize once (cached)
SUPPORTED_MODEL = get_valid_embedding_model()


def create_embedding(text: str) -> list[float]:
    """
    Generates a vector embedding for the provided text.
    """
    if not text:
        raise ValueError("Text for embedding cannot be empty")

    try:
        response = client.models.embed_content(
            model=SUPPORTED_MODEL,
            contents=text
        )

        embedding = response.embeddings[0].values

        if not embedding:
            raise ValueError("Empty embedding returned")

        return embedding

    except Exception as e:
        print(f"❌ Error using model {SUPPORTED_MODEL}: {e}")
        raise


# --- TEST BLOCK ---
if __name__ == "__main__":
    print("\n--- Diagnostic Check ---")
    print(f"Detected Embedding Model: {SUPPORTED_MODEL}")

    try:
        sample_text = "Best beaches in Cartagena"
        vector = create_embedding(sample_text)

        print(f"✅ Success! Vector length: {len(vector)}")
        print(f"Preview: {vector[:5]}")

    except Exception as e:
        print(f"❌ Failure: {e}")
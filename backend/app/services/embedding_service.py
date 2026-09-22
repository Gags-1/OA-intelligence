import os

from google import genai
from google.genai import types
from app.core.config import settings

client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)


EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSION = 768


def generate_embedding(text: str) -> list[float]:
    """
    Generate a semantic embedding for a piece of text
    using Gemini.
    """

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            output_dimensionality=EMBEDDING_DIMENSION,
        ),
    )

    return response.embeddings[0].values

def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for multiple pieces of text.
    """

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(
            output_dimensionality=EMBEDDING_DIMENSION,
        ),
    )

    return [
        embedding.values
        for embedding in response.embeddings
    ]

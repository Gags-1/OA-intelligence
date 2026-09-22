from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from app.core.config import settings


COLLECTION_NAME = "question_embeddings"
VECTOR_SIZE = 768


client = QdrantClient(url=settings.QDRANT_URL)


def create_question_collection() -> None:
    """
    Create the Qdrant collection used for question embeddings.
    """

    collections = client.get_collections()

    existing_collections = {
        collection.name
        for collection in collections.collections
    }

    if COLLECTION_NAME in existing_collections:
        print(f"Collection already exists: {COLLECTION_NAME}")
        return

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE,
        ),
    )

    print(f"Created collection: {COLLECTION_NAME}")


def upsert_question(
    question_id: int,
    question_text: str,
    embedding: list[float],
) -> None:
    """
    Store one question embedding in Qdrant.
    """

    point = PointStruct(
        id=question_id,
        vector=embedding,
        payload={
            "question_id": question_id,
            "question_text": question_text,
        },
    )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[point],
    )


def upsert_questions(
    questions: list[tuple[int, str]],
    embeddings: list[list[float]],
) -> None:
    """
    Upsert multiple question embeddings into Qdrant.
    """

    points = [
        PointStruct(
            id=question_id,
            vector=embedding,
            payload={
                "question_id": question_id,
                "question_text": question_text,
            },
        )
        for (question_id, question_text), embedding
        in zip(questions, embeddings)
    ]

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )

def search_similar_questions(
    embedding: list[float],
    limit: int = 5,
):
    """
    Search Qdrant for questions semantically similar
    to the supplied embedding.
    """

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=embedding,
        limit=limit,
        with_payload=True,
    )

    return results.points

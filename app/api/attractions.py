from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from app.database.session import get_db
from app.database.models.attraction import Attraction
from app.schemas.attraction import AttractionCreate
from app.services.embedding_service import create_embedding

from app.services.llm_service import generate_answer

router = APIRouter()


@router.post("/attractions", status_code=201)
def create_attraction(data: AttractionCreate, db: Session = Depends(get_db)):
    try:
        # Generate embedding
        embedding = create_embedding(data.description)

        # Create DB object
        attraction = Attraction(
            name=data.name,
            description=data.description,
            embedding=embedding
        )

        db.add(attraction)
        db.commit()
        db.refresh(attraction)

        return {"id": attraction.id, "name": attraction.name}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# Shared utility to keep things DRY
def get_similar_attractions(query_embedding: List[float], db: Session, limit: int = 5):
    # Convert list to string format for pgvector if necessary: str(query_embedding)
    sql = text("""
        SELECT id, name, description
        FROM attractions
        ORDER BY embedding <-> CAST(:embedding AS vector)
        LIMIT :limit;
    """)
    # Using mappings() makes the result easier to handle
    return db.execute(sql, {"embedding": str(query_embedding), "limit": limit}).mappings().all()


@router.post("/attractions/search")
def search_attractions(query: str, db: Session = Depends(get_db)):
    if not query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")

    try:
        query_embedding = create_embedding(query)
        results = get_similar_attractions(query_embedding, db)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/attractions/ask")
def ask_ai(query: str, db: Session = Depends(get_db)):
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        query_embedding = create_embedding(query)
        results = get_similar_attractions(query_embedding, db)

        if not results:
            return {"answer": "I couldn't find any information to answer that.", "sources": []}

        context = "\n".join([f"{r['name']}: {r['description']}" for r in results])

        prompt = f"""You are a travel assistant. 
Answer the question using ONLY the context below. 
If the answer is not in the context, say you don't know.

Context:
{context}

Question:
{query}"""

        answer = generate_answer(prompt)
        return {
            "answer": answer,
            "sources": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
## Requirements & Install
```
# requirements.txt
fastapi
uvicorn
sqlalchemy
psycopg2-binary
pydantic
pydantic-settings
pgvector
google-genai
```

```
python -m venv venv
venv\Scripts\activate 
pip install -r requirements.txt
```

## Recommended Structure
```
app/
 core/
  └── config.py
 database/
  ├── base.py
  ├── session.py
  └── models/
       └── attraction.py
 main.py
```

```
# app/core/config.py
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    GOOGLE_API_KEY: str
    DEBUG: bool = False

    # CORS origins
    CORS_ORIGINS: str | None = None

    # Pydantic v2 style config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

```
# app/main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware

from app.database.session import get_db
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="AI Travel Planner API",
    debug=settings.DEBUG
)

# 👇 CORS setup
origins = []

if settings.CORS_ORIGINS:
    origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]

# fallback (for development)
if not origins:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "API is running 🚀"}

@app.get("/health/db")
def check_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
```

```
# app/database/base.py
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# 👇 import models here (later)
# from app.database.models import attraction
```

```
# app/database/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(settings.DATABASE_URL, echo=True)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## Run the app
```
uvicorn app.main:app --reload
```

## Enable extension in PostgreSQL
https://github.com/andreiramani/pgvector_pgsql_windows

```
CREATE EXTENSION IF NOT EXISTS vector;
```

## 🚀 Endpoints
### 🔹 POST `/attractions`

#### 🎯 Goal
Store travel attractions enriched with semantic meaning.

#### 🧠 What it does
- Receives attraction data
- Generates embedding using AI
- Stores data + vector in PostgreSQL (pgvector)

#### 🤖 AI usage
- ✔ Uses AI to convert description into a vector (embedding)

#### 💬 Explanation
> This endpoint creates attractions by generating vector embeddings  
> from their descriptions and storing them in PostgreSQL using pgvector,  
> enabling semantic search capabilities.

#### 📥 Request Example
```json
{
  "name": "Playa Blanca",
  "description": "Beautiful white sand beach near Cartagena with crystal clear water"
}
```

### 🔹 POST `/attractions/search`
#### 🎯 Goal
Retrieve relevant attractions based on meaning, not keywords.

#### 🧠 What it does
- Converts query into embedding
- Performs vector similarity search
- Returns most relevant attractions

#### 🤖 AI usage
- ✔ AI → converts query into vector
- ❌ DB → performs similarity search (math, not AI)

#### 💬 Explanation
We use an embedding model to convert user queries into vectors,
then perform vector similarity search in PostgreSQL using pgvector
to retrieve semantically relevant results.

#### 📥 Request Example
```json
POST /attractions/search?query=beautiful beaches with clear water
```

### 🔹 POST `attractions/ask`
#### 🎯 Goal
Generate intelligent answers using your stored data (RAG).

#### 🧠 What it does
- Converts query into embedding
- Retrieves relevant attractions
- Builds context
- Uses LLM to generate a natural language answer

#### 🤖 AI usage
- ✔ AI → embedding
- ✔ AI → answer generation (LLM)

#### 💬 Explanation
I built a RAG-based travel assistant using FastAPI, PostgreSQL with pgvector,
and Gemini. The system retrieves semantically relevant data and generates
answers using an LLM.

#### 📥 Request Example
```json
POST /attractions/ask?query=Where can I find beautiful beaches near Cartagena?
```

## Full System Summary
- ✔ AI for semantic understanding (embeddings)
- ✔ PostgreSQL + pgvector for fast similarity search
- ✔ RAG pipeline for intelligent responses
- ✔ Built with FastAPI
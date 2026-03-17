from pydantic import BaseModel

class AttractionCreate(BaseModel):
    name: str
    description: str
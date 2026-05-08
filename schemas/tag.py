from pydantic import BaseModel

class TagCreate(BaseModel):
    name: str
    description: str

class TagResposne(BaseModel):
    id: int
    name: str
    description: str
    model_config = {"from_attributes": True}
from pydantic import BaseModel


class ChatCreate(BaseModel):
    repository_id: int
    query: str


class ChatResponse(BaseModel):
    id: int
    user_id: int
    repository_id: int
    query: str
    answer: str

    model_config = {
        "from_attributes": True
    }
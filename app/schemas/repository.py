from pydantic import BaseModel, ConfigDict


class RepositoryCreate(BaseModel):
    repo_url: str


class RepositoryResponse(BaseModel):
    id: int
    repo_url: str
    user_id: int
    status : str 
    model_config = ConfigDict(from_attributes=True)
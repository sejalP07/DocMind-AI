from pydantic import BaseModel, ConfigDict


class SearchResult(BaseModel):
    id: int
    title: str
    url: str
    score: int
    snippet: str

    model_config = ConfigDict(from_attributes=True)
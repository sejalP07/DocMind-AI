from pydantic import BaseModel


class IndexRequest(BaseModel):
    id: int
    title: str
    content: str
    url: str
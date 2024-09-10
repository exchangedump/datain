from pydantic import BaseModel

class unsubscribe(BaseModel):
    id: str
    method: str

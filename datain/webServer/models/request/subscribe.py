from pydantic import BaseModel

class subscribe(BaseModel):
    id: str = None
    method: str

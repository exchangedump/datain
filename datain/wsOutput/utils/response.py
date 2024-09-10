import json
from typing import Any

class responseWs():
    
    def __init__(self, type:str, d:Any ) -> None:
        self.type = type
        self.data = d
    
    def toJson(self) -> str:
        return json.dumps({"type": self.type, "data": self.data})
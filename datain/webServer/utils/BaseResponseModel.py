from pydantic import BaseModel
import time

class ResponseModel(BaseModel):
    status: int = 0
    time: int = int(round(time.time() * 1000))

class ResponseOKModel(ResponseModel):
    status: int = 200

class ResponseErrorModel(ResponseModel):
    status: int = 500
    errorRef:str='error500'
    errorText:str='error500'

class ResponseNotFoundModel(ResponseErrorModel):
    status: int = 404
    errorRef: str = 'error404'
    errorText: str = 'Not found'

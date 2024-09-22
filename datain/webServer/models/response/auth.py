from pydantic import BaseModel
from typing import Union
from fastapi import Depends, HTTPException, status

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None

class User(BaseModel):
    client: str
    usr: str

class HTTPExceptionJWD(HTTPException):
    def __init__( self, detail):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, headers={"WWW-Authenticate": "Bearer"})
        
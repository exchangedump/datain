from fastapi import APIRouter

class BaseWebServer:
    def __init__(self) -> None:
        self.router = APIRouter()

    def get_router(self) -> APIRouter:
        return self.router

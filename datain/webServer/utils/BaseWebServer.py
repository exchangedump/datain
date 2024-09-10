from fastapi import APIRouter
from fastapi.responses import HTMLResponse



class BaseWebServer:
    def __init__(self) -> None:
        self.router = APIRouter()

    def get_router(self) -> APIRouter:
        return self.router

    def HTMLResponseFile(self, file: str) -> HTMLResponse:
        with open(file, "r") as f:
            html = f.read()
        return HTMLResponse(html)
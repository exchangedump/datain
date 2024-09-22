from fastapi import WebSocket
from datain.stream.stream import Stream
from datain.webServer.utils.BaseWebServer import BaseWebServer
from datain.wsOutput.wsManager import WebsocketsManager
from datain.wsOutput.wsControl import wsControl

from datain.webServer.models.response.auth import User
from typing_extensions import Annotated
from fastapi import Depends
from datain.webServer.utils.authUtils import is_active

class output(BaseWebServer):

    def __init__(self, wsControl: wsControl, inputStream: Stream) -> None:
        super().__init__()
        self.inputStream = inputStream
        self.connections = {}
        self.managerWs = WebsocketsManager(wsControl)

        @self.router.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket, current_user: Annotated[User, Depends(is_active)]):
            # Generar un identificador único para la conexión
            await self.managerWs.connect(websocket)

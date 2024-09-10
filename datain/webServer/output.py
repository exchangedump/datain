from fastapi import WebSocket
from datain.stream.stream import Stream
from datain.webServer.utils.BaseWebServer import BaseWebServer
from datain.wsOutput.wsManager import WebsocketsManager
from datain.wsOutput.wsControl import wsControl



class output(BaseWebServer):

    def __init__(self, wsControl: wsControl, inputStream: Stream) -> None:
        super().__init__()
        self.inputStream = inputStream
        self.connections = {}
        self.managerWs = WebsocketsManager(wsControl)

        @self.router.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            # Generar un identificador único para la conexión
            await self.managerWs.connect(websocket)

from fastapi import WebSocket
from uuid import uuid4
from typing import Any
from datain.wsOutput.utils.response import responseWs
from datain.wsOutput.wsControl import wsControl

class ws():
    def __init__(self, webSocket: WebSocket, wsControl: wsControl) -> None:
        self.wsControl = wsControl
        self.websocket = webSocket
        self.uuid = uuid4()
    
    def getId(self) -> str:
        return str(self.uuid)

    async def start(self) -> None:
        await self.websocket.accept()
        
        await self.send("connection", 'start')
        await self.send("connection_id", self.getId())
        
        while True:
            await self.input()
    
    async def stop(self) -> None:
        await self.send("connection", 'close')
        await self.websocket.accept()
    
    async def send(self, _type:str, _d:Any):
        """Enviar un mensaje a un cliente específico."""
        await self.output( responseWs(type=_type, d=_d).toJson() )

    async def input(self):
        """Enviar un mensaje a un cliente específico."""
        data = await self.websocket.receive_text()
        rs = await self.wsControl.input(data, self)
        if rs is not None:
            if isinstance(rs, responseWs):
                await self.output(rs.toJson())
            else:              
                await self.send("response_action", rs)

    async def output(self, message: str):
        """Enviar un mensaje a un cliente específico."""
        await self.websocket.send_text(message)

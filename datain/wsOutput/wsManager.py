from fastapi import WebSocket
from typing import Dict, List

from datain.wsOutput.ws import ws
from datain.wsOutput.wsControl import wsControl

class WebsocketsManager:
    def __init__(self, wsControl: wsControl) -> None:
        self.connections: Dict[str, ws] = {}
        self.wsControl = wsControl

    async def connect(self, websocket: WebSocket):
        """Agregar una nueva conexión al administrador."""
        
        tmp = ws(websocket, self.wsControl)
        await tmp.start()
        self.connections[ tmp.getId() ] = tmp
        print(f"Connection {tmp.getId()} established.")

    def disconnect(self, connection_id: str):
        """Eliminar una conexión del administrador."""
        if connection_id in self.connections:
            self.connections[connection_id].stop()
            del self.connections[connection_id]
            print(f"Connection {connection_id} disconnected.")

    
    def getWs(self, connection_id: str) -> ws | None:
        """Obtener un objeto ws específico."""
        if connection_id in self.connections:
            return self.connections[connection_id]

    async def broadcast(self, message: str):
        """Difundir un mensaje a todos los clientes conectados."""
        for connection_id, websocket in self.connections.items():
            await websocket.send('broadcast', message)

    
    async def get_connections(self) -> List[str]:
        """Obtener una lista de los IDs de las conexiones activas."""
        return list(self.connections.keys())
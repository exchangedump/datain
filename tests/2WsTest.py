import json
import uvicorn
from rich.console import Console
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient

from uuid import uuid4

console = Console()
console.clear()


# Diccionario para almacenar conexiones activas con sus identificadores únicos
connections = {}
suscripciones = {}

# Crear una instancia de FastAPI
app = FastAPI()


async def asyncfunc(_call, args):
    await _call(args)
    

def ws_on_message(_, msg):
    print('ws_on_message')
    for call in suscripciones.values():
        asyncio.run(asyncfunc(call['callback'], msg))

streamIn = UMFuturesWebsocketClient( on_message=ws_on_message, is_combined=True )

def streamInSubscribe(event: str, OutSocket: WebSocket, id: str = None):
    if id is None:
        id = str(uuid4())
    
    tmp = subscribe_callback(OutSocket, id)
    
    suscripciones[id] = {
        'even': event,
        'callback': tmp.callback
    }
    streamIn.subscribe(event)

class subscribe_callback():
    def __init__(self, ws: WebSocket, id) -> None:
        self.ws = ws
        self.id = str(id)

    async def callback(self, data):
        print("subscribe_callback.callback")
        await self.ws.send_text(json.dumps({ 'id': self.id, 'data':data }))

@app.websocket("/ws")
async def websocket_endpoint(OutSocket: WebSocket):
    # Generar un identificador único para la conexión
    connection_id = str(uuid4())
    # Aceptar la conexión
    await OutSocket.accept()
    # Guardar la conexión con su identificador
    connections[connection_id] = OutSocket
    try:
        # Enviar el identificador único al cliente
        await OutSocket.send_text(f"Your connection ID: {connection_id}")
        
        # Mantener la conexión abierta mientras recibe mensajes
        while True:
            data = await OutSocket.receive_text()
            if data == 'suscripcion':
                streamInSubscribe('btcusdt@depth', OutSocket, connection_id)
    
    except WebSocketDisconnect:
        # Eliminar la conexión cuando el cliente se desconecte
        del connections[connection_id]
        print(f"Connection {connection_id} closed")

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>WebSocket Test</title>
    </head>
    <body>
        <h1>WebSocket Test</h1>
        <textarea id="messageText">suscripcion</textarea>
        <button onclick="sendMessage()">Send Message</button>
        <ul id="messages"></ul>
        <script>
            var ws = new WebSocket("ws://0.0.0.0:8880/ws");

            ws.onmessage = function(event) {
                var messages = document.getElementById('messages');
                var message = document.createElement('li');
                message.textContent = event.data;
                messages.appendChild(message);
            };

            function sendMessage() {
                ws.send(document.getElementById('messageText').value);
            }
        </script>
    </body>
</html>
"""
@app.router.get("/client")
async def get():
    return HTMLResponse(html)



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8880)
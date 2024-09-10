from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from datain.stream.stream import Stream
from datain.webServer.utils.BaseWebServer import BaseWebServer
from uuid import uuid4
from datain.wsOutput.wsManager import WebsocketsManager
from datain.wsOutput.wsControl import wsControl



class output(BaseWebServer):

    def __init__(self, wsControl: wsControl, inputStream: Stream) -> None:
        super().__init__()
        self.inputStream = inputStream
        self.connections = {}
        self.managerWs = WebsocketsManager(wsControl)

        html = """
        <!DOCTYPE html>
        <html>
            <head>
                <title>WebSocket Test</title>
            </head>
            <body>
                <h1>WebSocket Test</h1>
                <textarea id="messageText">{"action":"subscribe", "args": {"symbol": "btcusdt@kline_1m", "id": "123"}}</textarea>
                <button onclick="sendMessage()">Send Message</button>
                <button onclick="sendMessageAttr('')">Send Message</button>
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

                    function sendMessageAttr(msg) {
                        ws.send(msg);
                    }

                </script>
            </body>
        </html>
        """
        @self.router.get("/clientWs")
        async def get():
            return HTMLResponse(html)
        
        @self.router.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            # Generar un identificador único para la conexión
            await self.managerWs.connect(websocket)

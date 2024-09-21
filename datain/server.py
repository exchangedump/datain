import uvicorn
from rich.console import Console

from datain.stream.stream import Stream

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from datain.wsOutput.wsControl import wsControl


from datain.webServer.subscribe import subscribe as subscribeWebServer
from datain.webServer.status import status as statusWebServer
from datain.webServer.output import output as wsOutputWebServer
from datain.webServer.control import control as controlWebServer


console = Console()
console.clear()

if __name__ == "__main__":
    
    _Stream = Stream()
    # _Stream.start()
    
    _wsControl = wsControl(_Stream)
    
    
    # Crear una instancia de la clase ChatBotAPI
    _subscribeWebServer = subscribeWebServer(_Stream)
    _statusWebServer = statusWebServer(_Stream)
    _wsOutputWebServer = wsOutputWebServer(_wsControl, _Stream)
    _htmlWebServer = htmlWebServer(_Stream)
    _controlWebServer = controlWebServer(_Stream)

    # Crear una instancia de FastAPI
    app = FastAPI()
    app.mount('/static', StaticFiles(directory='datain/webServer/static', html=True), name='static')


    # Registrar las rutas definidas en la clase ChatBotAPI
    app.include_router(_subscribeWebServer.get_router())
    app.include_router(_statusWebServer.get_router())
    app.include_router(_wsOutputWebServer.get_router())
    app.include_router(_htmlWebServer.get_router())
    app.include_router(_controlWebServer.get_router())
    

    uvicorn.run(app, host="0.0.0.0", port=8880)
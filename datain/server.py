import uvicorn
import os
from rich.console import Console

from datain.stream.stream import Stream

from fastapi import FastAPI

from datain.wsOutput.wsControl import wsControl


from datain.webServer.subscribe import subscribe as subscribeWebServer
from datain.webServer.status import status as statusWebServer
from datain.webServer.output import output as wsOutputWebServer
from datain.webServer.control import control as controlWebServer
from datain.webServer.auth import auth as authWebServer


console = Console()
console.clear()

if __name__ == "__main__":

    _Stream = Stream()
    if 'STREAM_IN_AUTOSTART' in os.environ:
        if os.environ['STREAM_IN_AUTOSTART'] == 'true':
            _Stream.start()
    
    _wsControl = wsControl(_Stream)
    
    _authWebServer = authWebServer()
    _subscribeWebServer = subscribeWebServer(_Stream)
    _statusWebServer = statusWebServer(_Stream)
    _wsOutputWebServer = wsOutputWebServer(_wsControl, _Stream)
    _controlWebServer = controlWebServer(_Stream)

    # Crear una instancia de FastAPI
    app = FastAPI()

    # Registrar las rutas definidas
    app.include_router(_authWebServer.get_router())
    app.include_router(_subscribeWebServer.get_router())
    app.include_router(_statusWebServer.get_router())
    app.include_router(_wsOutputWebServer.get_router())
    app.include_router(_controlWebServer.get_router())
    

    uvicorn.run(app, host=os.environ['SERVER_HOST'], port=int(os.environ['SERVER_PORT']))
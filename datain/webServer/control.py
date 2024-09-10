from datain.stream.stream import Stream

from datain.webServer.models.control.startResponse import startResponse
from datain.webServer.utils.BaseWebServer import BaseWebServer
from datain.webServer.utils.BaseResponseModel import ResponseErrorModel
from datain.webServer.models.response.status import statusOk as statusResponse


class control(BaseWebServer):

    def __init__(self, inputStream: Stream) -> None:
        super().__init__()
        self.inputStream = inputStream
        
        @self.router.get("/control/start")
        async def start() -> startResponse:
            self.inputStream.start()
            return startResponse()

        @self.router.get("/control/stop")
        async def stop() -> startResponse:
            self.inputStream.stop()
            return startResponse()

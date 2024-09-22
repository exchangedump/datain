from datain.stream.stream import Stream

from datain.webServer.models.control.startResponse import startResponse
from datain.webServer.utils.BaseWebServer import BaseWebServer
from datain.webServer.utils.BaseResponseModel import ResponseErrorModel
from datain.webServer.models.response.status import statusOk as statusResponse


from datain.webServer.models.response.auth import User
from typing_extensions import Annotated
from fastapi import Depends
from datain.webServer.utils.authUtils import is_active

class control(BaseWebServer):

    def __init__(self, inputStream: Stream) -> None:
        super().__init__()
        self.inputStream = inputStream
        
        @self.router.get("/control/start")
        async def start(current_user: Annotated[User, Depends(is_active)]) -> startResponse:
            self.inputStream.start()
            return startResponse()

        @self.router.get("/control/stop")
        async def stop(current_user: Annotated[User, Depends(is_active)]) -> startResponse:
            self.inputStream.stop()
            return startResponse()

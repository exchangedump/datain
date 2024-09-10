from datain.stream.stream import Stream

from datain.webServer.utils.BaseWebServer import BaseWebServer
from datain.webServer.utils.BaseResponseModel import ResponseErrorModel
from datain.webServer.models.response.status import statusOk as statusResponse


class status(BaseWebServer):

    def __init__(self, inputStream: Stream) -> None:
        super().__init__()
        self.inputStream = inputStream
        
        @self.router.post("/status")
        async def status() -> statusResponse | ResponseErrorModel:
            
            try:
                self.inputStream
                return statusResponse(uptime=True, up=self.inputStream.running, down=not self.inputStream.running)
            except Exception as e:
                return ResponseErrorModel(errorRef='status:1', errorText=str(e))


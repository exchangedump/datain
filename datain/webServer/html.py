from datain.stream.stream import Stream

from datain.webServer.utils.BaseWebServer import BaseWebServer
from datain.webServer.utils.BaseResponseModel import ResponseErrorModel
from datain.webServer.models.response.status import statusOk as statusResponse
from fastapi.responses import HTMLResponse

class html(BaseWebServer):

    def __init__(self, inputStream: Stream) -> None:
        super().__init__()
        self.inputStream = inputStream
        
        @self.router.get("/clients")
        async def cliente() -> HTMLResponse:
            return self.HTMLResponseFile('datain/webServer/html/client.html')

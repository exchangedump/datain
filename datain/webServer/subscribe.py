from datain.stream.stream import Stream

from datain.webServer.utils.BaseWebServer import BaseWebServer
from datain.webServer.models.request.subscribe import subscribe as subscribeRequest
from datain.webServer.models.response.subscribe import subscribeOk as subscribeOkResponse
from datain.webServer.models.response.subscribe import subscribeError as subscribeErrorResponse

from datain.webServer.models.request.unsubscribe import unsubscribe as unsubscribeRequest
from datain.webServer.models.response.unsubscribe import unsubscribeOk as unsubscribeOkResponse
from datain.webServer.models.response.unsubscribe import unsubscribeError as unsubscribeErrorResponse


class subscribe(BaseWebServer):

    def __init__(self, inputStream: Stream) -> None:
        super().__init__()
        self.inputStream = inputStream
        
        @self.router.post("/subscribe")
        async def subscribe( data: subscribeRequest ) -> subscribeOkResponse | subscribeErrorResponse:
            
            try:
                self.inputStream.subscribe(
                    key=data.method,
                    callback=self.asd,
                    id=data.id)
                return subscribeOkResponse(id=data.id)
            except Exception as e:
                return subscribeErrorResponse(id=data.id, errorRef='subscribe:1', errorText=str(e))

        @self.router.post("/unsubscribe")
        async def unsubscribe( data: unsubscribeRequest ) -> unsubscribeOkResponse | unsubscribeErrorResponse:
            
            try:
                self.inputStream.unsubscribe(
                    key=data.method,
                    id=data.id)
                return unsubscribeOkResponse(id=data.id)
            except Exception as e:
                return unsubscribeErrorResponse(id=data.id, errorRef='ununsubscribe:1', errorText=str(e))

            

    def asd(self, data):
        pass
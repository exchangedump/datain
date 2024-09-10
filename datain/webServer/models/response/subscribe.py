from datain.webServer.utils.BaseResponseModel import ResponseErrorModel, ResponseOKModel


class subscribeOk(ResponseOKModel):
    id: str

class subscribeError(ResponseErrorModel):
    id: str

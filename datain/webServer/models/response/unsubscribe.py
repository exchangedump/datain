from datain.webServer.utils.BaseResponseModel import ResponseErrorModel, ResponseOKModel


class unsubscribeOk(ResponseOKModel):
    id: str

class unsubscribeError(ResponseErrorModel):
    id: str

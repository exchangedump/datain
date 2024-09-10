from datain.webServer.utils.BaseResponseModel import ResponseOKModel


class statusOk(ResponseOKModel):
    uptime: bool
    up: bool
    down: bool


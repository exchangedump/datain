import asyncio



class subscribe_callback():
    def __init__(self, ws, id) -> None:
        self.ws = ws
        self.id = id

    def callback(self, data):
        print("subscribe_callback.callback")
        asyncio.run(self.ws.send(self.id, data))

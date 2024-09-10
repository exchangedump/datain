import asyncio
import json
from datain.stream.stream import Stream
from binance.lib.utils import get_timestamp

from datain.wsOutput.utils.actionSubscribe import subscribe_callback
from datain.wsOutput.utils.response import responseWs

class wsControl():
    def __init__(self, _stream: Stream) -> None:
        self.inputStream = _stream
        pass
    
    async def input(self, data: str, ws) -> str | None:
        d = self.is_valid(data)
        if d is None:
            return None

        if 'action' not in d:
            return None
        
        action = f'action_{d["action"]}'
        args = d['args'] if 'args' in d else None
        
        _call = getattr(self, action, None)
        if not callable(_call):
            return None
        
        return await _call(args, ws)
    def is_valid(self, d):
        try:
            return json.loads(d)
        except ValueError:
            return None

    async def action_test(self, args: dict, ws) -> str:
        await self.action_test_muleta(ws)
        return None

    async def action_test_muleta(self, ws) -> str:
        await ws.send('test', 'lalallala')

    
    async def action_subscribe(self, args: dict, ws) -> str:
        # {"action":"subscribe", "args": {"event": "btcusdt@depth", "id": "123"}}
        if 'event' not in args:
            return None

        if 'id' not in args:
            id = get_timestamp()
        else:
            id = args['id']

        _callback = subscribe_callback(ws, id)
        
        self.inputStream.subscribe(args['event'], _callback.callback, id)
        
        return responseWs('subscribe', { 'status': True, 'id': id, 'event': args['event'] } )

    async def action_unsubscribe(self, args: dict, ws) -> str:
        # {"action":"unsubscribe", "args": {"event": "btcusdt@depth", "id": "123"}}
        if 'event' not in args:
            return responseWs('unsubscribe', { 'status': False, 'error': 'unsubscribe:1', 'error_text': 'No se envio attr "event"' } )

        if 'id' not in args:
            return responseWs('unsubscribe', { 'status': False, 'error': 'unsubscribe:1', 'error_text': 'No se envio attr "id"' } )

        self.inputStream.unsubscribe(args['event'], id)

        return responseWs('unsubscribe', { 'status': True, 'id': id, 'event': args['event'] } )




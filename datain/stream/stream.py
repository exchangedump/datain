import json
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
import logging

from websocket import (WebSocketException, WebSocketConnectionClosedException)
from binance.lib.utils import get_timestamp

class Stream:
    """
    Clase para gestionar un WebSocket, suscripciones a eventos y reconexiones.
    """

    def __init__(self, logger=None ):
        """
        Inicializa la clase Stream con la URL del WebSocket.
        """
        self.subscriptions = {}  # Diccionario de suscripciones
        self.client = None
        self.running = False  # Estado del WebSocket
        if not logger:
            logger = logging.getLogger('Stream')
            logging.basicConfig(level=logging.INFO)
            
        self.logger = logger
        self.logger.info("__init__")

    def start(self):
        """
        Inicia el WebSocket y comienza a escuchar los eventos utilizando asyncio.run().
        """
        self.logger.info("start")

        try:
            self.client = UMFuturesWebsocketClient(
                on_message=self.on_message,
                on_open=self.on_open,
                on_close=self.on_close,
                on_error=self.on_error,
                is_combined=True
            )
            self._subscribe_pending()
        except WebSocketException as e:
            if isinstance(e, WebSocketConnectionClosedException):
                self.reconnect()


    def stop(self):
        """
        Detiene el WebSocket y la escucha de eventos.
        """
        self.running = False
        self.client.stop()

    async def reconnect(self):
        """
        Intenta reconectar el WebSocket después de una desconexión.
        """
        self.logger.info('reconnect')
        for key in self.subscriptions.keys():
            self.subscriptions[key]['status'] = False
        self.client.stop()
        self.start()


    def on_message(self, *args):
        """
        Función para manejar los mensajes recibidos del WebSocket.
        """
        self.logger.info("on_message")
        self.logger.debug(args)
        data = json.loads(args[1])  # Convertir string a dict
        if 'stream' in data:
            self._subscribe_callback(data['stream'], data['data'])


    def on_open(self, *args):
        """
        Función para manejar la apertura del WebSocket.
        """
        self.logger.info("on_open")
        self.logger.debug(args)
        self.running = True
    def on_close(self, *args):
        """
        Función para manejar el cierre del WebSocket.
        """
        self.logger.info("on_close")
        
        if(self.running):
            # Reconnect
            self.reconnect()

    def on_error(self, *args):
        """
        Función para manejar errores del WebSocket.
        """
        self.logger.info("on_error")
        self.logger.debug(args)

    def _subscribe_pending(self):
        self.logger.info("_subscribe_pending")
        if self.running:
            for key in self.subscriptions.keys():
                self.client.subscribe(key)

    def _subscribe_callback(self, key, data):
        self.logger.info(f"_subscribe_callback {key}")
        self.logger.debug(data)
        if key in self.subscriptions:
            for id in self.subscriptions[key]['callbacks'].keys():
                self.logger.debug(self.subscriptions[key]['callbacks'][id].__name__ )
                self.subscriptions[key]['callbacks'][id](data)


    def subscribe(self, key, callback, id=None):
        """
        Suscribe un símbolo a un evento y establece un callback para manejar los datos.

        :param event_name: El nombre del evento (ej. 'depth', 'trades').
        :param callback: La función que manejará los datos recibidos.
        """
        self.logger.info(f"Subscribed to init {key} => {id}")
        if(id is None):
            id = get_timestamp()

        if(key not in self.subscriptions):
            self.subscriptions[key] = {
                'status': False,
                'callbacks': {}
            }
        else:
            self.subscriptions[key]['status'] = True
        
        self.subscriptions[key]['callbacks'][id] = callback
        
        self.logger.info(f"Subscribed to end {key} => {id}")
        
        return id
        

    def unsubscribe(self, key, id=None, callback=None):
        """
        Desuscribe un símbolo de un evento.

        :param key: El nombre del evento del que desuscribirse.
        :param id: El ID de la suscripción.
        :param callback: La función de callback a desuscribir.
        """
        
        self.logger.info(f"Unsubscribed from init {key}")
        
        if(key in self.subscriptions):
            if(id is not None):
                if(id in self.subscriptions[key]['callbacks']):
                    del self.subscriptions[key]['callbacks'][id]
                    self.logger.debug(f"Unsubscribed from {key} => {id}")
            else:
                for id in self.subscriptions[key]['callbacks'].keys():
                    if(callback == self.subscriptions[key]['callbacks'][id]):
                        del self.subscriptions[key]['callbacks'][id]
                        self.logger.debug(f"Unsubscribed from {key} => {callback}")
        
        if(len(self.subscriptions[key]) == 0):
            if self.running:
                self.client.unsubscribe(key)
            self.subscriptions[key]['status'] = False
        
        self.logger.info(f"Unsubscribed from {key}")

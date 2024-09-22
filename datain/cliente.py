import requests
from requests.exceptions import HTTPError
from dotenv import load_dotenv
import os

# Cargar variables de entorno del archivo .env
load_dotenv()

class APIClient:
    def __init__(self, base_url=None, client_id=None, username=None, password=None):
        """
        Inicializa el cliente de la API.

        :param base_url: URL base de la API (p. ej. http://localhost:8000)
        :param client_id: ID del cliente
        :param username: Nombre de usuario para autenticación
        :param password: Contraseña para autenticación
        """
        self.base_url = base_url or os.getenv('BASE_URL')
        self.client_id = client_id or os.getenv('CLIENT_ID')
        self.username = username or os.getenv('USERNAME')
        self.password = password or os.getenv('PASSWORD')
        self.token = None

    def authenticate(self):
        """
        Autentica al usuario y obtiene el token de acceso.
        """
        url = f"{self.base_url}/token"
        data = {
            "client_id": self.client_id,
            "username": self.username,
            "password": self.password,
            "grant_type": "password"
        }

        try:
            response = requests.post(url, data=data)
            response.raise_for_status()  # Eleva una excepción para errores HTTP
            token_data = response.json()
            self.token = token_data["access_token"]
            return token_data
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"An error occurred: {err}")
        return None

    def get_headers(self):
        """
        Genera los encabezados de autorización usando el token JWT.
        """
        if not self.token:
            raise ValueError("Autenticación requerida. Llame al método 'authenticate' primero.")
        return {"Authorization": f"Bearer {self.token}"}

    def get_current_user(self):
        """
        Obtiene la información del usuario autenticado.
        """
        url = f"{self.base_url}/users/me/"
        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            return response.json()
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"An error occurred: {err}")
        return None

    def subscribe(self, subscription_data):
        """
        Envía una solicitud de suscripción.
        :param subscription_data: Diccionario con los datos de la suscripción.
        """
        url = f"{self.base_url}/subscribe"
        try:
            response = requests.post(url, json=subscription_data, headers=self.get_headers())
            response.raise_for_status()
            return response.json()
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"An error occurred: {err}")
        return None

    def unsubscribe(self, subscription_id):
        """
        Envía una solicitud de baja de una suscripción.
        :param subscription_id: ID de la suscripción a cancelar.
        """
        url = f"{self.base_url}/unsubscribe"
        data = {"id": subscription_id, "method": "unsubscribe"}
        try:
            response = requests.post(url, json=data, headers=self.get_headers())
            response.raise_for_status()
            return response.json()
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"An error occurred: {err}")
        return None

    def get_status(self):
        """
        Obtiene el estado del servicio.
        """
        url = f"{self.base_url}/status"
        try:
            response = requests.post(url, headers=self.get_headers())
            response.raise_for_status()
            return response.json()
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"An error occurred: {err}")
        return None

    def control_start(self):
        """
        Inicia el control mediante una solicitud GET a /control/start.
        """
        url = f"{self.base_url}/control/start"
        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            return response.json()
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"An error occurred: {err}")
        return None

    def control_stop(self):
        """
        Detiene el control mediante una solicitud GET a /control/stop.
        """
        url = f"{self.base_url}/control/stop"
        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            return response.json()
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"An error occurred: {err}")
        return None


# Ejemplo de uso
if __name__ == "__main__":
    client = APIClient()
    token_data = client.authenticate()
    if token_data:
        user_info = client.get_current_user()
        print("Información del usuario autenticado:", user_info)

        # Ejemplo de suscripción
        subscription_data = {"method": "subscribe", "id": "12345"}
        subscribe_response = client.subscribe(subscription_data)
        print("Respuesta de suscripción:", subscribe_response)

        # Ejemplo de baja de suscripción
        unsubscribe_response = client.unsubscribe("12345")
        print("Respuesta de baja:", unsubscribe_response)

        # Obtener el estado
        status_response = client.get_status()
        print("Estado del servicio:", status_response)

        # Iniciar control
        start_response = client.control_start()
        print("Control iniciado:", start_response)

        # Detener control
        stop_response = client.control_stop()
        print("Control detenido:", stop_response)

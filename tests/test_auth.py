import pytest
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = f"{os.environ['SERVER_SCHEMA']}://{os.environ['SERVER_HOST']}:{os.environ['SERVER_PORT']}"
LOGIN_ENDPOINT = "/token"
USER_INFO_ENDPOINT = "/users/me/"


@pytest.fixture
def client_credentials():
    """Proporciona las credenciales de inicio de sesión para las pruebas."""
    return {
        "client_id": "client",
        "username": "user_1",
        "password": "asd"
    }

def test_login(client_credentials):
    """Prueba el login y la obtención de un token JWT."""
    login_url = f"{BASE_URL}{LOGIN_ENDPOINT}"
    login_data = {
        "client_id": client_credentials["client_id"],
        "username": client_credentials["username"],
        "password": client_credentials["password"]
    }
    
    # Hacemos una solicitud POST para obtener el token de acceso
    response = requests.post(login_url, data=login_data)
    # Verificamos que el código de respuesta sea 200 (éxito)
    assert response.status_code == 200, "Login fallido"

    # Verificamos que el cuerpo de la respuesta contenga el token
    token = response.json().get("access_token")
    assert token is not None, "Token no recibido en la respuesta"
    
    # Usar el token para acceder a la información del usuario
    util_test_user_info(token, client_credentials)

def util_test_user_info(token, client_credentials):
    """Prueba el acceso a la información del usuario usando el token JWT."""
    user_info_url = f"{BASE_URL}{USER_INFO_ENDPOINT}"
    
    # Agregamos el token al encabezado de la solicitud
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Hacemos una solicitud GET al endpoint protegido
    response = requests.get(user_info_url, headers=headers)

    # Verificamos que la respuesta sea 200
    assert response.status_code == 200, "Falló la obtención de datos del usuario"

    # Verificamos que los datos de usuario coincidan
    user_data = response.json()
    assert user_data["usr"] == client_credentials["username"], "El nombre de usuario no coincide"
    assert user_data["client"] == client_credentials["client_id"], "El ID del cliente no coincide"
import pytest
import requests
from unittest.mock import patch
from datain.cliente import APIClient
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = f"{os.environ['SERVER_SCHEMA']}://{os.environ['SERVER_HOST']}:{os.environ['SERVER_PORT']}"
LOGIN_CLIENT = "client"
LOGIN_USER = "user_1"
LOGIN_PWD = "asd"


@pytest.fixture
def api_client():
    """
    Fixture que inicializa la clase APIClient.
    """
    client = APIClient( base_url=BASE_URL, client_id=LOGIN_CLIENT, username=LOGIN_USER, password=LOGIN_PWD)
    return client

@pytest.fixture
def mock_token_response():
    """
    Respuesta simulada para la autenticación.
    """
    return {
        "access_token": "mock_access_token",
        "token_type": "bearer"
    }

@pytest.fixture
def mock_user_info():
    """
    Datos simulados del usuario autenticado.
    """
    return {
        "usr": "test_user",
        "client": "test_client"
    }

@pytest.fixture
def mock_subscribe_response():
    """
    Respuesta simulada para la suscripción.
    """
    return {
        "status": 200,
        "id": "12345",
        "time": 1727006264257
    }

@pytest.fixture
def mock_status_response():
    """
    Respuesta simulada para el estado del servicio.
    """
    return {
        "status": 200,
        "up": True,
        "down": False,
        "uptime": True
    }

@pytest.fixture
def mock_control_response():
    """
    Respuesta simulada para los controles (start/stop).
    """
    return {
        "status": 200,
        "time": 1727006264257
    }

# Test para autenticación
@patch('requests.post')
def test_authenticate(mock_post, api_client, mock_token_response):
    """
    Test para la autenticación del cliente.
    """
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = mock_token_response

    token_data = api_client.authenticate()

    assert token_data["access_token"] == "mock_access_token"
    assert api_client.token == "mock_access_token"
    mock_post.assert_called_once_with(
        f"{api_client.base_url}/token",
        data={
            "client_id": api_client.client_id,
            "username": api_client.username,
            "password": api_client.password,
            "grant_type": "password"
        }
    )

# Test para obtener el usuario autenticado
@patch('requests.get')
def test_get_current_user(mock_get, api_client, mock_user_info):
    """
    Test para la obtención de los detalles del usuario autenticado.
    """
    api_client.token = "mock_access_token"
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_user_info

    user_info = api_client.get_current_user()

    assert user_info["usr"] == "test_user"
    assert user_info["client"] == "test_client"
    mock_get.assert_called_once_with(
        f"{api_client.base_url}/users/me/",
        headers={"Authorization": "Bearer mock_access_token"}
    )

# Test para la suscripción
@patch('requests.post')
def test_subscribe(mock_post, api_client, mock_subscribe_response):
    """
    Test para la suscripción del usuario.
    """
    api_client.token = "mock_access_token"
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = mock_subscribe_response

    subscription_data = {"method": "subscribe", "id": "12345"}
    response = api_client.subscribe(subscription_data)

    assert response["status"] == 200
    assert response["id"] == "12345"
    mock_post.assert_called_once_with(
        f"{api_client.base_url}/subscribe",
        json=subscription_data,
        headers={"Authorization": "Bearer mock_access_token"}
    )

# Test para la baja de suscripción
@patch('requests.post')
def test_unsubscribe(mock_post, api_client, mock_subscribe_response):
    """
    Test para la baja de suscripción del usuario.
    """
    api_client.token = "mock_access_token"
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = mock_subscribe_response

    subscription_id = "12345"
    response = api_client.unsubscribe(subscription_id)

    assert response["status"] == 200
    assert response["id"] == "12345"
    mock_post.assert_called_once_with(
        f"{api_client.base_url}/unsubscribe",
        json={"id": subscription_id, "method": "unsubscribe"},
        headers={"Authorization": "Bearer mock_access_token"}
    )

# Test para obtener el estado del servicio
@patch('requests.post')
def test_get_status(mock_post, api_client, mock_status_response):
    """
    Test para la obtención del estado del servicio.
    """
    api_client.token = "mock_access_token"
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = mock_status_response

    response = api_client.get_status()

    assert response["status"] == 200
    assert response["up"] is True
    mock_post.assert_called_once_with(
        f"{api_client.base_url}/status",
        headers={"Authorization": "Bearer mock_access_token"}
    )

# Test para iniciar control
@patch('requests.get')
def test_control_start(mock_get, api_client, mock_control_response):
    """
    Test para iniciar el control.
    """
    api_client.token = "mock_access_token"
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_control_response

    response = api_client.control_start()

    assert response["status"] == 200
    mock_get.assert_called_once_with(
        f"{api_client.base_url}/control/start",
        headers={"Authorization": "Bearer mock_access_token"}
    )

# Test para detener control
@patch('requests.get')
def test_control_stop(mock_get, api_client, mock_control_response):
    """
    Test para detener el control.
    """
    api_client.token = "mock_access_token"
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_control_response

    response = api_client.control_stop()

    assert response["status"] == 200
    mock_get.assert_called_once_with(
        f"{api_client.base_url}/control/stop",
        headers={"Authorization": "Bearer mock_access_token"}
    )
# APIClient - FastAPI Client with JWT Authentication

Este proyecto para conectarte con los websokets de distintos exchange, y unificar la obtencion de datos desde un solo websocket.
Ademas facilitar:
- la normalizacion de datos
- ordenar los inputs desde los websokets

## Requisitos

- Python 3.8+
- [Poetry](https://python-poetry.org/) para la gestión de dependencias

## Dependencias
- ccxt = "^4.3.98"
- websockets = "^13.0.1"
- websocket = "^0.2.1"
- binance-futures-connector = "^4.0.0"
- uvicorn = "^0.30.6"
- fastapi = "^0.114.0"
- rich = "^13.8.0"
- poetry-dotenv = "^0.4.0"
- pyjwt = "^2.9.0"
- passlib = {extras = ["bcrypt"], version = "^1.7.4"}
- python-multipart = "^0.0.10"
- pytest = "^8.3.3"
- load-dotenv = "^0.1.0"


## Instalación

### 1. Clona el repositorio

```bash
git clone https://github.com/tu_usuario/api-client.git
cd api-client
```

### 2. Configura las variables de entorno
Crea un archivo .env en la raíz del proyecto con la siguiente estructura:
```bash
# donde se montara el servidor 
SERVER_SCHEMA="http" 
SERVER_HOST="0.0.0.0"
SERVER_PORT="8880"

# se autoconecta los websockets
STREAM_IN_AUTOSTART="true"

# configuracion de la autentificacion
JWT_SECRET_KEY="09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
JWT_ALGORITHM="HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_CREDENTIALS='{"client":{"user_1":{"usr":"user_1","pwd":"asd"}}}'

```


### 3. Instala las dependencias
Usa Poetry para instalar las dependencias del proyecto:
```bash
poetry install
```


### 4. Activa el entorno virtual
Poetry crea un entorno virtual para el proyecto. Actívalo con el siguiente comando:
```bash
poetry shell
```

### 5. Ejecutar el servidor
Poetry crea un entorno virtual para el proyecto. Actívalo con el siguiente comando:
```bash
poetry run datain/server.py
```


## Uso Cliente

El cliente APIClient te permite interactuar con la API de [exchangedump/datain](https://github.com/exchangedump/datain). Aquí te mostramos algunos ejemplos de uso:

### 1. Autenticación
```python
from exchangedump.datain.cliente import APIClient

client = APIClient()
token = client.authenticate("http://0.0.0.0:8880", 'client', 'user', 'password')
print(token)
```

### 2. Obtener detalles del usuario autenticado
```python
user_info = client.get_current_user()
print(user_info)
```

### 3. Suscribirse a un servicio
```python
subscription_data = {"method": "subscribe", "id": "12345"}
response = client.subscribe(subscription_data)
print(response)
```

### 4. Cancelar una suscripción
```python
response = client.unsubscribe("12345")
print(response)
```

### 5. Obtener el estado del servicio
```python
status = client.get_status()
print(status)
```

### 6. Iniciar y detener control
```python
client.control_start()
client.control_stop()
```

### 7. Conectar al websocket

....@TODO

## Test
El proyecto utiliza pytest para las pruebas. Para ejecutar los tests:

### 1. Configura las variables de entorno

Antes de ejecutar los tests, asegúrate de que tienes configurado un archivo .env con las variables necesarias (ver sección de instalación).

### 2. Ejecuta los tests
```bash
pytest
```
Los tests simulan las respuestas de la API utilizando unittest.mock para realizar pruebas unitarias de las funcionalidades del cliente.

## API Endpoints
La API FastAPI que este cliente consume tiene los siguientes endpoints:

- **POST /token**: Autenticación para obtener un token JWT.
- **GET /users/me**/: Retorna la información del usuario autenticado.
- **POST /subscribe**: Suscripción a un servicio.
- **POST /unsubscribe**: Cancelación de una suscripción.
- **POST /status**: Obtiene el estado del servicio.
- **GET /control/start**: Inicia un proceso de control.
- **GET /control/stop**: Detiene un proceso de control.

## Contribuir
Si deseas contribuir a este proyecto:

- Haz un fork del repositorio.
- Crea una rama con una nueva funcionalidad (git checkout -b feature/nueva-funcionalidad).
- Haz commit de los cambios (git commit -m 'Añadir nueva funcionalidad').
- Haz push a la rama (git push origin feature/nueva-funcionalidad).
- Abre un Pull Request.

## Licencia

Libre en la vercion que mas te guste.
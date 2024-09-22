from datetime import datetime, timedelta, timezone
import os
import json
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from typing_extensions import Annotated
from passlib.context import CryptContext

from datain.webServer.models.response.auth import TokenData as TokenDataResponse
from datain.webServer.models.response.auth import User as UserResponse
from datain.webServer.models.response.auth import HTTPExceptionJWD



# openssl rand -hex 32
SECRET_KEY = os.environ['JWT_SECRET_KEY']
ALGORITHM = os.environ['JWT_ALGORITHM']
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ['JWT_ACCESS_TOKEN_EXPIRE_MINUTES'])

class UserManager():
    """
        Esta clase gestiona los usuarios y la autenticación básica.
    """

    # Un diccionario simulado que contiene información de usuarios (puede ser reemplazado por una base de datos real).
    _db = json.loads(os.environ['JWT_CREDENTIALS'])
    # {
    #     'pitzil': {
    #         'ale': {
    #             'usr': 'ale',
    #             'pwd': 'asd'
    #         }
    #     }
    # }
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def get_user(self, client: str, username: str) -> UserResponse | None:
        """
        Retorna un objeto UserResponse si el cliente y el usuario existen en la base de datos.

        Args:
            client (str): _description_
            username (str): _description_

        Returns:
            UserResponse | None: detalles del usuario si existe, None en caso contrario.
        """
        if client not in self._db:
            return None
        if username not in self._db[client]:
            return None
        user_dict = self._db[client][username]
        return UserResponse(usr=user_dict['usr'], client=client)
    
    def validate_user(self, client: str, username: str, password: str) -> bool:
        """
        Valida si un usuario y su contraseña son correctos comparando los datos almacenados en _db.

        Args:
            client (str): _description_
            username (str): _description_
            password (str): _description_

        Returns:
            bool: true si el usuario y la contraseña son correctos, false en caso contrario.
        """
        
        if client not in self._db:
            return False
        if username not in self._db[client]:
            return False

        return self.validate_pwd(password=password, hash=self._db[client][username]['pwd'])

    def validate_pwd(self, password: str, hash: str) -> bool:
        """
        Compara la contraseña proporcionada con el hash almacenado (por simplicidad, aquí no hay encriptación de contraseñas, lo cual sería recomendable).

        Args:
            password (str): _description_
            hash (str): _description_

        Returns:
            _type_: Si la contraseña es correcta, retorna True, de lo contrario False.
        """
        if password == hash:
            return True
        return False



class AuthManager():
    """
    Esta clase maneja la autenticación y la creación de tokens.
    """
    
    userManeger = UserManager()
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
    _time_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    def authenticate_user(self, client: str, username: str, password: str) -> bool:
        """
        authenticate_user: Verifica las credenciales del usuario utilizando UserManager.

        Args:
            client (str): _description_
            username (str): _description_
            password (str): _description_

        Returns:
            _type_: _description_
        """
        return self.userManeger.validate_user(client, username, password)

    def generate_access_token(self, client: str, username: str) -> str:
        """
        Crea y devuelve un token JWT con los datos de usuario (como username, client) y una fecha de expiración.

        Args:
            data (dict): _description_

        Returns:
            _type_: _description_
        """

        user = self.userManeger.get_user(client=client, username=username)
        
        data = {
            "client": user.client, 
            "sub": user.usr,
            "unique": user.usr
        }

        return self.create_access_token(data=data)

    def create_access_token(self, data: dict) -> str:
        """
        Crea y devuelve un token JWT con los datos de usuario (como username, client) y una fecha de expiración.

        Args:
            data (dict): _description_

        Returns:
            _type_: _description_
        """
        
        to_encode = data.copy()

        expire = datetime.now(timezone.utc) + self._time_token_expires
        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(AuthManager.oauth2_scheme)]):
    """
    Valida el token JWT y extrae el username y client del payload. Si el token es inválido o los datos no son válidos, lanza una excepción personalizada HTTPExceptionJWD.

    Args:
        token (Annotated[str, Depends): _description_

    Raises:
        credentials_exception: _description_
        credentials_exception: _description_
        credentials_exception: _description_

    Returns:
        _type_: _description_
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        client: str = payload.get("client")
        if username is None:
            raise HTTPExceptionJWD(detail="Could not validate credentials")
        token_data = TokenDataResponse(username=username)
    except InvalidTokenError:
        raise HTTPExceptionJWD(detail="Error current user")

    user = AuthManager.userManeger.get_user(client=client, username=username)

    if user is None:
        raise HTTPExceptionJWD(detail="Could not validate credentials")
    return user

async def is_active( current_user: Annotated[UserResponse, Depends(get_current_user)] ):
    """
    Valida que el usuario esté activo y retorna la información del mismo.

    Args:
        current_user (Annotated[UserResponse, Depends): _description_

    Returns:
        _type_: _description_
    """
    return current_user
from datain.webServer.utils.BaseWebServer import BaseWebServer
from typing_extensions import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from datain.webServer.utils.authUtils import AuthManager, is_active

from datain.webServer.models.response.auth import Token as TokenResponse
from datain.webServer.models.response.auth import User as UserResponse
from datain.webServer.models.response.auth import HTTPExceptionJWD

class auth(BaseWebServer):
    
    def __init__(self) -> None:
        super().__init__()
        
        self.authManager = AuthManager()

        @self.router.post("/token")
        async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> TokenResponse:
            """
            
            Ruta para autenticar usuarios, valida las credenciales y devuelve un token de acceso.

            Args:
                form_data (Annotated[OAuth2PasswordRequestForm, Depends): _description_

            Raises:
                HTTPExceptionJWD: _description_

            Returns:
                TokenResponse: _description_
            """
            
            valid_auth = self.authManager.authenticate_user(form_data.client_id, form_data.username, form_data.password)
            if not valid_auth:
                raise HTTPExceptionJWD(detail="Incorrect username or password")
            
            access_token = self.authManager.generate_access_token(form_data.client_id, form_data.username)
            
            return TokenResponse(
                access_token=access_token,
                token_type="bearer"
            )
        
        @self.router.get("/users/me/", response_model=UserResponse)
        async def read_users_me( current_user: Annotated[UserResponse, Depends(is_active)],):
            """
            Retorna los detalles del usuario autenticado.

            Args:
                current_user (Annotated[UserResponse, Depends): _description_

            Returns:
                _type_: _description_
            """
            return current_user













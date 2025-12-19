from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from typing import Optional
from app.config.security import verify_token, verify_token_payload
from app.modules.auth.schemas.login import LoginRequest, LoginResponse
from app.modules.auth.services.auth_service import AuthService

auth_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
http_bearer = HTTPBearer(auto_error=False)

@auth_router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest):
    try:
        service = await AuthService.build()
        return await service.login(payload.email, payload.password, payload.remember_me)
    except ValueError:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno de autenticación")

async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    subject = verify_token(token)
    if subject is None:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    return subject

async def get_current_user_id_optional(credentials = Depends(http_bearer)) -> Optional[str]:
    if not credentials:
        return None
    try:
        return verify_token(credentials.credentials)
    except Exception:
        return None

@auth_router.get("/me")
async def me(user_id: str = Depends(get_current_user_id)):
    try:
        service = await AuthService.build()
        return await service.get_user_public_by_id(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno")

@auth_router.post("/refresh")
async def refresh_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = verify_token_payload(token)
        if payload is None:
            raise HTTPException(status_code=401, detail="Token inválido o expirado")
        user_id = payload.get("sub")
        remember_me = bool(payload.get("rm", False))
        service = await AuthService.build()
        return await service.refresh_token(user_id, remember_me=remember_me)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno")



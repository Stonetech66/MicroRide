from fastapi import Depends,  HTTPException
from fastapi_jwt_auth import AuthJWT
from fastapi.security import HTTPBearer
from .crud import UserCrud
from .database import database

async def get_current_user(Authorization=Depends(HTTPBearer()),Authorize:AuthJWT=Depends(),):
    exception=HTTPException(status_code=401, detail='invalid access token or access token has expired', headers={'WWW-Authenticate': 'Bearer'})
    try:
        Authorize.jwt_required()
        user_id=Authorize.get_jwt_subject()
        user= await UserCrud.get_user_by_id(database, user_id)
        return user
    except:
        raise exception

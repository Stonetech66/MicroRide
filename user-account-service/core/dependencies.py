from fastapi import Depends,  HTTPException
from fastapi_jwt_auth import AuthJWT
from fastapi.security import HTTPBearer
from .crud import UserCrud
from .database import database


# Function to get the current user based on the Authorization token
async def get_current_user(Authorization=Depends(HTTPBearer()),Jwt:AuthJWT=Depends(),):
    exception=HTTPException(status_code=401, detail='invalid or expired access token', headers={'WWW-Authenticate': 'Bearer'})
    try:
        Jwt.jwt_required()
        user_id=Jwt.get_jwt_subject()
        user= await UserCrud.get_user_by_id(database, user_id)
        return user
    except:
        raise exception

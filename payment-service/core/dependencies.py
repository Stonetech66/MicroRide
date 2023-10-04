from fastapi import Depends,  HTTPException
from fastapi.security import HTTPBearer
from fastapi_jwt_auth import AuthJWT



# Function to get the current user based on the Authorization token
async def get_current_user(Authorization=Depends(HTTPBearer()),Jwt:AuthJWT=Depends(),):
    exception=HTTPException(status_code=401, detail='invalid or expired access token', headers={'WWW-Authenticate': 'Bearer'})
    try:
        Jwt.jwt_required()
        user_id=Jwt.get_jwt_subject()
        return user_id
    except:
        raise exception

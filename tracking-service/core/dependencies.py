from fastapi import Depends,  HTTPException
from fastapi.security import HTTPBearer
from .database import driver_collection
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

   

# Function to check if the user is a registered driver
async def get_user_is_registered_driver(user_id=Depends(get_current_user), ):
    # Define exception to handle unauthorized access
    exception=HTTPException(detail='user is not a driver', status_code=403)

    # Check if the user is a registered driver in the database
    driver= await driver_collection.find_one({'user_id':user_id})
    if not driver:
        raise exception
    return driver['id']
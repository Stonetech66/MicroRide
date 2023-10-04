from fastapi import Depends,  HTTPException
from fastapi.security import HTTPBearer
import os
from .database import database
from .models import Driver
from sqlalchemy import select
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
    exception=HTTPException(detail='user is not signed up as a driver', status_code=400)

    # Check if the user is a registered driver in the database
    query= select(Driver).where(Driver.c.user_id==user_id)
    driver=await database.fetch_one(query)
    if not driver:
        raise exception
    return driver


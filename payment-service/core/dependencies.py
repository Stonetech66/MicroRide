from fastapi import Depends,  HTTPException
from fastapi.security import HTTPBearer
import aiohttp
import asyncio
import json
import aioredis
from datetime import datetime, timezone
import os

AUTH_URL= os.getenv('VERIFY_TOKEN_URL')
REDIS_HOST=os.getenv('REDIS_HOST')
REDIS_URL= f'redis://{REDIS_HOST}'

# Function to validate token by checking if it`s stored in Redis
async def validate_token_is_in_redis(redis, token):
    jwt=await redis.get(f'auth-{token}')
    if jwt:
        data=json.loads(jwt)
        return data['user_id']
    return None
    
# Function to get the current user based on the Authorization token
async def get_current_user(Authorization=Depends(HTTPBearer()), ):
    exception=HTTPException(
        status_code=401, 
        detail='invalid or expired access token', 
        headers={'WWW-Authenticate': 'Bearer'}
        )

    # Connect to Redis
    redis= await  aioredis.from_url(REDIS_URL, decode_responses=True)

    try:
        # Attempt to validate the token is stored in redis
        user_id=await validate_token_is_in_redis(redis, Authorization.credentials)
        if user_id:
            return user_id
        
        # If not found in Redis, validate the token with the authentication service
        async with aiohttp.ClientSession() as session:
            async with session.post(
                AUTH_URL, 
                headers={'Authorization':f'{Authorization.scheme} {Authorization.credentials}'}
                )as response:
                status_code = response.status
                if status_code == 200:
                    data= await response.json()
                    expiry=data['exp'] -  int(datetime.now(timezone.utc).timestamp())
                    await redis.set(f'auth-{Authorization.credentials}',json.dumps(data), ex= expiry)
                    return data['user_id']
                raise exception
    except aiohttp.ClientResponseError as e:
        raise exception
    except asyncio.TimeoutError:
        raise HTTPException(status_code=500, detail='server error an error occured', headers={'WWW-Authenticate': 'Bearer'})
   
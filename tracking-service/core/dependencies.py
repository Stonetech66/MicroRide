from fastapi import Depends,  HTTPException, Header, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer
import aiohttp
import asyncio
import json
import aioredis
from datetime import datetime, timezone

import os

USER_ACCOUNT_SERVICE= os.getenv('USER_ACCOUNT_SERVICE_URL')
AUTH_URL= f'{USER_ACCOUNT_SERVICE}/verify-token'
REDIS_URL= os.getenv('REDIS_URL')

async def validate_token_in_redis(redis, token):
    jwt=await redis.get(f'auth-{token}')
    if jwt:
        data=json.loads(jwt)
        return data['user_id']
    return None
    


async def get_current_user(Authorization=Depends(HTTPBearer()), ):
    exception=HTTPException(status_code=401, detail='invalid access token or access token has expired', headers={'WWW-Authenticate': 'Bearer'})
    redis= await  aioredis.from_url(REDIS_URL, decode_responses=True)
    try:
        user_id=await validate_token_in_redis(redis, Authorization.credentials)
        if user_id:
            return user_id
        async with aiohttp.ClientSession() as session:
            async with session.post(AUTH_URL, headers={'Authorization':f'{Authorization.scheme} {Authorization.credentials}'})as response:
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
   


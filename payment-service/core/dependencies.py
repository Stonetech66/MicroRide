from fastapi import Depends,  HTTPException, Header
from fastapi.security import HTTPBearer
import aiohttp
import asyncio

AUTH_URL= 'http://localhost:8001/verify-token'

async def get_current_user(Authorization=Depends(HTTPBearer()), ):
    exception=HTTPException(status_code=401, detail='invalid access token or access token has expired', headers={'WWW-Authenticate': 'Bearer'})
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(AUTH_URL, headers={'Authorization':f'{Authorization.scheme} {Authorization.credentials}'})as response:
                status_code = response.status
                if status_code == 200:
                    user_id= await response.json()
                    return user_id['user_id']
                raise exception
    except aiohttp.ClientResponseError as e:
        raise exception
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'server error an error occured', headers={'WWW-Authenticate': 'Bearer'})
    

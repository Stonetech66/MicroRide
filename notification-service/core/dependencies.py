from fastapi import Depends,  HTTPException, WebSocket, WebSocketDisconnect
import aiohttp
import json
import aioredis
from datetime import datetime, timezone
from .database import driver_table
from .websockets import WebsocketManager
import os

USER_ACCOUNT_SERVICE= os.getenv('USER_ACCOUNT_SERVICE_URL')
AUTH_URL= f'{USER_ACCOUNT_SERVICE}/verify-token'
REDIS_URL= os.getenv('REDIS_URL')

connections= WebsocketManager()



async def validate_credentials_auth_service(redis, token):
    async with aiohttp.ClientSession() as session:
        async with session.post(AUTH_URL, headers={'Authorization':f'Bearer {token}'})as response:
            status_code = response.status
            if status_code == 200:
                data= await response.json()
                expiry=data['exp'] -  int(datetime.now(timezone.utc).timestamp())
                await redis.set(f'auth-{token}',json.dumps(data), ex= expiry)
                user_id=str(data['user_id'])
                return user_id


async def get_current_websocket_user(token:str,websocket:WebSocket, type:str=None):
    exception=HTTPException(status_code=401, detail='invalid access token or access token has expired', headers={'WWW-Authenticate': 'Bearer'})
    err_msg= {'message':'invalid or expired access token ', 'status_code':401}
    global connections
    try:
        await websocket.accept()
        if type == 'server':
            if await connections.validate_token_from_server(token):
                data=await websocket.receive_json()
                user_id= str(data['user_id'])
                await connections.send_message_user(user_id, data)
                return websocket
            else:
                await websocket.send_json(err_msg)
                await websocket.close()
                raise exception

        else:
            redis= await  aioredis.from_url(REDIS_URL, decode_responses=True)
            user_id=await connections.validate_token_in_redis(redis, token)
            if user_id:
                await connections.connect_user(websocket, user_id)
                return websocket
            user_id= await validate_credentials_auth_service(redis, token)
            if user_id:
                await connections.connect_user(websocket, user_id)
                return websocket
            await websocket.send_json(err_msg)
            await websocket.close()
            raise exception
    except WebSocketDisconnect:
        await connections.disconnect_user(websocket, user_id)
        pass


async def get_current_websocket_driver(token:str,websocket:WebSocket, type:str=None):
    exception=HTTPException(status_code=401, detail='invalid access token or access token has expired', headers={'WWW-Authenticate': 'Bearer'})
    err_msg= {'message':'invalid or expired access token ', 'status_code':401}
    global connections
    try:
        await websocket.accept()
        if type == 'server':
            if await connections.validate_token_from_server(token):
                data=await websocket.receive_json()
                user_id, driver_id= str(data['user_id']), str(data['driver_id'])
                await connections.send_message_driver( driver_id, data)
                return websocket
            else:
                await websocket.send_json({'message':'error'})
                await websocket.close()
                raise exception

        else:
            redis= await  aioredis.from_url(REDIS_URL, decode_responses=True)
            user_id=await connections.validate_token_in_redis(redis, token)
            if user_id:
                driver=await driver_table.find_one({'user_id':user_id})
                if driver:
                    await connections.connect_driver(websocket, driver['id'])
                    return websocket
                await websocket.send_json({'message':'you are not registered as a driver', 'status_code':403})
                await websocket.close()
                return 
            user_id= await validate_credentials_auth_service(redis, token)
            if user_id:
                driver=await driver_table.find_one({'user_id':user_id})
                if not driver:
                    await websocket.send_json({'message':'you are not registered as a driver', 'status_code':403})
                    await websocket.close()
                    return 
                await connections.connect_driver(websocket, driver['id'])
                return websocket
            await websocket.send_json(err_msg)
            await websocket.close()
            return 
    except WebSocketDisconnect:
        await connections.disconnect_driver(websocket, user_id)


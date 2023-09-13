from fastapi import Depends,  HTTPException, WebSocket, WebSocketDisconnect
import aiohttp
import json
import aioredis
from datetime import datetime, timezone
from .database import driver_collection
from .websockets import WebsocketManager
import os



# Authentication service URL and Redis configuration
AUTH_URL= os.getenv('VERIFY_TOKEN_URL')
REDIS_HOST=os.getenv('REDIS_HOST')
REDIS_URL= f'redis://{REDIS_HOST}'

connections= WebsocketManager()


# Function to validate JWT token from the authentication service
async def validate_credentials_auth_service(redis, token):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            AUTH_URL, 
            headers={'Authorization':f'Bearer {token}'}
            )as response:
            status_code = response.status
            if status_code == 200:
                data= await response.json()
                expiry=data['exp'] -  int(datetime.now(timezone.utc).timestamp())
                await redis.set(f'auth-{token}',json.dumps(data), ex= expiry)
                user_id=str(data['user_id'])
                return user_id

# Function to get the current user from a Websocket connnection
async def get_current_websocket_user(token:str,websocket:WebSocket, type:str=None):
    err_msg= {'msg':'invalid or expired access token ', 'status_code':401}
    global connections
    try:
        await websocket.accept()
        # If the connection is from a micro-service and the token is valid
        if type == 'server':
            if await connections.validate_token_from_server(token):
                data=await websocket.receive_json()
                user_id= str(data['user_id'])

                # Send the data/event to the user Websocket connection
                await connections.send_message_user(user_id, data)
                return websocket
            
            # If the token isn`t valid, send an error message and close the Websocket connection
            else:
                await websocket.send_json(err_msg)
                await websocket.close()
                return
            
        # If the connection is from a user and not from a micro-service
        else:
            # Connect to Redis
            redis= await  aioredis.from_url(REDIS_URL, decode_responses=True)

            # Validate the user JWT token is stored in Redis and valid, then connect the user
            user_id=await connections.validate_token_is_in_redis(redis, token)
            if user_id:
                await connections.connect_user(websocket, user_id, redis)
                return websocket
            
            # Else validate the JWT token with the authentication service
            user_id= await validate_credentials_auth_service(redis, token)
            
            # If the JWT token is valid, then connect the user
            if user_id:
                await connections.connect_user(websocket, user_id, redis)
                return websocket
            
            # Else,  send an error message 'invalid or expired token' and close the Websocket connection
            await websocket.send_json(err_msg)
            await websocket.close()
            return
    except WebSocketDisconnect:
        await connections.disconnect_user(websocket, user_id)
        pass

# Function to get current driver from a Websocket connnection
async def get_current_websocket_driver(token:str,websocket:WebSocket, type:str=None):
    err_msg= {'msg':'invalid or expired access token ', 'status_code':401}
    global connections
    try:
        await websocket.accept()
        # If the connection is from a micro-service and the token is valid
        if type == 'server':
            if await connections.validate_token_from_server(token):
                data=await websocket.receive_json()
                user_id, driver_id= str(data['user_id']), str(data['driver_id'])

                # Send the data/event to the driver Websocket connection
                await connections.send_message_driver( driver_id, data)
                return websocket
            
            # If the token isn`t valid, send an error message and close the Websocket connection
            else:
                await websocket.send_json({'msg':'error'})
                await websocket.close()
                return
        
        # If the connection is from a driver and not from a micro-service
        else:
            # Connect to Redis
            redis= await  aioredis.from_url(REDIS_URL, decode_responses=True)
            
            # Validate the JWT token is stored in Redis and valid 
            user_id=await connections.validate_token_is_in_redis(redis, token)
            if user_id:
                # Retrieve the driver from the database
                driver=await driver_collection.find_one({'user_id':user_id}, projection={'id':1, '_id':0})
                if driver:
                    # If the driver exists connect the driver 
                    await connections.connect_driver(websocket, driver['id'], redis)
                    return websocket
                
                # Else send an error message to the user and close websocket connnection
                await websocket.send_json({'msg':'user not registered as a driver', 'status_code':403})
                await websocket.close()
                return 
            
            # Else validate the JWT token with the authentication service
            user_id= await validate_credentials_auth_service(redis, token)
            if user_id:
                # Retrieve the driver from the database
                driver=await driver_collection.find_one({'user_id':user_id},projection={'id':1})
                if not driver:
                    # If the driver dosen`t exists send an error message and close the websocket connection
                    await websocket.send_json({'msg':'user not registered as a driver', 'status_code':403})
                    await websocket.close()
                    return 
                # Else connect the driver
                await connections.connect_driver(websocket, driver['id'], redis)
                return websocket
            await websocket.send_json(err_msg)
            await websocket.close()
            return 
    except WebSocketDisconnect:
        await connections.disconnect_driver(websocket, user_id)


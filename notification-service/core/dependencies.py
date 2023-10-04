from fastapi import Depends,  HTTPException, WebSocket, WebSocketDisconnect
import aioredis
from .database import driver_collection
from .websockets import websocket_manager
import os
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException


# Authentication service URL and Redis configuration
REDIS_HOST=os.getenv('REDIS_HOST')
REDIS_URL= f'redis://{REDIS_HOST}'





# Function to get the current user from a Websocket connnection
async def get_current_websocket_user(token:str,websocket:WebSocket, type:str=None, Jwt:AuthJWT=Depends()):
    err_msg= {'msg':'invalid or expired access token ', 'status_code':401}
    try:
        await websocket.accept()
        # If the connection is from a micro-service and the token is valid
        if type == 'server':
            if await websocket_manager.validate_token_from_server(token):
                data=await websocket.receive_json()
                user_id= str(data['user_id'])

                # Send the data/event to the user Websocket connection
                await websocket_manager.send_message_user(user_id, data)
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

            try:
                Jwt.jwt_required('websocket', token=token)
                user_id=Jwt.get_raw_jwt(token)['sub']
                await websocket_manager.connect_user(websocket, user_id, redis)
                return websocket
            except AuthJWTException:
                await websocket.send_json(err_msg)
                await websocket.close()
                return
    except WebSocketDisconnect:
        await websocket_manager.disconnect_user(websocket, user_id)
        pass

# Function to get current driver from a Websocket connnection
async def get_current_websocket_driver(token:str,websocket:WebSocket, type:str=None,  Jwt:AuthJWT=Depends()):
    err_msg= {'msg':'invalid or expired access token ', 'status_code':401}
    try:
        await websocket.accept()
        # If the connection is from a micro-service and the token is valid
        if type == 'server':
            if await websocket_manager.validate_token_from_server(token):
                data=await websocket.receive_json()
                user_id, driver_id= str(data['user_id']), str(data['driver_id'])

                # Send the data/event to the driver Websocket connection
                await websocket_manager.send_message_driver( driver_id, data)
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
            try:
                Jwt.jwt_required('websocket', token=token)
                user_id=Jwt.get_raw_jwt(token)['sub']
                # Retrieve the driver from the database
                driver=await driver_collection.find_one({'user_id':user_id}, projection={'id':1, '_id':0})
                if driver:
                    # If the driver exists connect the driver 
                    await websocket_manager.connect_driver(websocket, driver['id'], redis)
                    return websocket
                
                # Else send an error message to the user and close websocket connnection
                await websocket.send_json({'msg':'user not registered as a driver', 'status_code':403})
                await websocket.close()
                return 
            except AuthJWTException:
                await websocket.send_json(err_msg)
                await websocket.close()
                return 
    except WebSocketDisconnect:
        await websocket_manager.disconnect_driver(websocket, user_id)


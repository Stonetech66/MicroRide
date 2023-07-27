import websockets
import json 
import os
from fastapi import WebSocket
from .utils import update_user_websocket_event, update_driver_websocket_event

NOTIFICATION_SERVICE_HOST=os.getenv('NOTIFICATION_SERVICE_HOST')

WEBSOCKET_SECRET_KEY=os.getenv('WEBSOCKET_SECRET_KEY')


class WebsocketManager :

    def __init__(self) -> None:
        self.user_connections={}
        self.driver_connections={}
        
    async def connect_user(self, websocket:WebSocket,user_id:str, redis):
        self.user_connections.update({user_id:websocket})
        await websocket.send_json({'message':'connected', 'status_code':200})
        current_data= await redis.get(f'user-current-websocket-data-{user_id}')
        if current_data:
            await websocket.send_json(json.loads(current_data))
    
    async def connect_driver(self, websocket:WebSocket,driver_id:str, redis):
        self.driver_connections.update({driver_id:websocket})
        await websocket.send_json({'message':'connected', 'status_code':200})
        current_data= await redis.get(f'driver-current-websocket-data-{driver_id}')
        if current_data:
            await websocket.send_json(json.loads(current_data))

    async def disconnect_user(self, websocket, user_id):
        await websocket.close()
        self.user_connections.pop(user_id)

    async def disconnect_driver(self, websocket, driver_id):
        await websocket.close()
        self.driver_connections.pop(driver_id)

    async def send_message_user(self, user_id,  data):
        connection=self.user_connections.get(user_id)
        if connection:
            await connection.send_json(data)

    async def send_message_driver(self, driver_id,data):
        connection=self.driver_connections.get(driver_id)
        if connection:
            await connection.send_json(data)

    @staticmethod
    async def validate_token_from_server(token):
        if token == WEBSOCKET_SECRET_KEY:
            return True 
        return False
    
    @staticmethod
    async def validate_token_in_redis(redis, token):
        jwt=await redis.get(f'auth-{token}')
        if jwt:
            data=json.loads(jwt)
            return data['user_id']
        return None



async def send_user_websocket_data(user_id, event, data, redis):
        data.update({'event':event})
        async with websockets.connect(f'ws://{NOTIFICATION_SERVICE_HOST}/api/v1/ws/user/?token={WEBSOCKET_SECRET_KEY}&type=server') as websocket:
            await websocket.send(json.dumps(data))
        await update_user_websocket_event(redis, data, user_id)


async def send_driver_websocket_data( driver_id, event, data, redis,):
        data.update({'event':event})
        async with websockets.connect(f'ws://{NOTIFICATION_SERVICE_HOST}/api/v1/ws/driver/?token={WEBSOCKET_SECRET_KEY}&type=server') as websocket:
            await websocket.send(json.dumps(data))
        await update_driver_websocket_event(redis, data, driver_id)
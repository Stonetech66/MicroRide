import websockets
import json 
import os
from fastapi import WebSocket

NOTIFICATION_SERVICE_URL=os.getenv('NOTIFICATION_SERVICE_URL')

WEBSOCKET_SECRET_KEY=os.getenv('WEBSOCKET_SECRET_KEY', 'secret')


class WebsocketManager :

    def __init__(self) -> None:
        self.user_connections={}
        self.driver_connections={}
        
    async def connect_user(self, websocket:WebSocket,user_id:str, ):
        self.user_connections.update({user_id:websocket})
        await websocket.send_json({'message':'connected', 'status_code':200})
    
    async def connect_driver(self, websocket:WebSocket,driver_id:str, ):
        self.driver_connections.update({driver_id:websocket})
        await websocket.send_json({'message':'connected', 'status_code':200})

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



async def send_user_websocket_data(user_id, event, data):
        data.update({'event':event})
        async with websockets.connect(NOTIFICATION_SERVICE_URL+f'/ws/ride/?token={WEBSOCKET_SECRET_KEY}&type=server') as websocket:
            await websocket.send(json.dumps(data))


async def send_driver_websocket_data(driver_id, event, data):
        data.update({'event':event})
        async with websockets.connect(NOTIFICATION_SERVICE_URL+f'/ws/driver/?token={WEBSOCKET_SECRET_KEY}&type=server') as websocket:
            await websocket.send(json.dumps(data))
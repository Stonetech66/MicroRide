import websockets
import json 
import os
from fastapi import WebSocket


# Get the host of the notification service from the environmental variables
NOTIFICATION_SERVICE_HOST=os.getenv('NOTIFICATION_SERVICE_HOST')

# Get the Websocket secret key from the environmental variables
WEBSOCKET_SECRET_KEY=os.getenv('WEBSOCKET_SECRET_KEY')


class WebsocketManager :

    def __init__(self) -> None:
        # Initialize dictionaries to store user and driver websocket connections
        self.user_connections={}
        self.driver_connections={}
        
    async def connect_user(self, websocket:WebSocket,user_id:str, redis):
        # Store the user`s websocket connection
        self.user_connections.update({user_id:websocket})
        await websocket.send_json({'msg':'connected', 'status_code':200, 'user_id':user_id})
        
        # Send any current stored data from Redis to the user
        current_data= await redis.get(f'user-current-websocket-data-{user_id}')
        if current_data:
            await websocket.send_json(json.loads(current_data))
    
    async def connect_driver(self, websocket:WebSocket,driver_id:str, redis):
        # Store the driver`s websocket connection
        self.driver_connections.update({driver_id:websocket})
        await websocket.send_json({'msg':'connected', 'status_code':200, 'driver_id':driver_id})
        
        # Send any current stored data from Redis to the driver
        current_data= await redis.get(f'driver-current-websocket-data-{driver_id}')
        if current_data:
            await websocket.send_json(json.loads(current_data))

    async def disconnect_user(self, websocket, user_id):
        # Close the user`s websocket connection and remove it from the dictionary store
        await websocket.close()
        self.user_connections.pop(user_id)

    async def disconnect_driver(self, websocket, driver_id):
        # Close the driver`s websocket connection and remove it from the dictionary store
        await websocket.close()
        self.driver_connections.pop(driver_id)

    async def send_message_user(self, user_id,  data):
        # Send a message to the user`s websocket connection if it exists
        connection=self.user_connections.get(user_id)
        if connection:
            await connection.send_json(data)

    async def send_message_driver(self, driver_id,data):
        # Send a message to the driver`s websocket connection if it exists
        connection=self.driver_connections.get(driver_id)
        if connection:
            await connection.send_json(data)

    @staticmethod
    async def validate_token_from_server(token):
        # Validate the token against the Websocket Secret Key
        if token == WEBSOCKET_SECRET_KEY:
            return True 
        return False
    
    @staticmethod
    async def validate_token_is_in_redis(redis, token):
        # Validate the token by checking if it`s in Redis
        jwt=await redis.get(f'auth-{token}')
        if jwt:
            data=json.loads(jwt)
            return data['user_id']
        return None
    
    async def update_user_websocket_event(self, redis, data, user_id):
        #  Update user`s stored cached data in Redis
        await redis.set(f'user-current-websocket-data-{user_id}', data)

    async def delete_user_websocket_event(self, redis,user_id):
        #  Delete user`s stored cached data in Redis
        await redis.delete(f'user-current-websocket-data-{user_id}')

    async def update_driver_websocket_event(self, redis, data, driver_id):
        #  Update driver`s stored cached data in Redis
        await redis.set(f'driver-current-websocket-data-{driver_id}', data)

    async def delete_driver_websocket_event(self, redis, driver_id):
        #  Delete driver`s stored cached data in Redis
        await redis.delete(f'driver-current-websocket-data-{driver_id}')

    async def send_user_websocket_data(self,user_id, event, data, redis, update_cache_data=False, clear_cache_data=False):
            # Send data to a user`s websocket connnection and optionally update or clear cache data
            data.update({'event':event})
            data= json.dumps(data)
            async with websockets.connect(f'ws://{NOTIFICATION_SERVICE_HOST}/api/v1/ws/user/?token={WEBSOCKET_SECRET_KEY}&type=server') as websocket:
                await websocket.send(data)
            if update_cache_data:
               await  self.update_user_websocket_event(redis, data, user_id)
            elif clear_cache_data:
               await self.delete_user_websocket_event(redis, user_id)


    async def send_driver_websocket_data(self, driver_id, event, data, redis, update_cache_data=False, clear_cache_data=False):
            # Send data to a driver`s websocket connnection and optionally update or clear cache data
            data.update({'event':event})
            data= json.dumps(data)
            async with websockets.connect(f'ws://{NOTIFICATION_SERVICE_HOST}/api/v1/ws/driver/?token={WEBSOCKET_SECRET_KEY}&type=server') as websocket:
                await websocket.send(data)
            if update_cache_data:
                await  self.update_driver_websocket_event(redis, data, driver_id)
            elif clear_cache_data:
               await self.delete_driver_websocket_event(redis, driver_id)
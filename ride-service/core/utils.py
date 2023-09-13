import random 
import os
import json
import websockets

NOTIFICATION_SERVICE_HOST=os.getenv('NOTIFICATION_SERVICE_HOST')
WEBSOCKET_SECRET_KEY=os.getenv('WEBSOCKET_SECRET_KEY')
REDIS_HOST= os.getenv('REDIS_HOST')


# sample function to get random fare when a ride is canceled
def get_ride_canceled_fare():
    fares=(100, 200, 500, 700)
    return random.choice(fares)

# Function to send websocket data to a user
async def send_websocket_data(user_id, data):
        ws=f'ws://{NOTIFICATION_SERVICE_HOST}/api/v1/ws/user/?type=server&token={WEBSOCKET_SECRET_KEY}'
        async with websockets.connect(ws) as websocket:
            await websocket.send(json.dumps(data))
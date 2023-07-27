import json

async def update_user_websocket_event(redis, data, user_id):
    data=json.dumps(data)
    await redis.set(f'user-current-websocket-data-{user_id}', data)

async def update_driver_websocket_event(redis, data, driver_id):
    data=json.dumps(data)
    await redis.set(f'driver-current-websocket-data-{driver_id}', data)
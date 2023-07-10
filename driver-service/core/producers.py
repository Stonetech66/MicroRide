import json
from aio_pika import connect, ExchangeType, Message


connection= None
async def get_connection():
    global connection
    connection= await connect('amqp://guest:guest@localhost/')
    return connection

async def get_channel():
    global connection
    if not connection:
        connection= await get_connection()
    channel= await connection.channel()
    return channel



async def publish_driver_created(driver_data:dict):
    channel= await get_channel()
    ride_events= await channel.declare_exchange('driver-events', ExchangeType.TOPIC,)
    await ride_events.publish(Message(json.dumps(driver_data).encode()), routing_key='driver.created')




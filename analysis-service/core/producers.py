import json
from aio_pika import connect, ExchangeType, Message
import os
RABBITMQ_URL= os.getenv('RABBITMQ_URL')

connection= None
async def get_connection():
    global connection
    connection= await connect(RABBITMQ_URL)
    return connection

async def get_channel():
    global connection
    if not connection:
        connection= await get_connection()
    channel= await connection.channel()
    return channel



async def publish_ride_fare_calculated(channel, ride_data:dict):
    analysis_events= await channel.declare_exchange('analysis-events', ExchangeType.TOPIC)
    await analysis_events.publish(Message(json.dumps(ride_data).encode()), routing_key='analysis.ride.fare')




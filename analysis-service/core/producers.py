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



async def publish_ride_fare_calculated(channel, ride_data:dict):
    analysis_events= await channel.declare_exchange('analysis-events', ExchangeType.TOPIC)
    await analysis_events.publish(Message(json.dumps(ride_data).encode()), routing_key='analysis.ride.fare')




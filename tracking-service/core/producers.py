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



async def publish_driver_arrived(ride_data:dict):
    channel= await get_channel()
    ride_events= await channel.declare_exchange('tracking-events', ExchangeType.TOPIC,)
    await ride_events.publish(Message(json.dumps(ride_data).encode()), routing_key='tracking.ride.arrived')

async def publish_ride_in_transit(ride_data:dict):
    channel= await get_channel()
    ride_events= await channel.declare_exchange('tracking-events', ExchangeType.TOPIC,)
    await ride_events.publish(Message(json.dumps(ride_data).encode()), routing_key='tracking.ride.in_transit')

async def publish_ride_completed(ride_data:dict):
    channel= await get_channel()
    ride_events= await channel.declare_exchange('tracking-events', ExchangeType.TOPIC,)
    await ride_events.publish(Message(json.dumps(ride_data).encode()), routing_key='tracking.ride.completed')

async def publish_closest_driver(channel, ride_data:dict):
    ride_events= await channel.declare_exchange('tracking-events', ExchangeType.TOPIC,)
    await ride_events.publish(Message(json.dumps(ride_data).encode()), routing_key='tracking.ride.driver')


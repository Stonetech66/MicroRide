import json
from aio_pika import connect, ExchangeType, Message
import os


RABBITMQ_HOST= os.getenv('RABBITMQ_HOST')
RABBITMQ_PORT= os.getenv('RABBITMQ_PORT')
RABBITMQ_USER= os.getenv('RABBITMQ_DEFAULT_USER')
RABBITMQ_PASSWORD= os.getenv('RABBITMQ_DEFAULT_PASS')

RABBITMQ_URL= f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/'

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
    tracking_events= await channel.declare_exchange('tracking-events', ExchangeType.TOPIC,)
    await tracking_events.publish(Message(json.dumps(ride_data).encode()), routing_key='tracking.ride.arrived')

async def publish_ride_in_transit(ride_data:dict):
    channel= await get_channel()
    tracking_events= await channel.declare_exchange('tracking-events', ExchangeType.TOPIC,)
    await tracking_events.publish(Message(json.dumps(ride_data).encode()), routing_key='tracking.ride.in_transit')

async def publish_ride_completed(ride_data:dict):
    channel= await get_channel()
    tracking_events= await channel.declare_exchange('tracking-events', ExchangeType.TOPIC,)
    await tracking_events.publish(Message(json.dumps(ride_data).encode()), routing_key='tracking.ride.completed')

async def publish_nearest_driver(channel, ride_data:dict):
    tracking_events= await channel.declare_exchange('tracking-events', ExchangeType.TOPIC,)
    await tracking_events.publish(Message(json.dumps(ride_data).encode()), routing_key='tracking.ride.nearest_driver')

async def publish_ride_eta_updated(channel, ride_data:dict):
    tracking_events= await channel.declare_exchange('tracking-events', ExchangeType.TOPIC,)
    await tracking_events.publish(Message(json.dumps(ride_data).encode()), routing_key='tracking.ride.update_eta')


async def publish_update_driver_location(ride_data:dict):
    channel= await get_channel()
    tracking_events= await channel.declare_exchange('tracking-events', ExchangeType.TOPIC,)
    await tracking_events.publish(Message(json.dumps(ride_data).encode()), routing_key='tracking.driver.location_updated')


async def publish_driver_eta(channel, ride_data:dict):
    tracking_events= await channel.declare_exchange('tracking-events', ExchangeType.TOPIC,)
    await tracking_events.publish(Message(json.dumps(ride_data).encode()), routing_key='tracking.ride.eta')

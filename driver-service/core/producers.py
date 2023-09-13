import json
from aio_pika import connect, ExchangeType, Message
import os

# Get RabbitMQ connection details
RABBITMQ_HOST= os.getenv('RABBITMQ_HOST')
RABBITMQ_PORT= os.getenv('RABBITMQ_PORT')
RABBITMQ_USER= os.getenv('RABBITMQ_DEFAULT_USER')
RABBITMQ_PASS= os.getenv('RABBITMQ_DEFAULT_PASS')

# Construct RabbitMQ URL
RABBITMQ_URL= f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/'

# Function to get or create connnection to RabbitMQ 
connection= None
async def get_connection():
    global connection
    connection= await connect(RABBITMQ_URL)
    return connection

# Function to get RabbitMQ channel
async def get_channel():
    global connection
    if not connection:
        connection= await get_connection()
    channel= await connection.channel()
    return channel


# Handles publishing of event when a driver is created
async def publish_driver_created(driver_data:dict):
    channel= await get_channel()
    ride_events= await channel.declare_exchange('driver-events', ExchangeType.TOPIC,)
    await ride_events.publish(Message(json.dumps(driver_data).encode()), routing_key='driver.created')


# Handles publishing of event when a driver status is updated
async def publish_driver_status_updated(driver_data:dict):
    channel= await get_channel()
    ride_events= await channel.declare_exchange('driver-events', ExchangeType.TOPIC,)
    await ride_events.publish(Message(json.dumps(driver_data).encode()), routing_key='driver.status.updated')


# Handles publishing of event when a driver confirms a ride request
async def publish_ride_confirmed_driver(driver_data:dict):
    channel= await get_channel()
    ride_events= await channel.declare_exchange('driver-events', ExchangeType.TOPIC,)
    await ride_events.publish(Message(json.dumps(driver_data).encode()), routing_key='driver.ride.confirmed')

# Handles publishing of event when a driver rejects a ride request
async def publish_ride_rejected(driver_data:dict):
    channel= await get_channel()
    ride_events= await channel.declare_exchange('driver-events', ExchangeType.TOPIC,)
    await ride_events.publish(Message(json.dumps(driver_data).encode()), routing_key='driver.ride.rejected')

# Handles publishing of event to find ETA of a confirmed ride request
async def publish_find_ride_eta(driver_data:dict):
    channel= await get_channel()
    ride_events= await channel.declare_exchange('driver-events', ExchangeType.TOPIC,)
    await ride_events.publish(Message(json.dumps(driver_data).encode()), routing_key='driver.find_eta')

# Handles publishing of event when a driver gets a new ride request
async def publish_driver_new_ride_request(channel,driver_data:dict):
    ride_events= await channel.declare_exchange('driver-events', ExchangeType.TOPIC,)
    await ride_events.publish(Message(json.dumps(driver_data).encode()), routing_key='driver.ride.new_request')

# Handles publishing of event when a driver is unavailable or already matched to a ride request
async def publish_find_new_driver(channel,driver_data:dict):
    ride_events= await channel.declare_exchange('driver-events', ExchangeType.TOPIC,)
    await ride_events.publish(Message(json.dumps(driver_data).encode()), routing_key='driver.ride.find_new_driver')

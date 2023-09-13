import json
from aio_pika import connect, ExchangeType, Message
import os

# Get RabbitMQ connection details
RABBITMQ_HOST= os.getenv('RABBITMQ_HOST')
RABBITMQ_PORT= os.getenv('RABBITMQ_PORT')
RABBITMQ_USER= os.getenv('RABBITMQ_DEFAULT_USER')
RABBITMQ_PASSWORD= os.getenv('RABBITMQ_DEFAULT_PASS')

# Construct RabbitMQ URL
RABBITMQ_URL= f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/'

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


# Handles publishing of event when a user confirms a ride request
async def publish_ride_confirmed_user(channel, ride_data:dict):
    driver_events= await channel.declare_exchange('ride-events', ExchangeType.TOPIC)
    await driver_events.publish(Message(json.dumps(ride_data).encode()), routing_key='ride.confirmed.user')


# Handles publishing of event when a user cancels a ride request
async def publish_ride_canceled(ride_data:dict):
    channel= await get_channel()
    driver_events= await channel.declare_exchange('ride-events', ExchangeType.TOPIC)
    await driver_events.publish(Message(json.dumps(ride_data).encode()), routing_key='ride.canceled')


# Handles publishing of event to find nearest ride to a user
async def publish_find_nearest_ride(ride_data:dict):
    channel= await get_channel()
    driver_events= await channel.declare_exchange('ride-events', ExchangeType.TOPIC)
    await driver_events.publish(Message(json.dumps(ride_data).encode()), routing_key='ride.find.driver')

# Handles publishing of event to get ride fare
async def publish_get_ride_fare(ride_data:dict):
    channel= await get_channel()
    ride_events= await channel.declare_exchange('ride-events', ExchangeType.TOPIC)
    await ride_events.publish(Message(json.dumps(ride_data).encode()), routing_key='ride.find.fare')






# connect= pika.BlockingConnection(pika.ConnectionParameters('localhost'))
# channel=connect.channel()
# channel.exchange_declare(exchange='ride-events', exchange_type='topic')

# def publish_ride_booked(ride_data:dict):
#     data= json.dumps(ride_data)
#     channel.basic_publish(exchange='ride-events', routing_key='ride.booked', body=data)


# def publish_ride_completed(ride_data:dict):
#     data= json.dumps(ride_data)
#     channel.basic_publish(exchange='ride-events', routing_key='ride.completed', body=data)

# def publish_ride_canceled(ride_data:dict):
#     data= json.dumps(ride_data)
#     channel.basic_publish(exchange='ride-events', routing_key='ride.canceled', body=data)






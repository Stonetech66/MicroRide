import json
from aio_pika import connect, ExchangeType, Message
import os


# Define RabbitMQ connection details from environmental variables
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


# Handles publishing of ride fare
async def publish_ride_fare_calculated(channel, ride_data:dict):
    analysis_events= await channel.declare_exchange('analysis-events', ExchangeType.TOPIC)
    await analysis_events.publish(Message(json.dumps(ride_data).encode()), routing_key='analysis.ride.fare')




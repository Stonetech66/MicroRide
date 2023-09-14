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

# Handles publishing of event when a ride payment is successful
async def publish_payment_success(payment_data:dict):
    channel= await get_channel()
    ride_events= await channel.declare_exchange('payment-events', ExchangeType.TOPIC,)
    await ride_events.publish(Message(json.dumps(payment_data).encode()), routing_key='payment.ride.success')

# Handles publishing of event when a ride payment failed
async def publish_payment_failed(payment_data:dict):
    channel= await get_channel()
    ride_events= await channel.declare_exchange('payment-events', ExchangeType.TOPIC,)
    await ride_events.publish(Message(json.dumps(payment_data).encode()), routing_key='payment.ride.failed')
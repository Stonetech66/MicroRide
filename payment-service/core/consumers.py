import asyncio 
import json
from aio_pika import connect, ExchangeType
from .models import Ride, Ride_Status
from .database import database
import os
from . import callbacks


# Define RabbitMQ connection details from environmental variables
RABBITMQ_HOST= os.getenv('RABBITMQ_HOST')
RABBITMQ_PORT= os.getenv('RABBITMQ_PORT')
RABBITMQ_USER= os.getenv('RABBITMQ_DEFAULT_USER')
RABBITMQ_PASSWORD= os.getenv('RABBITMQ_DEFAULT_PASS')

# Construct RabbitMQ URL
RABBITMQ_URL= f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/'


# Callback for handling ride-related messages
async def ride_consumer_callback( message):
    consumer_callback=callbacks.RideConsumerCallback()
    async with message.process():
        data=json.loads(message.body)
        if message.routing_key == 'ride.canceled':
            await consumer_callback.ride_canceled(data)

# Callback for handling driver-related messages
async def driver_consumer_callback( message):
    consumer_callback=callbacks.DriverConsumerCallback()
    async with message.process():
        data=json.loads(message.body)
        if message.routing_key == 'driver.ride.confirmed':
            await consumer_callback.driver_confirmed_ride_request(data)


# Main consumer function
async def consumer()-> None:
    try: 
        # Connect to RabbitMQ
        connection= await connect(RABBITMQ_URL)
        async with connection:
            # Connect to database
            await database.connect()

            channel= await connection.channel()

            # Declare exchanges and queues for different event types
            ride_events= await channel.declare_exchange('ride-events', ExchangeType.TOPIC)
            ride_queue= await channel.declare_queue('payment-service-queue-ride', durable=True)
            await ride_queue.bind(ride_events, routing_key='ride.canceled.#')
            
            driver_events= await channel.declare_exchange('driver-events', ExchangeType.TOPIC)
            driver_queue= await channel.declare_queue('payment-service-queue-driver', durable=True)
            await driver_queue.bind(driver_events, routing_key='driver.ride.confirmed.#')
 
            # Consume messages with appropriate callbacks
            await ride_queue.consume(ride_consumer_callback)
            await driver_queue.consume(driver_consumer_callback)

            # Keep the consumer running
            while True:
                await asyncio.sleep(1)


    finally:
        await channel.close()
        await connection.close()
        await database.disconnect()


if __name__ == '__main__':
    print('started consuming')
    asyncio.run(consumer())

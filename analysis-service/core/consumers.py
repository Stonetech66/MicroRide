import asyncio 
import json
from aio_pika import connect, ExchangeType
from functools import partial
import os
from .callbacks import RideConsumerCallback

# Define RabbitMQ connection details from environmental variables
RABBITMQ_HOST= os.getenv('RABBITMQ_HOST')
RABBITMQ_PORT= os.getenv('RABBITMQ_PORT')
RABBITMQ_USER= os.getenv('RABBITMQ_DEFAULT_USER')
RABBITMQ_PASS= os.getenv('RABBITMQ_DEFAULT_PASS')

# Construct RabbitMQ URL
RABBITMQ_URL= f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/'


# Callback for handling ride-related messages
async def ride_consumer_callback(channel, message):
    consumer_callback=RideConsumerCallback()
    async with message.process():
        data=json.loads(message.body)
        if message.routing_key == 'ride.find.fare':
            await consumer_callback.find_ride_fare(channel, data)


# Main consumer function
async def consumer()-> None:
    try:
        # Connect to RabbitMQ
        connection= await connect(RABBITMQ_URL)
        async with connection:
            channel= await connection.channel()

            # Declare exchanges and queues for different event types
            ride_events= await channel.declare_exchange('ride-events', ExchangeType.TOPIC)
            ride_queue= await channel.declare_queue('analysis-service-queue-ride', durable=True)
            await ride_queue.bind(ride_events, routing_key='ride.find.fare.#')
            await ride_queue.bind(ride_events, routing_key='ride.confirmed.#')

            # Consume messages with appropriate callbacks
            await ride_queue.consume(partial(ride_consumer_callback, channel))
            
            # Keep the consumer running
            while True:
                await asyncio.sleep(1)

    finally:
        await channel.close()
        await connection.close()              




if __name__ == '__main__':
    print('started consuming')
    asyncio.run(consumer())











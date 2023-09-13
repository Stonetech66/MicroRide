import asyncio 
import json
from aio_pika import connect, ExchangeType
from functools import partial
from .database import database
import os
import aioredis
from . import callbacks


# Define RabbitMQ connection details from environmental variables
RABBITMQ_HOST= os.getenv('RABBITMQ_HOST')
RABBITMQ_PORT= os.getenv('RABBITMQ_PORT')
RABBITMQ_USER= os.getenv('RABBITMQ_DEFAULT_USER')
RABBITMQ_PASS= os.getenv('RABBITMQ_DEFAULT_PASS')

# Construct RabbitMQ URL
RABBITMQ_URL= f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/'

# Define Redis connection
REDIS_HOST=os.getenv('REDIS_HOST')

# Callback for handling ride-related messages
async def ride_consumer_callback(channel, redis, message):
    consumer_callback=callbacks.RideConsumerCallback()
    async with message.process():
        data=json.loads(message.body)
        if message.routing_key == 'ride.confirmed.user':
            await consumer_callback.ride_confirmed_user(channel, redis, data)
        elif message.routing_key == 'ride.canceled':
            await consumer_callback.ride_canceled(redis, data)


# Callback for handling tracking-related messages
async def tracking_consumer_callback( message):
    consumer_callback=callbacks.TrackingConsumerCallback()
    async with message.process():
        data= json.loads(message.body)
        if message.routing_key == 'tracking.ride.in_transit':
            await consumer_callback.tracking_ride_in_transit(data)
        elif message.routing_key == 'tracking.ride.arrived':
            await consumer_callback.tracking_ride_arrived(data)
        elif message.routing_key == 'tracking.ride.completed':
            await consumer_callback.tracking_ride_completed(data)

# Callback for handling payment-related messages
async def payment_consumer_callback(message):
    consumer_callback=callbacks.PaymentConsumerCallback()
    async with message.process():
        data=json.loads(message.body)
        if message.routing_key=='payment.ride.success':
            await consumer_callback.payment_succesful(data)
        

# Main consumer function
async def consumer()-> None:
    try: 
        # Connect to RabbitMQ
        connection= await connect(RABBITMQ_URL)
        async with connection:
            channel= await connection.channel()
            # Connect to database
            await database.connect()

            # Connect to Redis
            redis= await aioredis.from_url(f'redis://{REDIS_HOST}', decode_responses=True)

            # Declare exchanges and queues for different event types
            ride_events= await channel.declare_exchange('ride-events', ExchangeType.TOPIC)
            ride_queue= await channel.declare_queue('driver-service-queue-ride', durable=True)
            await ride_queue.bind(ride_events, routing_key='ride.canceled.#')
            await ride_queue.bind(ride_events, routing_key='ride.confirmed.user.#')

            tracking_events= await channel.declare_exchange('tracking-events', ExchangeType.TOPIC,)
            tracking_queue= await channel.declare_queue('driver-service-queue-tracking',  durable=True)
            await tracking_queue.bind(tracking_events, routing_key='tracking.ride.arrived.#')
            await tracking_queue.bind(tracking_events, routing_key='tracking.ride.in_transit.#')
            await tracking_queue.bind(tracking_events, routing_key='tracking.ride.completed.#')

            payment_events= await channel.declare_exchange('payment-events', ExchangeType.TOPIC,)
            payment_queue= await channel.declare_queue('driver-service-queue-payment',  durable=True)
            await payment_queue.bind(payment_events, routing_key='payment.ride.success.#')

            # Consume messages with appropriate callbacks
            await payment_queue.consume(payment_consumer_callback,)
            await tracking_queue.consume(tracking_consumer_callback)
            await ride_queue.consume(partial(ride_consumer_callback, channel, redis))
    
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




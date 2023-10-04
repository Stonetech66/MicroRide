import asyncio 
import aioredis
import json
from aio_pika import connect, ExchangeType
import os
from functools import partial
from . import callbacks


# Define RabbitMQ connection details from environmental variables
RABBITMQ_HOST= os.getenv('RABBITMQ_HOST')
RABBITMQ_PORT= os.getenv('RABBITMQ_PORT')
RABBITMQ_USER= os.getenv('RABBITMQ_DEFAULT_USER')
RABBITMQ_PASSWORD= os.getenv('RABBITMQ_DEFAULT_PASS')

# Construct RabbitMQ URL
RABBITMQ_URL= f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/'

# Define Redis host
REDIS_HOST=os.getenv('REDIS_HOST')

# Callback for handling tracking-related messages
async def tracking_consumer_callback(redis, message):
    consumer_callback=callbacks.TrackingConsumerCallback()
    async with message.process():
        data= json.loads(message.body)
        user_id=data['user_id']
        if message.routing_key == 'tracking.ride.update_eta':
            await consumer_callback.tracking_ride_update_eta(redis, user_id, data)
        elif message.routing_key == 'tracking.ride.arrived':
            await consumer_callback.tracking_ride_arrived(redis, user_id, data)
        elif message.routing_key == 'tracking.ride.in_transit':
            await consumer_callback.tracking_ride_in_transit(redis, user_id, data)
        elif message.routing_key == 'tracking.ride.completed':
            await consumer_callback.tracking_ride_completed(redis, user_id, data)
        elif message.routing_key == 'tracking.ride.nearest_driver':
            await consumer_callback.tracking_nearest_driver(redis, user_id, data)

# Callback for handling ride-related messages
async def ride_consumer_callback( redis, message):
    consumer_callback=callbacks.RideConsumerCallback()
    async with message.process():
        data=json.loads(message.body)
        if message.routing_key == 'ride.find.driver':
            await consumer_callback.ride_find_nearest_driver(redis, data)
        elif message.routing_key == 'ride.canceled':
            await consumer_callback.ride_canceled(redis, data)


# Callback for handling payment-related messages
async def payment_consumer_callback( redis, message):
    consumer_callback=callbacks.PaymentConsumerCallback()
    async with message.process():
        data=json.loads(message.body)
        user_id=data['user_id']
        if message.routing_key == 'payment.success':
            await consumer_callback.ride_payment_success(redis, user_id, data)
        elif message.routing_key == 'payment.failed':
            await consumer_callback.ride_payment_failed(redis, user_id, data)


# Callback for handling driver-related messages
async def driver_consumer_callback(redis, message):
    consumer_callback=callbacks.DriverConsumerCallback()
    async with message.process():
        data=json.loads(message.body)
        if message.routing_key == 'driver.created':
            await consumer_callback.driver_created(redis, data)
        elif message.routing_key == 'driver.ride.new_request':
            await consumer_callback.driver_new_ride_request(redis, data)
        elif message.routing_key == 'driver.ride.confirmed':
            await consumer_callback.driver_confirmed_ride(redis, data)
        elif message.routing_key == 'driver.ride.rejected':
            await consumer_callback.driver_rejected_ride(redis, data)

# Callback for handling analysis-related messages
async def analysis_consumer_callback(redis, message):
    consumer_callback= callbacks.AnalysisConsumerCallback()
    async with message.process():
        data=json.loads(message.body)
        if message.routing_key == 'analysis.ride.fare':
            await consumer_callback.analysis_ride_fare(redis, data)


# Main consumer function
async def consumer()-> None:
    try: 
        # Connect to RabbitMQ
        connection= await connect(RABBITMQ_URL)
        async with connection:
            channel= await connection.channel()
            redis= await aioredis.from_url(f'redis://{REDIS_HOST}', decode_responses=True)

            # Declare exchanges and queues for different event types
            tracking_events= await channel.declare_exchange('tracking-events', ExchangeType.TOPIC,)
            tracking_queue= await channel.declare_queue('notification-service-queue-tracking',  durable=True)
            await tracking_queue.bind(tracking_events, routing_key='tracking.ride.arrived.#')
            await tracking_queue.bind(tracking_events, routing_key='tracking.ride.update_eta.#')
            await tracking_queue.bind(tracking_events, routing_key='tracking.ride.in_transit.#')
            await tracking_queue.bind(tracking_events, routing_key='tracking.ride.completed.#')
            await tracking_queue.bind(tracking_events, routing_key='tracking.ride.nearest_driver.#')

            payment_events= await channel.declare_exchange('payment-events', ExchangeType.TOPIC,)
            payment_queue= await channel.declare_queue('notification-service-queue-payment',  durable=True)
            await payment_queue.bind(payment_events, routing_key='payment.ride.*')

            ride_events= await channel.declare_exchange('ride-events', ExchangeType.TOPIC,)
            ride_queue= await channel.declare_queue('notification-service-queue-ride', durable=True)
            await ride_queue.bind(ride_events, routing_key='ride.find.driver.#')
            await ride_queue.bind(ride_events, routing_key='ride.canceled.#')

            driver_events= await channel.declare_exchange('driver-events', ExchangeType.TOPIC)
            driver_queue= await channel.declare_queue('notification-service-queue-driver',  durable=True)
            await driver_queue.bind(driver_events, routing_key='driver.created.#')
            await driver_queue.bind(driver_events, routing_key='driver.ride.new_request.#')
            await driver_queue.bind(driver_events, routing_key='driver.ride.rejected.#')
            await driver_queue.bind(driver_events, routing_key='driver.ride.confirmed.#')

            analysis_events= await channel.declare_exchange('analysis-events', ExchangeType.TOPIC,)
            analysis_queue= await channel.declare_queue('notification-service-queue-analysis',  durable=True)
            await analysis_queue.bind(analysis_events, routing_key='analysis.ride.fare.#')
           
            # Consume messages with appropriate callbacks
            await tracking_queue.consume(partial(tracking_consumer_callback, redis))
            await ride_queue.consume(partial(ride_consumer_callback, redis))
            await payment_queue.consume(partial(payment_consumer_callback, redis))
            await driver_queue.consume(partial(driver_consumer_callback, redis))
            await analysis_queue.consume(partial(analysis_consumer_callback, redis))

            while True:
                await asyncio.sleep(1)
                    
    finally:
        await channel.close()
        await connection.close()

if __name__ == '__main__':
    print('started consuming')
    asyncio.run(consumer())







import asyncio 
import json
from aio_pika import connect, ExchangeType
from functools import partial
import os
from .callbacks import DriverConsumerCallback, RideConsumerCallback, TrackingConsumerCallback

# Define RabbitMQ connection details from environmental variables
RABBITMQ_HOST= os.getenv('RABBITMQ_HOST')
RABBITMQ_PORT= os.getenv('RABBITMQ_PORT')
RABBITMQ_USER= os.getenv('RABBITMQ_DEFAULT_USER')
RABBITMQ_PASSWORD= os.getenv('RABBITMQ_DEFAULT_PASS')

# Construct RabbitMQ URL
RABBITMQ_URL= f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/'

# Callback for handling ride-related messages
async def ride_consumer_callback(channel, message):
    consumer_callback=RideConsumerCallback()
    async with message.process():
        data=json.loads(message.body)
        if message.routing_key == 'ride.canceled':
            await consumer_callback.ride_canceled(data)
        elif message.routing_key == 'ride.find.driver':
            await consumer_callback.ride_find_nearest_driver(channel, data)

# Callback for handling driver-related messages
async def driver_consumer_callback(channel,  message):
    consumer_callback=DriverConsumerCallback()
    async with message.process():
        data=json.loads(message.body)
        if message.routing_key == 'driver.created':
            await consumer_callback.driver_created(data)
        elif message.routing_key == 'driver.ride.confirmed':
            await consumer_callback.driver_confirmed_ride(data)         
        elif message.routing_key == 'driver.status.updated':
            await consumer_callback.driver_status_updated(data)
        elif message.routing_key== 'driver.find_eta':
            await consumer_callback.driver_find_eta(channel, data)
        elif message.routing_key== 'driver.ride.rejected':
            await consumer_callback.driver_reject_ride(channel, data)
        elif message.routing_key== 'driver.ride.find_new_driver':
            await consumer_callback.driver_find_new_driver(channel, data)
                


# Callback for handling tracking-related messages
async def tracking_consumer_callback(channel, message):
    consumer_callback= TrackingConsumerCallback()
    async with message.process():
        data=json.loads(message.body)
        if message.routing_key == 'tracking.driver.location_updated':
            await consumer_callback.tracking_driver_location_updated(channel, data)


# Main consumer function
async def consumer()-> None:

    try:
        # Connect to RabbitMQ
        connection= await connect(RABBITMQ_URL)
        async with connection:
            channel= await connection.channel()

            # Declare exchanges and queues for different event types
            ride_events= await channel.declare_exchange('ride-events', ExchangeType.TOPIC)
            ride_queue= await channel.declare_queue('tracking-service-queue-ride', durable=True)
            await ride_queue.bind(ride_events, routing_key='ride.canceled.#')
            await ride_queue.bind(ride_events, routing_key='ride.find.driver.#')

            driver_events= await channel.declare_exchange('driver-events', ExchangeType.TOPIC)
            driver_queue= await channel.declare_queue('tracking-service-queue-driver', durable=True)
            await driver_queue.bind(driver_events, routing_key='driver.created.#')
            await driver_queue.bind(driver_events, routing_key='driver.status.updated.#')
            await driver_queue.bind(driver_events, routing_key='driver.find_eta.#')
            await driver_queue.bind(driver_events, routing_key='driver.ride.confirmed.#')
            await driver_queue.bind(driver_events, routing_key='driver.ride.rejected.#')
            await driver_queue.bind(driver_events, routing_key='driver.ride.find_new_driver.#')

            tracking_events= await channel.declare_exchange('tracking-events', ExchangeType.TOPIC)
            tracking_queue= await channel.declare_queue('tracking-service-queue-tracking', durable=True)
            await tracking_queue.bind(tracking_events, routing_key='tracking.driver.location_updated.#')

            # Consume messages with appropriate callbacks
            await ride_queue.consume(partial(ride_consumer_callback, channel))
            await driver_queue.consume(partial(driver_consumer_callback, channel))
            await tracking_queue.consume(partial(tracking_consumer_callback, channel))

            # Keep the consumer running
            while True:
                await asyncio.sleep(1)

                    

    finally:
        await channel.close()
        await connection.close()            




if __name__ == '__main__':
    print('started consuming')
    asyncio.run(consumer())















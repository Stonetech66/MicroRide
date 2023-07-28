import asyncio 
import aioredis
import json
from aio_pika import connect, ExchangeType
from .database import driver_table
from .websockets import send_driver_websocket_data, send_user_websocket_data
import os
from functools import partial
from .utils import update_user_websocket_event


RABBITMQ_HOST= os.getenv('RABBITMQ_HOST')
RABBITMQ_PORT= os.getenv('RABBITMQ_PORT')
RABBITMQ_USER= os.getenv('RABBITMQ_DEFAULT_USER')
RABBITMQ_PASSWORD= os.getenv('RABBITMQ_DEFAULT_PASS')

RABBITMQ_URL= f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/'
REDIS_HOST=os.getenv('REDIS_HOST')





        

async def tracking_consumer_callback(redis, message):
    async with message.process():
        data= json.loads(message.body)
        user_id=data['user_id']
        if message.routing_key == 'tracking.ride.arrived':
            await send_user_websocket_data(str(user_id), 'ride-arrived', data, redis)
        elif message.routing_key == 'tracking.ride.in_transit':
                await send_user_websocket_data(str(user_id), 'ride-in_transit', data, redis)
                await send_driver_websocket_data(str(data['driver_id']), 'ride-in_transit', data, redis)
        elif message.routing_key == 'tracking.ride.completed':
                await send_user_websocket_data(str(user_id), 'ride-completed', data, redis)
                await send_driver_websocket_data(str(data['driver_id']), 'ride-completed', data, redis)


                           
async def ride_consumer_callback( redis, message):
    async with message.process():
        data=json.loads(message.body)
        driver_id=data['driver_id']
        if message.routing_key == 'ride.confirmed':
            await send_driver_websocket_data(str(driver_id), 'ride-confirmed', data, redis)
            data.update({'event':'ride-confirmed'})
            await update_user_websocket_event(redis, data, data['user_id'])
        elif message.routing_key == 'ride.canceled':
            await send_driver_websocket_data(str(driver_id), 'ride-canceled', data, redis)

async def payment_consumer_callback( redis, message):
    async with message.process():
        data=json.loads(message.body)
        user_id=data['user_id']
        if message.routing_key == 'payment.success':
            await send_user_websocket_data(str(user_id), 'payment-successful', data, redis)
            await send_driver_websocket_data(str(data['driver_id']), 'payment-successful', data, redis)
        elif message.routing_key == 'payment.failed':
            await send_user_websocket_data(str(user_id), 'payment-successful', data, redis)
    
async def driver_consumer_callback(redis, message):
    async with message.process():
        data=json.loads(message.body)
        if message.routing_key == 'driver.created':
            await driver_table.insert_one(data)

async def consumer()-> None:
    try: 
        connection= await connect(RABBITMQ_URL)
        async with connection:
            channel= await connection.channel()
            redis= await aioredis.from_url(f'redis://{REDIS_HOST}', decode_responses=True)

            tracking_events= await channel.declare_exchange('tracking-events', ExchangeType.TOPIC,)
            tracking_queue= await channel.declare_queue('notification-service-queue-tracking',  durable=True)
            await tracking_queue.bind(tracking_events, routing_key='tracking.ride.*')

            payment_events= await channel.declare_exchange('payment-events', ExchangeType.TOPIC,)
            payment_queue= await channel.declare_queue('notification-service-queue-payment',  durable=True)
            await payment_queue.bind(payment_events, routing_key='payment.ride.*')

            ride_events= await channel.declare_exchange('ride-events', ExchangeType.TOPIC,)
            ride_queue= await channel.declare_queue('notification-service-queue-ride', durable=True)
            await ride_queue.bind(ride_events, routing_key='ride.confirmed.#')
            await ride_queue.bind(ride_events, routing_key='ride.canceled.#')
        
            driver_events= await channel.declare_exchange('driver-events', ExchangeType.TOPIC)
            driver_queue= await channel.declare_queue('notification-service-queue-driver',  durable=True)
            await driver_queue.bind(driver_events, routing_key='driver.created.#')

            await tracking_queue.consume(partial(tracking_consumer_callback, redis))
            await ride_queue.consume(partial(ride_consumer_callback, redis))
            await payment_queue.consume(partial(payment_consumer_callback, redis))
            await driver_queue.consume(partial(driver_consumer_callback, redis))

            while True:
                await asyncio.sleep(1)
                    
    finally:
        await channel.close()
        await connection.close()

if __name__ == '__main__':
    print('started consuming')
    asyncio.run(consumer())







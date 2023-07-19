import asyncio 
import aioredis
import json
from aio_pika import connect, ExchangeType
from .database import driver_table
from .websockets import send_driver_websocket_data, send_user_websocket_data
import os


RABBITMQ_HOST= os.getenv('RABBITMQ_HOST')
RABBITMQ_PORT= os.getenv('RABBITMQ_PORT')
RABBITMQ_USER= os.getenv('RABBITMQ_DEFAULT_USER')
RABBITMQ_PASSWORD= os.getenv('RABBITMQ_DEFAULT_PASS')

RABBITMQ_URL= f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/'





        

async def tracking_consumer_callback( message):
    async with message.process():
        data= json.loads(message.body)
        if message.routing_key == 'tracking.ride.arrived':
            await send_user_websocket_data(str(data['user_id']), 'ride-arrived', data)
        elif message.routing_key == 'tracking.ride.in_transit':
                await send_user_websocket_data(str(data['user_id']), 'ride-in_transit', data)
                await send_driver_websocket_data(str(data['driver_id']), 'ride-in_transit', data)
        elif message.routing_key == 'tracking.ride.completed':
                await send_user_websocket_data(str(data['user_id']), 'ride-completed', data)
                await send_driver_websocket_data(str(data['driver_id']), 'ride-completed', data)


                           
async def ride_consumer_callback( message):
    async with message.process():
        data=json.loads(message.body)
        if message.routing_key == 'ride.confirmed':
            await send_driver_websocket_data(str(data['driver_id']), 'ride-confirmed', data)
        elif message.routing_key == 'ride.canceled':
            await send_driver_websocket_data(str(data['driver_id']), 'ride-canceled', data)

async def payment_consumer_callback( message):
    async with message.process():
        data=json.loads(message.body)
        if message.routing_key == 'payment.success':
            await send_user_websocket_data(str(data['user_id']), 'payment-successful', data)
            await send_driver_websocket_data(str(data['driver_id']), 'payment-successful', data)
        elif message.routing_key == 'payment.failed':
            await send_user_websocket_data(str(data['user_id']), 'payment-successful', data)
    
async def driver_consumer_callback( message):
    async with message.process():
        data=json.loads(message.body)
        if message.routing_key == 'driver.created':
            await driver_table.insert_one(data)

async def consumer()-> None:
    try: 
        connection= await connect(RABBITMQ_URL)
        async with connection:
            channel= await connection.channel()
                        
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

            await tracking_queue.consume(tracking_consumer_callback)
            await ride_queue.consume(ride_consumer_callback)
            await payment_queue.consume(payment_consumer_callback)
            await driver_queue.consume(driver_consumer_callback)

            while True:
                await asyncio.sleep(1)
                    
    finally:
        await channel.close()
        await connection.close()

if __name__ == '__main__':
    print('started consuming')
    asyncio.run(consumer())







import asyncio 
import json
from aio_pika import connect, ExchangeType
from .producers import publish_nearest_driver
from .utils import get_nearest_driver
from .database import ride_table, driver_table
from functools import partial
import os


RABBITMQ_HOST= os.getenv('RABBITMQ_HOST')
RABBITMQ_PORT= os.getenv('RABBITMQ_PORT')
RABBITMQ_USER= os.getenv('RABBITMQ_DEFAULT_USER')
RABBITMQ_PASSWORD= os.getenv('RABBITMQ_DEFAULT_PASS')

RABBITMQ_URL= f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/'

async def ride_consumer_callback(channel, message):
    async with message.process():
        data=json.loads(message.body)
        if message.routing_key == 'ride.confirmed':
            await ride_table.insert_one(data)
        elif message.routing_key == 'ride.canceled':
            await ride_table.update_one({'id':data['ride_id'], '$set':{'status':'canceled'}})
        elif message.routing_key == 'ride.find.driver':
            driver=await get_nearest_driver(data['pickup_location'])
            data.update({'driver_id':driver})
            await publish_nearest_driver(channel, data)


async def driver_consumer_callback( message):
    async with message.process():
        data=json.loads(message.body)
        if message.routing_key == 'driver.created':
            await driver_table.insert_one(data)
        elif message.routing_key == 'driver.status.updated':
            await driver_table.update_one({'user_id':data['user_id'], '$set':{'status':data['status']}})


async def consumer()-> None:

    try:
        connection= await connect(RABBITMQ_URL)
        async with connection:
            channel= await connection.channel()
            ride_events= await channel.declare_exchange('ride-events', ExchangeType.TOPIC)
            ride_queue= await channel.declare_queue('', durable=True)
            await ride_queue.bind(ride_events, routing_key='ride.confirmed.#')
            await ride_queue.bind(ride_events, routing_key='ride.canceled.#')
            await ride_queue.bind(ride_events, routing_key='ride.find.driver.#')

            driver_events= await channel.declare_exchange('driver-events', ExchangeType.TOPIC)
            driver_queue= await channel.declare_queue('tracking-queue-events', durable=True)
            await driver_queue.bind(driver_events, routing_key='driver.*')


            await ride_queue.consume(partial(ride_consumer_callback, channel))
            await driver_queue.consume(driver_consumer_callback)


            while True:
                await asyncio.sleep(1)

                    

    finally:
        await channel.close()
        await connection.close()            




if __name__ == '__main__':
    print('started consuming')
    asyncio.run(consumer())











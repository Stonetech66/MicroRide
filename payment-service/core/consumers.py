import asyncio 
import json
from aio_pika import connect, ExchangeType
from .models import Ride, Ride_Status
from .database import database
import os


RABBITMQ_HOST= os.getenv('RABBITMQ_HOST')
RABBITMQ_PORT= os.getenv('RABBITMQ_PORT')
RABBITMQ_USER= os.getenv('RABBITMQ_DEFAULT_USER')
RABBITMQ_PASSWORD= os.getenv('RABBITMQ_DEFAULT_PASS')

RABBITMQ_URL= f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/'


async def ride_consumer_callback( message):
    async with message.process():
        data=json.loads(message.body)
        if message.routing_key == 'ride.confirmed':
            query= Ride.insert().values(**data)
            await database.execute(query)
        elif message.routing_key == 'ride.canceled':
            query= Ride.update().where(Ride.c.id==data['ride_id']).values(status=Ride_Status.canceled, fare=data['fare'])
            await database.execute(query)
        
async def consumer()-> None:
    try: 
        connection= await connect(RABBITMQ_URL)
        async with connection:
            await database.connect()
            channel= await connection.channel()
            ride_events= await channel.declare_exchange('ride-events', ExchangeType.TOPIC)
            ride_queue= await channel.declare_queue('payment-service-queue-ride', durable=True)
            await ride_queue.bind(ride_events, routing_key='ride.canceled.#')
            await ride_queue.bind(ride_events, routing_key='ride.confirmed.#')

            await ride_queue.consume(ride_consumer_callback)
    

            while True:
                await asyncio.sleep(1)


    finally:
        await channel.close()
        await connection.close()
        await database.disconnect()


if __name__ == '__main__':
    print('started consuming')
    asyncio.run(consumer())

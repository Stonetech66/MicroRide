import asyncio 
import json
from aio_pika import connect, ExchangeType
from .models import Ride, Ride_Status
from .database import database
import os


RABBITMQ_HOST= os.getenv('RABBITMQ_HOST')
RABBITMQ_PORT= os.getenv('RABBITMQ_PORT')
RABBITMQ_USER= os.getenv('RABBITMQ_DEFAULT_USER')
RABBITMQ_PASS= os.getenv('RABBITMQ_DEFAULT_PASS')

RABBITMQ_URL= f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/'



async def ride_consumer_callback( message):
    async with message.process():
        data=json.loads(message.body)
        if message.routing_key == 'ride.confirmed':
            query= Ride.insert().values(**data)
            await database.execute(query)
        elif message.routing_key == 'ride.canceled':
            query= Ride.update().where(Ride.c.id==data['ride_id']).values(status=Ride_Status.canceled, fare=data['fare'])
            ride= await database.execute(query)
        

async def tracking_consumer_callback( message):
    async with message.process():
        data= json.loads(message.body)
        if message.routing_key == 'tracking.ride.in_transit':
            ride_id= data['ride_id']
            query= Ride.update().where(Ride.c.id==ride_id).values(status=Ride_Status.in_transit)
            await database.execute(query)
        elif message.routing_key == 'tracking.ride.arrived':
            ride_id= data['ride_id']
            query= Ride.update().where(Ride.c.id==ride_id).values(status=Ride_Status.arrived)
            await database.execute(query)
        elif message.routing_key == 'tracking.ride.completed':
            ride_id= data['ride_id']
            query= Ride.update().where(Ride.c.id==ride_id).values(status=Ride_Status.completed)
            await database.execute(query)


async def payment_consumer_callback(message):
    async with message.process():
            data=json.loads(message.body)
            ride_id= data['ride_id']
            query= Ride.update().where(Ride.c.id==ride_id).values(paid=True)
            await database.execute(query)


async def consumer()-> None:
    try: 
        connection= await connect(RABBITMQ_URL)
        async with connection:
            channel= await connection.channel()
            ride_events= await channel.declare_exchange('ride-events', ExchangeType.TOPIC)
            ride_queue= await channel.declare_queue('driver-service-queue-ride', durable=True)
            await ride_queue.bind(ride_events, routing_key='ride.canceled.#')
            await ride_queue.bind(ride_events, routing_key='ride.confirmed.#')

            tracking_events= await channel.declare_exchange('tracking-events', ExchangeType.TOPIC,)
            tracking_queue= await channel.declare_queue('driver-service-queue-tracking',  durable=True)
            await tracking_queue.bind(tracking_events, routing_key='tracking.ride.*')

            payment_events= await channel.declare_exchange('payment-events', ExchangeType.TOPIC,)
            payment_queue= await channel.declare_queue('driver-service-queue-payment',  durable=True)
            await payment_queue.bind(payment_events, routing_key='payment.ride.success.#')

            await payment_queue.consume(payment_consumer_callback,)
            await tracking_queue.consume(tracking_consumer_callback)
            await ride_queue.consume(ride_consumer_callback)
    

            while True:
                await asyncio.sleep(1)


    finally:
        await channel.close()
        await connection.close()
             




if __name__ == '__main__':
    print('started consuming')
    asyncio.run(consumer())




import asyncio 
import aioredis
import json
from aio_pika import connect, ExchangeType
from .database import database
from .models import Ride, Ride_Status
import websockets
from datetime import datetime
from functools import partial
import os

RABBITMQ_HOST= os.getenv('RABBITMQ_HOST')
RABBITMQ_PORT= os.getenv('RABBITMQ_PORT')
RABBITMQ_USER= os.getenv('RABBITMQ_DEFAULT_USER')
RABBITMQ_PASSWORD= os.getenv('RABBITMQ_DEFAULT_PASS')

RABBITMQ_URL= f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/'

NOTIFICATION_SERVICE_HOST=os.getenv('NOTIFICATION_SERVICE_HOST')
WEBSOCKET_SECRET_KEY=os.getenv('WEBSOCKET_SECRET_KEY')
REDIS_HOST= os.getenv('REDIS_HOST')

async def send_websocket_data(user_id, data):
        time=datetime.now()
        async with websockets.connect(f'ws://{NOTIFICATION_SERVICE_HOST}/api/v1/ws/user/?type=server&token={WEBSOCKET_SECRET_KEY}') as websocket:
            await websocket.send(json.dumps(data))
        
        

async def analysis_consumer_callback(redis, message):
    async with message.process():
        data=json.loads(message.body)
        user_id= str(data['user_id'])
        saved_ride_data=await redis.hgetall('ride-'+user_id)
        if saved_ride_data:
            saved_ride_id=saved_ride_data['ride_id']
            if  saved_ride_id == data['ride_id']: 
                await send_websocket_data(user_id, data)
                await redis.hset('ride-'+user_id, 'fare', data['fare'])

async def tracking_consumer_callback(redis, message):
    async with message.process():
        data= json.loads(message.body)
        if message.routing_key == 'tracking.ride.nearest_driver':
            user_id=str(data['user_id'])
            ride_id=await redis.hget('ride-'+user_id, 'ride_id')
            if ride_id == data['ride_id']:
                await redis.hset('ride-'+user_id, 'driver_id', data['driver_id'])
        elif message.routing_key == 'tracking.ride.arrived':
            ride_id= data['ride_id']
            query= Ride.update().where(Ride.c.id==ride_id).values(status=Ride_Status.arrived)
            ride= await database.execute(query)
        elif message.routing_key == 'tracking.ride.in_transit':
            ride_id= data['ride_id']
            query= Ride.update().where(Ride.c.id==ride_id).values(status=Ride_Status.in_transit)
            ride= await database.execute(query)
        elif message.routing_key == 'tracking.ride.completed':
            ride_id= data['ride_id']
            query= Ride.update().where(Ride.c.id==ride_id).values(status=Ride_Status.completed)
            ride= await database.execute(query)

async def payment_consumer_callback(message):
    async with message.process():
            data=json.loads(message.body)
            ride_id= data['ride_id']
            query= Ride.update().where(Ride.c.id==ride_id).values(paid=True)
            await database.execute(query)



async def consumer()-> None:
    connection= await connect(RABBITMQ_URL)
    try:
        async with connection:
            channel= await connection.channel()
            redis= await aioredis.from_url(f'redis://{REDIS_HOST}', decode_responses=True)


            analysis_events= await channel.declare_exchange('analysis-events', ExchangeType.TOPIC,)
            analysis_queue= await channel.declare_queue('ride-service-queue-analysis',  durable=True)
            await analysis_queue.bind(analysis_events, routing_key='analysis.ride.fare.#')
            
            tracking_events= await channel.declare_exchange('tracking-events', ExchangeType.TOPIC,)
            tracking_queue= await channel.declare_queue('ride-service-queue-tracking',  durable=True)
            await tracking_queue.bind(tracking_events, routing_key='tracking.ride.*')

            payment_events= await channel.declare_exchange('payment-events', ExchangeType.TOPIC,)
            payment_queue= await channel.declare_queue('ride-service-queue-payment',  durable=True)
            await payment_queue.bind(payment_events, routing_key='payment.ride.success.#')

            await analysis_queue.consume(partial(analysis_consumer_callback, redis))
            await tracking_queue.consume(partial(tracking_consumer_callback, redis))
            await payment_queue.consume(payment_consumer_callback,)
            while True:
                await asyncio.sleep(1)
    finally:
        await channel.close()
        await connection.close()
        await redis.close()


            




                           
if __name__ == '__main__':
    print('started consuming')
    asyncio.run(consumer())









# import pika 
# import json
# from .models import Ride, Ride_Status
# import aioredis

# # rabbitmq connection
# connect= pika.BlockingConnection(pika.ConnectionParameters('localhost'))
# channel=connect.channel()

# #redis connection
# redis= aioredis.from_url('redis://localhost', decode_responses=True)

# # binding payments queue to payment events with complete status
# channel.exchange_declare(exchange='payment-events', exchange_type='topic',)
# payment_events_queue= channel.queue_declare(queue= '', exclusive=True)
# channel.queue_bind(payment_events_queue.method.queue, exchange='payment-events', routing_key='payment.complete#')

# def handle_ride_payment_complete(ch, method, propr, body):
#     data=json.loads(body)
#     print(data)


# # binding payments queue to driver events with confirmed status
# channel.exchange_declare(exchange='driver-events', exchange_type='topic',)
# driver_events_queue= channel.queue_declare(queue= '', exclusive=True)
# channel.queue_bind(driver_events_queue.method.queue, exchange='driver-events', routing_key='driver.confirmed.#')


# async def handle_driver_confirmed(ch, method, propr, body):
#     data=json.loads(body)
#     print(data)
#     ride_data= await redis.hgetall(data['ride_id'])
    


# channel.basic_consume(queue=payment_events_queue.method.queue, on_message_callback=handle_ride_payment_complete, auto_ack=True)
# channel.basic_consume(queue=driver_events_queue.method.queue, on_message_callback=handle_driver_confirmed, auto_ack=True)

# print('started consuming')
# channel.start_consuming()

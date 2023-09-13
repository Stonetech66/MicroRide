import asyncio 
import aioredis
import json
from aio_pika import connect, ExchangeType
from .database import database
from functools import partial
from . import callbacks
import os

# Define RabbitMQ connection details from environmental variables
RABBITMQ_HOST= os.getenv('RABBITMQ_HOST')
RABBITMQ_PORT= os.getenv('RABBITMQ_PORT')
RABBITMQ_USER= os.getenv('RABBITMQ_DEFAULT_USER')
RABBITMQ_PASSWORD= os.getenv('RABBITMQ_DEFAULT_PASS')

# Construct RabbitMQ URL
RABBITMQ_URL= f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/'

# Get Redis host
REDIS_HOST= os.getenv('REDIS_HOST')

        
        
# Callback for handling analysis-related messages
async def analysis_consumer_callback(redis, message):
    consumer_callback= callbacks.AnalysisConsumerCallback()
    async with message.process():
        data=json.loads(message.body)
        if message.routing_key == 'analysis.ride.fare':
            await consumer_callback.analysis_ride_fare(redis, data)

# Callback for handling tracking-related messages
async def tracking_consumer_callback(channel, redis, message):
    consumer_callback=callbacks.TrackingConsumerCallback()
    async with message.process():
        data= json.loads(message.body)
        if message.routing_key == 'tracking.ride.nearest_driver':
            await consumer_callback.tracking_ride_nearest_driver(channel, redis, data)
        elif message.routing_key == 'tracking.ride.arrived':
            await consumer_callback.tracking_ride_arrived(data)
        elif message.routing_key == 'tracking.ride.in_transit':
            await consumer_callback.tracking_ride_in_transit(data)
        elif message.routing_key == 'tracking.ride.completed':
            await consumer_callback.tracking_ride_completed(data)
        elif message.routing_key=='tracking.ride.eta':
            await consumer_callback.tracking_ride_eta_update(redis, data)

# Callback for handling payment-related messages
async def payment_consumer_callback(message):
    consumer_callback=callbacks.PaymentConsumerCallback()
    async with message.process():
            data=json.loads(message.body)
            if message.routing_key=='payment.ride.success':
                await consumer_callback.ride_payment_success(data)

# Callback for handling driver-related messages
async def driver_consumer_callback(redis,message):
    consumer_callback=callbacks.DriverConsumerCallback()
    async with message.process():
            data=json.loads(message.body)
            if message.routing_key == 'driver.ride.confirmed':
                await consumer_callback.driver_ride_confirmed(redis, data)


# Main consumer function
async def consumer()-> None:
    connection= await connect(RABBITMQ_URL)
    try:
        async with connection:
            channel= await connection.channel()
            # Connect to redis
            redis= await aioredis.from_url(f'redis://{REDIS_HOST}', decode_responses=True)
            # Connect to database
            await database.connect()

            # Declare exchanges and queues for different event types
            analysis_events= await channel.declare_exchange('analysis-events', ExchangeType.TOPIC,)
            analysis_queue= await channel.declare_queue('ride-service-queue-analysis',  durable=True)
            await analysis_queue.bind(analysis_events, routing_key='analysis.ride.fare.#')
            
            tracking_events= await channel.declare_exchange('tracking-events', ExchangeType.TOPIC,)
            tracking_queue= await channel.declare_queue('ride-service-queue-tracking',  durable=True)
            await tracking_queue.bind(tracking_events, routing_key='tracking.ride.arrived.#')
            await tracking_queue.bind(tracking_events, routing_key='tracking.ride.eta.#')
            await tracking_queue.bind(tracking_events, routing_key='tracking.ride.in_transit.#')
            await tracking_queue.bind(tracking_events, routing_key='tracking.ride.completed.#')
            await tracking_queue.bind(tracking_events, routing_key='tracking.ride.nearest_driver.#')

            payment_events= await channel.declare_exchange('payment-events', ExchangeType.TOPIC,)
            payment_queue= await channel.declare_queue('ride-service-queue-payment',  durable=True)
            await payment_queue.bind(payment_events, routing_key='payment.ride.success.#')

            driver_events= await channel.declare_exchange('driver-events', ExchangeType.TOPIC,)
            driver_queue= await channel.declare_queue('ride-service-queue-driver',  durable=True)
            await driver_queue.bind(driver_events, routing_key='driver.ride.confirmed.#')

            # Consume messages with appropriate callbacks
            await analysis_queue.consume(partial(analysis_consumer_callback, redis))
            await tracking_queue.consume(partial(tracking_consumer_callback,channel, redis))
            await payment_queue.consume(payment_consumer_callback,)
            await driver_queue.consume(partial(driver_consumer_callback, redis))

            # Keep the consumer running
            while True:
                await asyncio.sleep(1)

    finally:
        await channel.close()
        await connection.close()
        await redis.close()
        await database.disconnect()


            




                           
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

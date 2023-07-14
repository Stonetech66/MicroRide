import asyncio 
import json
from aio_pika import connect, ExchangeType
from .producers import publish_ride_fare_calculated
from .analyzers import get_random_fare, get_ride_eta
from functools import partial
import os


RABBITMQ_URL= os.getenv('RABBITMQ_URL')

async def ride_consumer_callback(channel, message):
    async with message.process():
        data=json.loads(message.body)
        if message.routing_key == 'ride.find.fare':
            ride_id= data['ride_id']
            analyzed_ride={'ride_id':ride_id, 'user_id':data['user_id'],'fare':get_random_fare(), 'eta':get_ride_eta()}
            await publish_ride_fare_calculated(channel, analyzed_ride)



async def consumer()-> None:
    try:
        connection= await connect(RABBITMQ_URL)
        async with connection:
            channel= await connection.channel()

            ride_events= await channel.declare_exchange('ride-events', ExchangeType.TOPIC)
            ride_queue= await channel.declare_queue('analysis-service-queue-ride', durable=True)
            await ride_queue.bind(ride_events, routing_key='ride.find.fare.#')
            await ride_queue.bind(ride_events, routing_key='ride.confirmed.#')


            await ride_queue.consume(partial(ride_consumer_callback, channel))

            while True:
                await asyncio.sleep(1)

    finally:
        await channel.close()
        await connection.close()              




if __name__ == '__main__':
    print('started consuming')
    asyncio.run(consumer())











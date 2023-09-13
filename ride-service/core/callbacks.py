from .consumers import database
from datetime import datetime
import pytz
import json
from .utils import send_websocket_data
from .producers import publish_ride_confirmed_user
from .models import Ride, Ride_Status


# Class for handling analysis related events
class AnalysisConsumerCallback:

    # Handle analysis ride fare event
    async def analysis_ride_fare(self, redis ,data):
        user_id= str(data['user_id'])
        saved_ride_data=json.loads(await redis.get('ride-'+user_id))
        saved_ride_id=saved_ride_data.get('ride_id')
        if  saved_ride_id == data['ride_id']: 
            saved_ride_data['fare']=data['fare']
            await redis.set('ride-'+user_id, json.dumps(saved_ride_data))
            await send_websocket_data(user_id, saved_ride_data)


# Class for handling tracking related events
class TrackingConsumerCallback:

    # Handle nearest driver event
    async def tracking_ride_nearest_driver(self, channel,  redis, data):
        user_id=str(data['user_id'])
        ride_data= json.loads(await redis.get('ride-'+user_id,))
        ride_id=ride_data.get('ride_id') or ride_data.get('id')
        if ride_id == data['ride_id']:
            driver=data['driver']
            if driver:
                driver_id=driver['driver_id']
                ride_data.update({'driver_id':driver_id})
                await publish_ride_confirmed_user(channel, {**ride_data})
                await redis.set('ride-'+str(user_id), json.dumps(ride_data))
            else:
                data={'event':'no drivers available around you', 'user_id':user_id}
                await redis.delete('ride-'+str(user_id))
                await send_websocket_data(user_id, data)

    # Handle ride in transit
    async def tracking_ride_in_transit(self,data):
        ride_id= data['ride_id']
        query= Ride.update().where(Ride.c.id==ride_id).values(status=Ride_Status.in_transit)
        await database.execute(query)

    # Handle ride arrived
    async def tracking_ride_arrived(self,data):
        ride_id= data['ride_id']
        query= Ride.update().where(Ride.c.id==ride_id).values(status=Ride_Status.arrived)
        await database.execute(query)

    # Handle ride completed
    async def tracking_ride_completed(self,data):
        ride_id= data['ride_id']
        query= Ride.update().where(Ride.c.id==ride_id).values(status=Ride_Status.completed, date=datetime.now(tz=pytz.timezone('UTC')))
        await database.execute(query)

    # Handle ride eta event
    async def tracking_ride_eta_update(self, redis, data):
            ride_data= json.loads(await redis.get('ride-'+data['user_id']))
            if data.get('driver_location'):
                ride_data.update({'eta':data['eta'], 'driver_location':data['driver_location']})
            ride_data.update({'eta':data['eta']})
            await redis.set('ride-'+data['user_id'], json.dumps(ride_data))



# Class for handling payment related events
class PaymentConsumerCallback:

    # Handle ride payment success
    async def ride_payment_success(self, data):
        ride_id= data['ride_id']
        query= Ride.update().where(Ride.c.id==ride_id).values(paid=True)
        await database.execute(query)



# Class for handling driver related events
class DriverConsumerCallback:

    # Handle driver confirmed ride request
    async def  driver_ride_confirmed(self, redis, data):
        user_id= data['user_id']
        query= Ride.insert().values(**data)
        await database.execute(query)
        ride_data= json.loads(await redis.get('ride-'+user_id))

        '''consider scenario where ETA hasn`t arrived in the redis database. But the driver`s location will be updated every approx. 30 seconds so the eta should be fixed after say approx. 30 seconds '''
        
        #start= datetime.now()
        # while ride_data.get('eta')==None and datetime.now()-start<timedelta(seconds=20):
        #     asyncio.sleep(10)
        #     ride_data= json.loads(await redis.get('ride-'+user_id))
        # if ride_data.get('eta') == None:
        #     ride_data.update({'eta':'error'})
        await redis.delete('ride-'+user_id)
        await send_websocket_data(user_id, ride_data)



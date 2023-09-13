from .models import Driver, Driver_Status, Ride, Ride_Status
from .consumers import database
from .producers import publish_driver_new_ride_request, publish_find_new_driver
from datetime import datetime
import pytz
import json


# Class for handling ride related events
class RideConsumerCallback:

    async def ride_confirmed_user(self, channel, redis, data):
        # Handle user ride confirmation
        driver_id=data['driver_id']
        driver_request= await redis.get('ride-request-'+driver_id)
        if driver_request:
            await publish_find_new_driver(channel, data)
        else:
            await redis.set('ride-request-'+driver_id, json.dumps(data))
            query= Driver.update().where(Driver.c.id==data['driver_id']).values(status=Driver_Status.matched)
            await database.execute(query)
            await publish_driver_new_ride_request(channel, data)

    async def ride_canceled(self, redis, data):
        # Handle ride cancellation
            if data.get('driver_id'):
                query= Ride.update().where(Ride.c.id==data['ride_id']).values(status=Ride_Status.canceled, fare=data.get('fare'), date=datetime.now(tz=pytz.timezone('UTC')))
                await database.execute(query)
                query= Driver.update().where(Driver.c.id==data['driver_id']).values(status=Driver_Status.available)
                await database.execute(query)
            await redis.delete('ride-request-'+data['driver_id'])

# Class for handling tracking related events
class TrackingConsumerCallback:

    async def tracking_ride_in_transit(self,data):
        # Handle ride in transit
        ride_id= data['ride_id']
        query= Ride.update().where(Ride.c.id==ride_id).values(status=Ride_Status.in_transit)
        await database.execute(query)
        query= Driver.update().where(Driver.c.id==data['driver_id']).values(status=Driver_Status.in_transit)
        await database.execute(query)

    async def tracking_ride_arrived(self,data):
        # Handle ride arrived
        ride_id= data['ride_id']
        query= Ride.update().where(Ride.c.id==ride_id).values(status=Ride_Status.arrived)
        await database.execute(query)
        query= Driver.update().where(Driver.c.id==data['driver_id']).values(status=Driver_Status.arrived)
        await database.execute(query)


    async def tracking_ride_completed(self,data):
        # Handle ride completed
        ride_id= data['ride_id']
        query= Ride.update().where(Ride.c.id==ride_id).values(status=Ride_Status.completed, date=datetime.now(tz=pytz.timezone('UTC')))
        await database.execute(query)
        query= Driver.update().where(Driver.c.id==data['driver_id']).values(status=Driver_Status.available)
        await database.execute(query)


# Class for handling payment related events
class PaymentConsumerCallback:

    async def payment_succesful(self,data):
        # Handle payment successful
        ride_id= data['ride_id']
        query= Ride.update().where(Ride.c.id==ride_id).values(paid=True)
        await database.execute(query)
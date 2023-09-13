
from datetime import datetime
import pytz
from .models import Ride, Ride_Status
from .consumers import database

# Class for handling driver related events
class DriverConsumerCallback:

    # Handle driver confirmed ride request
    async def driver_confirmed_ride_request(self, data):
        query= Ride.insert().values(**data)
        await database.execute(query)



# Class for handling ride related events
class RideConsumerCallback:

    # Handle ride canceled
    async def ride_canceled(self, data):
        if data.get('driver_id'):
            query= Ride.update().where(Ride.c.id==data['ride_id']).values(status=Ride_Status.canceled, fare=data['fare'])
            await database.execute(query)
    



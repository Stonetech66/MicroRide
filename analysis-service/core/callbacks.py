from .producers import publish_ride_fare_calculated
from .analyzers import get_random_fare


# Class for handling ride related events
class RideConsumerCallback:

    async def find_ride_fare(self,channel, data):
        # Handle find ride fare
        ride_id= data['ride_id']
        analyzed_ride={'ride_id':ride_id, 'user_id':data['user_id'],'fare':get_random_fare()}
        await publish_ride_fare_calculated(channel, analyzed_ride)
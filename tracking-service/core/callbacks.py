from .database import driver_collection, ride_collection, driver_tracking_collection
from .utils import get_driver_eta, get_nearest_driver
from .producers import publish_driver_eta, publish_nearest_driver, publish_ride_eta_updated
from datetime import datetime
import pytz

# Class for handling driver related events
class DriverConsumerCallback:
    # Initialize class with database collections
    driver_collection= driver_collection
    ride_collection= ride_collection
    driver_tracking_collection= driver_tracking_collection

    async def driver_created(self, data):
        # Handle driver creation
        await self.driver_collection.insert_one(data)

    async def driver_confirmed_ride(self, data):
        # Handle driver confirming ride
        await self.ride_collection.insert_one(data)
        await self.driver_collection.update_one({'id':data['driver_id']}, {'$set':{'status':'on_pickup'}})            

    async def driver_status_updated(self, data):  
        # Handle driver status updates
        await self.driver_collection.update_one({'id':data['driver_id']}, {'$set':{'status':data['status']}})
        
    async def driver_find_eta(self,  channel, data,):  
        # Find and publish driver ETA and location
        eta, location=await get_driver_eta(data['driver_id'], destination_coordinates=(data['lat'], data['lon']), return_current_location=True)
        await publish_driver_eta(channel, {'eta':eta, 'user_id':data['user_id'], 'driver_location':location })

    async def driver_reject_ride(self, channel,  data,):    
        # Handle driver rejecting a ride and finding a replacement driver
        location=data['pickup_location']
        driver_rejecting=data['driver_id']
        new_driver=await get_nearest_driver(location, driver_rejecting)
        if new_driver:
            # Publish information about the replacement driver
            data.update({'driver':new_driver})
            await publish_nearest_driver(channel, data)
            await driver_collection.update_one({'id':new_driver['driver_id']}, {'$set':{'status':'matched'}})
            await driver_tracking_collection.find_one_and_update({'driver_id':new_driver['driver_id']}, {'$set':{'status':'matched'}},  projection={'_id':1}, sort=[('timestamp', -1)])
            await driver_collection.update_one({'id':driver_rejecting}, {'$set':{'status':'available'}})
        else:
            new_driver=None
            data.update({'driver':new_driver})
            await publish_nearest_driver(channel, data)
            await driver_collection.update_one({'id':driver_rejecting}, {'$set':{'status':'available'}})

    async def driver_find_new_driver(self,  channel, data,):  
        # Handle finding a new driver when the previous one is unavailable/matched
        location=data['pickup_location']
        driver_already_matched=data['driver_id']
        new_driver=await get_nearest_driver(location, driver_already_matched)
        if new_driver:
            data.update({'driver':new_driver})
            await publish_nearest_driver(channel, data)
            await driver_collection.update_one({'id':new_driver['driver_id']}, {'$set':{'status':'matched'}})
            await driver_tracking_collection.find_one_and_update({'driver_id':new_driver['driver_id']}, {'$set':{'status':'matched'}},  projection={'_id':1}, sort=[('timestamp', -1)])
        else:
            new_driver=None
            data.update({'driver':new_driver})
            await publish_nearest_driver(channel, data)


# Class for handling ride related events
class RideConsumerCallback:
    # Initialize class with database collections
    driver_collection= driver_collection
    ride_collection= ride_collection
    driver_tracking_collection= driver_tracking_collection

    async def ride_canceled(self, data):
        # Handle ride cancellation
        if data.get('driver_id'):
            await ride_collection.update_one({'id':data['ride_id']}, {'$set':{'status':'canceled'}})
            await driver_collection.update_one({'id':data['driver_id']}, {'$set':{'status':'available'}})
            await driver_tracking_collection.find_one_and_update({'driver_id':data['driver_id']}, {'$set':{'status':'available'}},  projection={'_id':1}, sort=[('timestamp', -1)])

    async def ride_find_nearest_driver(self, channel, data):
            # Find and publish the nearest driver for a ride
            location=data['pickup_location']
            driver=await get_nearest_driver(location)
            if driver:
                data.update({'driver':driver})
                await publish_nearest_driver(channel, data)
                await driver_collection.update_one({'id':driver['driver_id']}, {'$set':{'status':'matched'}})
                await driver_tracking_collection.find_one_and_update({'driver_id':driver['driver_id']}, {'$set':{'status':'matched'}},  projection={'_id':1}, sort=[('timestamp', -1)])
            else:
                driver=None
                data.update({'driver':driver})
                await publish_nearest_driver(channel, data)

# Class for handling tracking related events
class TrackingConsumerCallback:
    # Initialize class with database collections
    driver_collection= driver_collection
    ride_collection= ride_collection
    driver_tracking_collection= driver_tracking_collection

    async def tracking_driver_location_updated(self, channel, data):
        # Handle driver location updates and ETA calculations
        status=data['status']
        await driver_tracking_collection.insert_one({'driver_id':data['driver_id'], 'location':{'type':'Point', 'coordinates':[data['location']['lon'],data['location']['lat'] ]}, 'timestamp':datetime.now(tz=pytz.timezone('UTC')), 'status':status})
        if status == 'in_transit':
            ride=await ride_collection.find_one({'driver_id':data['driver_id'], 'status':'in_transit'}, projection={'_id':0})
            if ride:
                eta=await get_driver_eta(data['driver_id'], driver_current_coordinates=(data['location']['lat'],data['location']['lon'] ), destination_coordinates=(ride['destination'][1],ride['destination'][0] ) )
                ride['eta']=eta
                ride['driver_location']=[data['location']['lon'],data['location']['lat']] 
                await publish_ride_eta_updated(channel, ride )
        elif status== 'on_pickup':
            ride=await ride_collection.find_one({'driver_id':data['driver_id'], 'status':'confirmed'}, projection={'_id':0})
            if ride:
                eta=await get_driver_eta(data['driver_id'], driver_current_coordinates=(data['location']['lat'],data['location']['lon'] ), destination_coordinates=(ride['pickup_location'][1],ride['pickup_location'][0] ) )
                ride['eta']=eta 
                ride['driver_location']=[data['location']['lon'],data['location']['lat']] 
                await publish_ride_eta_updated(channel, ride )
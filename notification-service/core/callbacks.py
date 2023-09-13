from .websockets import WebsocketManager
from datetime import datetime
import pytz
from .database import driver_collection
import json

websocket_manager=WebsocketManager()


# Class for handling tracking related events
class TrackingConsumerCallback:

    async def tracking_ride_update_eta(self, redis,user_id,  data):
        # Handle ride ETA  updates
        event= 'ride-eta'
        data['ride_id']=data['id']
        data.pop('id')
        await websocket_manager.send_user_websocket_data(data['user_id'], event, data, redis, update_cache_data=True)        
        await websocket_manager.send_driver_websocket_data(data['driver_id'], event, data, redis, update_cache_data=True)
    async def tracking_ride_in_transit(self,redis, user_id, data):
        # Handle ride in transit
        event= 'ride-in_transit'
        await websocket_manager.send_user_websocket_data(str(user_id), event, data, redis, update_cache_data= True)
        await websocket_manager.send_driver_websocket_data(str(data['driver_id']), event, data, redis, update_cache_data=True)

    async def tracking_ride_arrived(self,redis, user_id, data):
        # Handle ride arrived
        event='ride-arrived'
        await websocket_manager.send_user_websocket_data(str(user_id), event, data, redis, update_cache_data=True)
        await websocket_manager.send_driver_websocket_data(str(data['driver_id']), event, data, redis, update_cache_data=True)

    async def tracking_ride_completed(self,redis, user_id, data):
        # Handle ride completed
        event= 'ride-completed'
        await websocket_manager.send_user_websocket_data(str(user_id), event, data, redis, clear_cache_data=True)
        await websocket_manager.send_driver_websocket_data(str(data['driver_id']), event, data, redis, clear_cache_data=True)

    async def tracking_nearest_driver(self, redis, user_id, data):
        # Handle tracking nearest driver update
        if not data.get('driver_id'):
            await websocket_manager.delete_user_websocket_event(redis, user_id)



# Class for handling driver related events
class DriverConsumerCallback:
    # Initialize class with database collections
    driver_collection= driver_collection

    async def driver_created(self, redis,  data):
        # Handle driver creation event
        await self.driver_collection.insert_one(data)

    async def driver_confirmed_ride(self, redis, data):
        # Handle driver confirming ride event
        event='comfirmed-ride-request'
        data['event']=event
        data['ride_id']=data['id']
        data.pop('id')
        await websocket_manager.update_driver_websocket_event(redis, json.dumps(data), str(data['driver_id']),)        

    async def driver_rejected_ride(self,redis, data): 
        # Handle driver rejecting ride event 
        driver_id=data['driver_id']
        await websocket_manager.delete_driver_websocket_event(redis, driver_id)
    
    async def driver_new_ride_request(self, redis, data,):  
        # Handle driver new ride request
        event='new-ride-request'
        await websocket_manager.send_driver_websocket_data(str(data['driver_id']), event, data, redis, update_cache_data=True)
        



# Class for handling ride related events
class RideConsumerCallback:

    async def ride_canceled(self, redis, data):
        # Handle ride cancellation events
        driver_id=data.get('driver_id')
        event='ride-canceled'
        await websocket_manager.send_user_websocket_data(data['user_id'], event, data, redis, clear_cache_data=True)
        await websocket_manager.send_driver_websocket_data(str(driver_id), event, data, redis, clear_cache_data=True)

    async def ride_find_nearest_driver(self, redis, data):
        # Handle find nearest driver
        event='searching-for-nearest-ride'
        data['event']=event 
        await websocket_manager.update_user_websocket_event(redis, json.dumps(data), data['user_id'])


# Class for handling payment related events
class PaymentConsumerCallback:

    async def ride_payment_success(self, redis, user_id, data):
        # Handle ride payment success
        event='payment-succesful'
        await websocket_manager.send_user_websocket_data(str(user_id), event, data, redis)
        await websocket_manager.send_driver_websocket_data(str(data['driver_id']), event, data, redis)

    async def ride_payment_failed(self, redis, user_id,  data):
        # Handle ride payment failed
        event='payment-failed'
        await websocket_manager.send_user_websocket_data(str(user_id), event, data, redis, update_cache_data=True)
from .producers import publish_driver_arrived, publish_ride_completed, publish_ride_in_transit, publish_update_driver_location
import json

# Handles ride in transit
async def background_task_ride_in_transit(driver_id, ride_id, user_id):
    await publish_ride_in_transit({'driver_id':driver_id, 'ride_id':ride_id, 'user_id':user_id})

# Handles ride completed
async def background_task_ride_completed(driver_id, ride_id, user_id):
    await publish_ride_completed({'driver_id':driver_id, 'ride_id':ride_id, 'user_id':user_id})

# Handles driver arrived
async def background_task_driver_arrived(driver_id, ride_id, user_id):
    await publish_driver_arrived({'driver_id':driver_id, 'ride_id':ride_id,'user_id':user_id})

# Handles driver location updates
async def background_task_update_driver_location(driver_id, lat, lon, status):
   await publish_update_driver_location({'driver_id':driver_id, 'location':{'lat':lat, 'lon':lon}, 'status':status})


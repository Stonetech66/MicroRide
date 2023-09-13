from .producers import publish_find_nearest_ride, publish_ride_canceled, publish_get_ride_fare
import json

# Handle find ride request
async def background_task_find_ride(redis, ride_data, user_id):
    # Store the ride data in redis
    await redis.set('ride-'+str(user_id), json.dumps(ride_data))
    # Publish get ride fare
    await publish_get_ride_fare(ride_data)

# Handle cancel ride request
async def background_task_cancel_ride(redis, data:dict):
    # Delete the ride data in redis
    await redis.delete('ride-'+str(data.get('user_id')))
    # Publish ride canceled
    await publish_ride_canceled(data)

# Handle ride request confirmed
async def background_task_confirm_ride(redis, ride_data, user_id):
    # Store the ride data in redis
    await redis.set('ride-'+str(user_id), json.dumps(ride_data))
    # Publish find nearest ride to the user
    await publish_find_nearest_ride(ride_data)


    
    



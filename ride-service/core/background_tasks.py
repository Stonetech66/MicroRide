from .producers import publish_find_nearest_ride, publish_ride_canceled, publish_ride_confirmed, publish_get_ride_fare


async def background_task_find_ride(redis, ride_data, user_id):
    await redis.hset('ride-'+str(user_id), mapping=ride_data)
    await publish_find_nearest_ride(ride_data)
    await publish_get_ride_fare(ride_data)
    

async def background_task_cancel_ride(data:dict):
    await publish_ride_canceled(data)


async def background_task_confirm_ride(redis, ride_data, user_id):
    await publish_ride_confirmed({**ride_data, 'status':'confirmed'})
    await redis.delete('ride-'+str(user_id))
    



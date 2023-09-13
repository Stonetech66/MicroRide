from .producers import publish_find_ride_eta, publish_ride_confirmed_driver, publish_ride_rejected, publish_driver_created, publish_driver_status_updated


# Handle driver accept ride request
async def background_task_accept_ride(ride_request, driver_id, redis):
    # Delete ride request from redis database
    await redis.delete('ride-request-'+driver_id,)

    # Publish find ride ETA and driver confirmed/accepted ride
    await publish_find_ride_eta({'driver_id':driver_id, 'lon':ride_request['pickup_location'][0], 'lat':ride_request['pickup_location'][1], 'user_id':ride_request['user_id']})
    await publish_ride_confirmed_driver({**ride_request, 'status':'confirmed'})
    

# Handle driver reject ride request
async def background_task_reject_ride(ride_request, driver_id, redis):
    # Delete ride request from redis database
    await redis.delete('ride-request-'+driver_id,)

    # Publish ride rejected
    await publish_ride_rejected(ride_request)
    
# Handle driver status updates
async def background_task_driver_status_updated(driver_id, driver_status):
    await publish_driver_status_updated({'driver_id':driver_id, 'status':driver_status})
    
# Handle driver created
async def background_task_driver_created(data, driver_id, user_id):
    await publish_driver_created({**data, 'id':driver_id, 'user_id':user_id, 'status':'unavailable'})
    
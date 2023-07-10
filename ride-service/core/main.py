from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from .database import  database
from .schema import RideBase, RideDetails
from .dependencies import get_current_user
import uuid
import aioredis
from .crud import RideCrud
from .background_tasks import background_task_find_ride, background_task_cancel_ride, background_task_confirm_ride


app= FastAPI()


redis= None
@app.on_event('startup')
async def startup():
    await database.connect()
    global redis
    redis= await  aioredis.from_url('redis://localhost', decode_responses=True)
    


@app.on_event('shutdown')
async def shutdown():
    global redis
    await database.disconnect()
    await redis.close()



NOTIFICATION_SERVICE_URL=''


@app.get('/rides/', response_model=list[RideDetails])
async def get_past_rides(user_id=Depends(get_current_user) ):
    rides=await RideCrud.get_past_rides(database, user_id)
    return rides

@app.get('/rides/{ride_id}', response_model=RideDetails)
async def get_past_ride(ride_id:str,  user_id=Depends(get_current_user)):
        ride= await RideCrud.get_ride_details(database, user_id, ride_id)
        if not ride:
             raise HTTPException(detail='ride no found', status_code=404)
        return ride


@app.post('/rides/')
async def find_ride(schema:RideBase,task:BackgroundTasks,  user_id=Depends(get_current_user), ):
    ride= await RideCrud.get_user_has_active_ride(database,user_id)
    if ride:
        raise HTTPException(detail='confirmed/in_transit ride detected, cancel or complete ride to book a new ride', status_code=400)
    ride_id=str(uuid.uuid4())
    ride_data= {'ride_id':ride_id, 'user_id':user_id, **schema.dict()}
    task.add_task(background_task_find_ride, redis, ride_data, user_id)
    return {
        'message':'connect to the websocket url to get notified when the closest driver has been found and other ride events',
        'websocket_url':f'{NOTIFICATION_SERVICE_URL}/ride/{user_id}',
        }

@app.post('/rides/{ride_id}/confirm')
async def confirm_ride(task:BackgroundTasks, ride_id:str,  user_id=Depends(get_current_user), ):
    ride_data= await redis.hgetall('ride-'+str(user_id))
    if not ride_data:
        raise HTTPException(detail='ride not found', status_code=404)
    ride_data.update({'id':ride_data['ride_id']})
    ride_data.pop('ride_id')
    driver_id= ride_data.get('driver_id')
    if driver_id == 'no drivers':
        return {'message':'no driver found'}
    await RideCrud.create_ride(database, ride_data)
    task.add_task(background_task_confirm_ride, redis, ride_data, user_id )
    return {'message':'ride confirmed', 'driver_id':driver_id}


@app.post('/rides/{ride_id}/cancel')
async def cancel_ride(ride_id:str,task:BackgroundTasks,  user_id=Depends(get_current_user), ):
        fare, driver_id= await RideCrud.cancel_ride(database, user_id, ride_id)
        task.add_task(background_task_cancel_ride, {'ride_id':ride_id, 'fare':fare, 'driver_id':driver_id, 'user_id':user_id})
        return {'message':'ride canceled'}





                






from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from .database import  database
from .schemas import RideDetails, BookRide
from .dependencies import get_current_user
import uuid
import aioredis
from .crud import RideCrud
import os
import json 
from . import background_tasks as bg_tasks
from fastapi.middleware.cors import CORSMiddleware

app= FastAPI(title='MicroRide ride-service')

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*']      
    )


# Construct Redis URL from enviromental variable
REDIS_HOST= os.getenv('REDIS_HOST')
REDIS_URL= f'redis://{REDIS_HOST}'
redis= None



NOTIFICATION_SERVICE_HOST=os.getenv('NOTIFICATION_SERVICE_HOST')


# Defines functions for application to run before startup
@app.on_event('startup')
async def startup():
    # Connect to database
    await database.connect()
    global redis
    # Connect to redis
    redis= await  aioredis.from_url(REDIS_URL, decode_responses=True)
    

# Defines functions for application to run before shutdown
@app.on_event('shutdown')
async def shutdown():
    global redis

    # Connect to database
    await database.disconnect()
    # Disconnect to redis
    await redis.close()


# Root route for probing the application during startup
@app.get('/')
async def app_probe():
    return {'message':'success'}

# Endpoint to get user past rides
@app.get('/api/v1/rides/', response_model=list[RideDetails], summary='Endpoint to get user past rides')
async def get_past_rides(user_id=Depends(get_current_user) ):
    rides=await RideCrud.get_past_rides(database, user_id)
    return rides

# Endpoint to get details of a past ride
@app.get('/api/v1/rides/{ride_id}', response_model=RideDetails, summary='Endpoint to get details of a past ride')
async def get_past_ride(ride_id:str,  user_id=Depends(get_current_user)):
        ride= await RideCrud.get_ride_details(database, user_id, ride_id)
        if not ride:
             raise HTTPException(detail='ride not found', status_code=404)
        return ride

# Endpoint to find a ride 
@app.post('/api/v1/rides/', summary='Endpoint to find a ride ')
async def find_ride(schema:BookRide,task:BackgroundTasks,  user_id=Depends(get_current_user), ):
    ride= await RideCrud.get_user_has_active_ride(database,user_id, redis)
    if ride:
        raise HTTPException(detail='confirmed/in_transit ride detected, cancel or complete ride to book a new ride', status_code=400)
    ride_id=str(uuid.uuid4())
    ride_data= {'ride_id':ride_id, 'user_id':user_id, 'destination':[schema.destination.lon, schema.destination.lat], 'pickup_location':[schema.pickup_location.lon, schema.pickup_location.lat]}
    task.add_task(bg_tasks.background_task_find_ride, redis, ride_data, user_id)
    return {
        'message':'connect to the websocket url to listen for ride events ride events',
        'websocket_url':'/notification-service/user?token=jwt-credential',
        }

# Endpoint to confirm a ride request
@app.post('/api/v1/rides/{ride_id}/confirm', summary='Endpoint to confirm a ride request')
async def confirm_ride(task:BackgroundTasks, ride_id:str,  user_id=Depends(get_current_user), ):
    ride_data=await redis.get('ride-'+str(user_id))
    if not ride_data:
        raise HTTPException(detail='ride not found', status_code=404)
    ride_data=json.loads(ride_data)
    if ride_data.get('status')=='confirmed':
        return {'message':'ride already confirmed. searching for driver',
            'websocket_url':'/notification/user?token=jwt-credential'}
    ride_data['status']='confirmed'
    task.add_task(bg_tasks.background_task_confirm_ride, redis, ride_data, user_id )
    return {'message':'ride confirmed. searching for driver',
            'websocket_url':'/notification/user?token=jwt-credential'}

# Endpoint to cancel a ride request
@app.post('/api/v1/rides/{ride_id}/cancel', summary='Endpoint to cancel a ride request')
async def cancel_ride(ride_id:str,task:BackgroundTasks,  user_id=Depends(get_current_user), ):
        cancel_data= await RideCrud.cancel_ride(database, user_id, ride_id, redis)
        task.add_task(bg_tasks.background_task_cancel_ride,redis,  {'ride_id':ride_id, **cancel_data, 'user_id':user_id})
        return {'message':'ride canceled'}





                






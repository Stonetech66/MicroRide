from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from .dependencies import get_current_user, get_user_is_registered_driver
from sqlalchemy import select, join, or_
import uuid
from .database import database
from .models import Driver, Ride, Ride_Status, Driver_Status
from .schemas import DriverCreate, DriverDetails, RideDetails, UpdateStatusEnum, RideSchema
from asyncpg.exceptions import UniqueViolationError
import json
import os
import aioredis
from . import background_tasks as bg_tasks
from fastapi.middleware.cors import CORSMiddleware


app= FastAPI(title='MicroRide driver-service')

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
    
    # Disconnect to database
    await database.disconnect()
    # Disconnect to redis
    await redis.close()


# Root route for probing the application during startup
@app.get('/')
async def app_probe():
    return {'message':'success'}

# Endpoint to create driver profile
@app.post('/api/v1/profile', summary='Endpoint to create driver profile')
async def create_driver_profile(schema:DriverCreate,task:BackgroundTasks, user_id=Depends(get_current_user)):
    driver_id=str(uuid.uuid4())
    data= schema.dict()
    query= Driver.insert().values(**data, user_id=user_id, id=driver_id)
    try:
        await database.execute(query)
    except UniqueViolationError:
        raise HTTPException(detail='user already has a driver profile', status_code=400)
    task.add_task(bg_tasks.background_task_driver_created, data, driver_id, user_id)
    return {'message':'driver profile sucessfuly created'}

# Endpoint to create get driver`s profile
@app.get('/api/v1/profile', response_model=DriverDetails, summary='Endpoint to get driver`s profile')
async def get_driver_profile(driver=Depends(get_user_is_registered_driver)):
    return driver

# Endpoint to get a driver details
@app.get('/api/v1/drivers/{driver_id}', response_model=DriverDetails, summary='Endpoint to get a driver details')
async def get_driver(driver_id:str,):
    query= select(Driver).where(Driver.c.id==driver_id)
    driver=await database.fetch_one(query)
    if not driver:
            raise HTTPException(detail='driver not found', status_code=404)
    return driver

# Endpoint to get driver`s past rides
@app.get('/api/v1/rides', response_model=list[RideDetails], summary='Endpoint to get driver`s past rides')
async def get_driver_past_rides( user_id=Depends(get_current_user), driver=Depends(get_user_is_registered_driver)):
    query= select(Ride).select_from(join(Ride,Driver, Driver.c.id==Ride.c.driver_id)).where(Driver.c.user_id==user_id,  or_(Ride.c.status==Ride_Status.canceled, Ride.c.status==Ride_Status.completed))
    rides=await database.fetch_all(query)
    return rides

# Endpoint to update driver`s availability status
@app.put('/api/v1/status', summary='Endpoint to update driver`s availability status')
async def update_driver_status(driver_status:UpdateStatusEnum,task:BackgroundTasks, driver=Depends(get_user_is_registered_driver)):
    if driver.status not in ('available', 'unavailable'):
        raise HTTPException(detail='can`t update status currently have an active ride or ride request', status_code=400)
    query= Driver.update().where(Driver.c.id==driver.id).values(status=driver_status)
    await database.execute(query)
    task.add_task(bg_tasks.background_task_driver_status_updated, driver.id, driver_status)
    return {'message':'status updated successfully'}

# Endpoint to accept ride request
@app.post('/api/v1/rides/accept', summary='Endpoint to accept ride request')
async def accept_ride(ride_id:RideSchema, task:BackgroundTasks, driver=Depends(get_user_is_registered_driver)):
    try:
        ride_request=json.loads(await redis.get('ride-request-'+driver.id,))  
    except TypeError: # if the ride_request is None
        raise HTTPException(detail='ride not found', status_code=404)
    if not ride_request.get('ride_id')==ride_id.ride_id:
        raise HTTPException(detail='ride not found', status_code=404)
    ride_request['id']=ride_request['ride_id']
    ride_request.pop('ride_id')
    try:
        async with database.transaction():
            ride_query= Ride.insert().values(**ride_request)
            await database.execute(ride_query)
            driver_query= Driver.update().where(Driver.c.id==ride_request['driver_id']).values(status=Driver_Status.on_pickup)
            await database.execute(driver_query)
    except:
        raise HTTPException(detail='error occured try again', status_code=500)
    task.add_task(bg_tasks.background_task_accept_ride, ride_request, driver.id, redis)
    return {'message':'ride request confirmed'}

# Endpoint to reject ride request
@app.post('/api/v1/rides/reject',summary='Endpoint to reject ride request' )
async def reject_ride(ride_id:RideSchema, task:BackgroundTasks,  driver=Depends(get_user_is_registered_driver)):
    try:
        ride_request=json.loads(await redis.get('ride-request-'+driver.id,))  
    except TypeError: # if the ride_request is None
        raise HTTPException(detail='ride not found', status_code=404)
    if not ride_request.get('ride_id')==ride_id.ride_id:
        raise HTTPException(detail='ride not found', status_code=404)
    driver_query= Driver.update().where(Driver.c.id==ride_request['driver_id']).values(status=Driver_Status.available)
    await database.execute(driver_query)
    task.add_task(bg_tasks.background_task_reject_ride, ride_request, driver.id, redis)
    return {'message':'ride succesfully rejected'}


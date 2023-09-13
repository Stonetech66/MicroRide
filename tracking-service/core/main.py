from fastapi import FastAPI, Depends,HTTPException, BackgroundTasks
from .dependencies import get_current_user, get_user_is_registered_driver
from .database import ride_collection, driver_collection, driver_tracking_collection
from .schemas import Location
from .database import create_index
from . import background_tasks as bg_tasks
from fastapi.middleware.cors import CORSMiddleware

app= FastAPI(title='MicroRide tracking-service')

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*']      
    )

# Defines functions for application to run before startup
@app.on_event('startup')
async def startup():
    await create_index()

# Root route for probing the application during startup
@app.get('/')
async def app_probe():
    return {'message':'success'}


# Endpoint to mark a ride as completed
@app.post('/api/v1/rides/{ride_id}/completed/', summary='Endpoint to mark a ride as completed')
async def send_ride_completed(ride_id:str, task:BackgroundTasks,  driver_id=Depends(get_user_is_registered_driver)):
    # Check if the ride exists and is assigned to the driver
    ride=await ride_collection.find_one({'id':ride_id, 'driver_id':driver_id}, projection={'user_id':1, '_id':0, 'status':1})
    if not ride:
        raise HTTPException(detail='ride not found', status_code=404)
    elif ride['status'] == 'canceled':
        raise HTTPException(detail='ride already canceled', status_code=400)
    
    # Update ride status to 'completed' and driver status to 'available'
    await ride_collection.update_one({"id": ride_id},{"$set":{'status':'completed'}})
    await driver_collection.update_one({'id':driver_id},{ '$set':{'status':'available'}})

    # Execute a background task for ride completion
    task.add_task(bg_tasks.background_task_ride_completed,driver_id, ride_id, ride['user_id'])
    return {'message':'success'}

# Endpoint to mark a ride as in transit
@app.post('/api/v1/rides/{ride_id}/in-transit/',summary='Endpoint to mark a ride as in transit')
async def send_ride_in_transit(ride_id:str,task:BackgroundTasks, driver_id=Depends(get_user_is_registered_driver)):
    # Check if the ride exists and is assigned to the driver
    ride=await ride_collection.find_one({'id':ride_id, 'driver_id':driver_id,}, projection={'user_id':1, '_id':0, 'status':1})
    if not ride:
        raise HTTPException(detail='ride not found', status_code=404)
    elif ride['status'] == 'canceled':
        raise HTTPException(detail='ride already canceled', status_code=400)
    elif ride['status'] == 'completed':
        raise HTTPException(detail='ride already completed', status_code=400)
    # Update ride status to 'in_transit' and driver status to 'in_transit'
    await ride_collection.update_one({"id": ride_id, },{"$set":{'status':'in_transit'}})
    await driver_collection.update_one({'id':driver_id}, {'$set':{'status':'in_transit'}})

    # Execute a background task for ride in transit
    task.add_task(bg_tasks.background_task_ride_in_transit, driver_id, ride_id, ride['user_id'])
    return {'message':'success'}

# Endpoint to mark a ride as arrived
@app.post('/api/v1/rides/{ride_id}/driver-arrived', summary='Endpoint to mark a ride as arrived')
async def send_ride_driver_arrived(ride_id:str,task:BackgroundTasks, driver_id=Depends(get_user_is_registered_driver)):
    # Check if the ride exists and is assigned to the driver
    ride=await ride_collection.find_one({'id':ride_id, 'driver_id':driver_id}, projection={'user_id':1, '_id':0, 'status':1})
    if not ride:
        raise HTTPException(detail='ride not found', status_code=404)
    elif ride['status'] == 'canceled':
        raise HTTPException(detail='ride already canceled', status_code=400)
    elif ride['status'] == 'in_transit':
        raise HTTPException(detail='ride already in_transit', status_code=400)
    elif ride['status'] == 'completed':
        raise HTTPException(detail='ride already completed', status_code=400)
    # Update ride status to 'arrived' and driver status to 'arrived'
    await ride_collection.update_one({"id": ride_id, },{"$set":{'status':'arrived'}})
    await driver_collection.update_one({'id':driver_id},{"$set":{'status':'arrived'}})

    # Execute a background task for ride driver arrived
    task.add_task(bg_tasks.background_task_driver_arrived,driver_id, ride_id, ride['user_id'] )
    return {'message':'success'}

# Endpoint to update the driver`s location
@app.put('/api/v1/driver/location', summary='Endpoint to update the driver`s location')
async def update_driver_location(location:Location, task:BackgroundTasks, driver_id:str):
    # Check if the ride exists and is assigned to the driver
    driver=await driver_collection.find_one({'id':driver_id}, projection={'user_id':1, '_id':0, 'status':1})
    if not driver:
        raise HTTPException(detail='driver not found', status_code=404)
    
    # Execute a background task toupdate driver`s location
    task.add_task(bg_tasks.background_task_update_driver_location, driver_id, location.lat, location.lon, driver['status'])
    return {'message':'success'}




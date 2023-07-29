from fastapi import FastAPI, Depends, HTTPException
from .dependencies import get_current_user, get_user_is_driver
from sqlalchemy import select, join, or_
import uuid
from .database import database
from .models import Driver, Ride, Ride_Status, Driver_Status
from .schema import DriverCreate, DriverDetails, RideDetails, UpdateStatus
from .producers import publish_driver_created, publish_driver_status_updated
app= FastAPI()



@app.on_event('startup')
async def startup():
    await database.connect()

@app.on_event('shutdown')
async def shutdown():
    await database.disconnect()

@app.get('/')
async def app_probe():
    return {'message':'success'}


@app.post('/api/v1/drivers')
async def create_driver_profile(schema:DriverCreate,user_id=Depends(get_current_user)):
    driver_id=str(uuid.uuid4())
    data= schema.dict()
    query= Driver.insert().values(**data, user_id=user_id, id=driver_id)
    try:
        await database.execute(query)
    except:
        raise HTTPException(detail='user already has a driver profile', status_code=400)
    await publish_driver_created({**data, 'id':driver_id, 'user_id':user_id})
    return {'message':'driver profile sucessfuly created'}


@app.get('/api/v1/drivers/profile', response_model=DriverDetails)
async def get_driver_profile(driver=Depends(get_user_is_driver)):
    return driver

@app.get('/api/v1/drivers/{driver_id}', response_model=DriverDetails)
async def get_driver(driver_id:str,):
    query= select(Driver).where(Driver.c.id==driver_id)
    driver=await database.fetch_one(query)
    return driver


@app.get('/api/v1/rides', response_model=list[RideDetails])
async def get_driver_past_rides( user_id=Depends(get_current_user), driver=Depends(get_user_is_driver)):
    query= select(Ride).select_from(join(Ride,Driver, Driver.c.id==Ride.c.driver_id)).where(Driver.c.user_id==user_id,  or_(Ride.c.status==Ride_Status.canceled, Ride.c.status==Ride_Status.completed))
    rides=await database.fetch_all(query)
    return rides

@app.put('/api/v1/status')
async def update_driver_status(driver_status:UpdateStatus, driver=Depends(get_user_is_driver)):
    query= Driver.update().where(Driver.c.id==driver.id).values(status=driver_status.status)
    await database.execute(query)
    await publish_driver_status_updated({'user_id':driver.user_id, 'status':driver_status.status})
    return {'message':'status updated successfully'}


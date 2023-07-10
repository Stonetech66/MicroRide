from fastapi import FastAPI, Depends, HTTPException
from .dependencies import get_current_user
from sqlalchemy import select, join, or_
import uuid
from .database import database
from .models import Driver, Ride, Ride_Status
from .schema import DriverCreate, DriverDetails, RideDetails
from .producers import publish_driver_created
app= FastAPI()



@app.on_event('startup')
async def startup():
    await database.connect()

@app.on_event('shutdown')
async def shutdown():
    await database.disconnect()



@app.post('/drivers')
async def create_driver_profile(schema:DriverCreate,user_id=Depends(get_current_user)):
    driver_id=str(uuid.uuid4())
    data= schema.dict()
    query= Driver.insert().values(**data, user_id=user_id, id=driver_id)
    try:
        await database.execute(query)
    except:
        raise HTTPException(detail='user already has a driver profile', status_code=400)
    data.update({'birth_date':str(data['birth_date'])})
    await publish_driver_created({**data, 'id':driver_id, 'user_id':user_id})
    return {'message':'driver profile sucessfuly created'}


@app.get('/drivers/profile', response_model=DriverDetails)
async def get_driver_profile(user_id=Depends(get_current_user)):
    query= select(Driver).where(Driver.c.user_id==user_id)
    driver=await database.fetch_one(query)
    if not driver:
        raise HTTPException(detail='user is not signed up as a driver', status_code=400)
    return driver

@app.get('/drivers/{driver_id}', response_model=DriverDetails)
async def get_driver(driver_id:str, user_id=Depends(get_current_user)):
    query= select(Driver).where(Driver.c.user_id==user_id)
    driver=await database.fetch_one(query)
    return driver


@app.get('/rides', response_model=list[RideDetails])
async def get_driver_past_rides( user_id=Depends(get_current_user)):
    query= select(Ride).select_from(join(Ride,Driver, Driver.c.id==Ride.c.driver_id)).where(Driver.c.user_id==user_id,  or_(Ride.c.status==Ride_Status.canceled, Ride.c.status==Ride_Status.completed))
    rides=await database.fetch_all(query)
    return rides
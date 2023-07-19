from fastapi import FastAPI, HTTPException
from .producers import publish_payment_success, publish_payment_failed
from .database import database
from sqlalchemy import select
from .models import Payment, Ride
from .schema import PaymentSchema

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

@app.post('/api/v1/payment/success/')
async def payment_success(schema:PaymentSchema):
    ride_query= select(Ride.c.id, Ride.c.paid, Ride.c.fare, Ride.c.user_id).where(Ride.c.id==schema.ride_id)
    ride= await database.fetch_one(ride_query)
    if not ride:
         raise HTTPException(detail='ride not found', status_code=404)
    if ride.paid== True:
        raise HTTPException(detail='ride already paid for', status_code=400)
    query= Payment.insert().values(ride_id=schema.ride_id, amount=ride.fare, user_id=ride.user_id)
    await database.execute(query)
    await publish_payment_success({**schema.dict(), 'user_id':ride.user_id, 'driver_id': ride.driver_id, 'amount':ride.fare})
    return {'message':'payment successful'}



@app.post('/api/v1/payment/failed/')
async def payment_failed(schema:PaymentSchema):
    ride_query= select(Ride.c.id, Ride.c.paid, Ride.c.fare, Ride.c.user_id).where(Ride.c.id==schema.ride_id)
    ride= await database.fetch_one(ride_query)
    if not ride:
         raise HTTPException(detail='ride not found', status_code=404)
    if ride.paid== True:
        raise HTTPException(detail='ride already paid for', status_code=400)
    await publish_payment_failed({**schema.dict(), 'user_id':ride.user_id})
    return {'message':'payment failed'}
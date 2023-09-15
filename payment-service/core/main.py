from fastapi import FastAPI, HTTPException
from .producers import publish_payment_success, publish_payment_failed
from .database import database
from sqlalchemy import select
from .models import Payment, Ride
from .schemas import PaymentSchema
from asyncpg.exceptions import UniqueViolationError
from fastapi.middleware.cors import CORSMiddleware

app= FastAPI(title='MicroRide payment-service')

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
    # Connect to database
    await database.connect()
# Defines functions for application to run before shutdown
@app.on_event('shutdown')
async def shutdown():
    # Disconnect to database
    await database.disconnect()

# Root route for probing the application during startup
@app.get('/')
async def app_probe():
    return {'message':'success'}

# Endpoint to simulate payment success
@app.post('/api/v1/payment/success/', summary='Endpoint to simulate payment success')
async def payment_success(schema:PaymentSchema):
    ride_query= select(Ride.c.id, Ride.c.fare, Ride.c.user_id).where(Ride.c.id==schema.ride_id)
    ride= await database.fetch_one(ride_query)
    if not ride:
         raise HTTPException(detail='ride not found', status_code=404)
    query= Payment.insert().values(ride_id=schema.ride_id, amount=ride.fare, user_id=ride.user_id)
    try:
        await database.execute(query)
    except UniqueViolationError:
        return {'message':'ride already paid for'}
    await publish_payment_success({'ride_id':schema.ride_id, 'user_id':ride.user_id, 'driver_id': ride.driver_id, 'amount':ride.fare})
    return {'message':'payment successful'}


# Endpoint to simulate payment success
@app.post('/api/v1/payment/failed/', summary='Endpoint to simulate payment failure')
async def payment_failed(schema:PaymentSchema):
    ride_query= select(Ride.c.id, Ride.c.user_id).where(Ride.c.id==schema.ride_id)
    ride= await database.fetch_one(ride_query)
    if not ride:
         raise HTTPException(detail='ride not found', status_code=404)
    await publish_payment_failed({'ride_id':schema.ride_id, 'user_id':ride.user_id})
    return {'message':'payment failed'}
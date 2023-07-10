from .models import Ride, Ride_Status
from sqlalchemy import or_,  select
from fastapi import HTTPException
from .utils import get_ride_canceled_fare


class RideCrud:

    async def get_past_rides(database,  user_id ):
        query= select(Ride).where(Ride.c.user_id== user_id , or_(Ride.c.status==Ride_Status.completed, Ride.c.status==Ride_Status.canceled))
        rides= await database.fetch_all(query)
        return rides
    
    async def get_ride_details(database,  user_id, ride_id):
        query= select(Ride).where(Ride.c.user_id ==  user_id, Ride.c.id== ride_id)
        ride= await database.fetch_one(query)
        return ride
    
    async def get_user_has_active_ride(database,  user_id):
        query= select(Ride.c.id).where(Ride.c.user_id == user_id,  or_(Ride.c.status== Ride_Status.confirmed, Ride.c.status== Ride_Status.in_transit))
        ride= await database.fetch_all(query)
        return ride
    
    async def create_ride(database, ride_data):
        query= Ride.insert().values(**ride_data, status=Ride_Status.confirmed)
        ride= await database.execute(query)
        return ride
    
    async def complete_ride(database,  ride_id, user_id):
        query= Ride.update().where(Ride.c.id==ride_id, Ride.c.user_id==user_id).values(status=Ride_Status.completed)
        ride= await database.execute(query)
        return ride
    
    async def cancel_ride(database,  user_id, ride_id):
        query=select(Ride.c.status, Ride.c.driver_id).where(Ride.c.id==ride_id, Ride.c.user_id==user_id)
        ride= await database.fetch_one(query)
        if not ride:
            raise HTTPException(detail='ride not found', status_code=404)
        if ride.status== Ride_Status.confirmed:
            fare = 0.0 
        elif ride.status== Ride_Status.in_transit:
            fare = get_ride_canceled_fare()
        elif ride.status== Ride_Status.arrived:
            fare = get_ride_canceled_fare()
        elif ride.status == Ride_Status.completed:
            raise   HTTPException(detail='cant cancel completed ride', status_code=400)
        elif ride.status == Ride_Status.canceled:
            raise   HTTPException(detail='ride already canceled', status_code=400)
        query= Ride.update().where(Ride.c.id==ride_id, Ride.c.user_id==user_id).values(status=Ride_Status.canceled, fare=fare)
        await database.execute(query)
        return fare, ride.driver_id
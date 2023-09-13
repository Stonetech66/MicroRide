from .models import Ride, Ride_Status
from sqlalchemy import or_,  select
from fastapi import HTTPException
from .utils import get_ride_canceled_fare
import json
from datetime import datetime 
import pytz


class RideCrud:

    # Return user's past rides that have been completed or canceled
    @staticmethod
    async def get_past_rides(database,  user_id ):
        query= select(Ride).where(Ride.c.user_id== user_id , or_(Ride.c.status==Ride_Status.completed, Ride.c.status==Ride_Status.canceled))
        rides= await database.fetch_all(query)
        return rides
    
    # Returns details of a particular ride
    @staticmethod
    async def get_ride_details(database,  user_id, ride_id):
        query= select(Ride).where(Ride.c.user_id ==  user_id, Ride.c.id== ride_id)
        ride= await database.fetch_one(query)
        return ride
    
    # Checks if user has a ride that has not been completed (confirmed/in_transit/arrived)
    @staticmethod
    async def get_user_has_active_ride(database,  user_id, redis):
        query= select(Ride.c.id).where(Ride.c.user_id == user_id,  or_(Ride.c.status== Ride_Status.confirmed, Ride.c.status== Ride_Status.arrived,  Ride.c.status== Ride_Status.in_transit, ))
        ride= await database.fetch_all(query)
        if ride:
            return ride
        active_ride_redis=await redis.get('ride-'+str(user_id))
        if active_ride_redis:
            active_ride_redis=json.loads(active_ride_redis)
            if active_ride_redis.get('status')=='confirmed':
                return active_ride_redis
            return None
    
    # Creates a Ride
    @staticmethod
    async def create_ride(database, ride_data):
        query= Ride.insert().values(**ride_data, status=Ride_Status.confirmed)
        ride= await database.execute(query)
        return ride
    
    # Marks a Ride as completed
    @staticmethod
    async def complete_ride(database,  ride_id, user_id):
        query= Ride.update().where(Ride.c.id==ride_id, Ride.c.user_id==user_id).values(status=Ride_Status.completed)
        ride= await database.execute(query)
        return ride
    
    # Marks a Ride as canceled
    @staticmethod
    async def cancel_ride(database, user_id, ride_id, redis):
        active_ride_redis=await redis.get('ride-'+str(user_id))
        if active_ride_redis:
            active_ride_redis=json.loads(active_ride_redis)
            if active_ride_redis.get('ride_id')==ride_id and active_ride_redis.get('status')=='confirmed':
                return {'driver_id':active_ride_redis.get('driver_id')}
            raise HTTPException(detail='ride not found', status_code=404)
        query=select(Ride.c.status, Ride.c.driver_id).where(Ride.c.id==ride_id, Ride.c.user_id==user_id)
        ride= await database.fetch_one(query)
        if not ride:
            raise HTTPException(detail='ride not found', status_code=404)
        if ride.status== 'confirmed':
            fare = 0.0 
        elif ride.status== 'in_transit':
            fare = get_ride_canceled_fare()
        elif ride.status== 'arrived':
            fare = get_ride_canceled_fare()
        elif ride.status == 'completed':
            raise   HTTPException(detail='cant cancel completed ride', status_code=400)
        elif ride.status == 'canceled':
            raise   HTTPException(detail='ride already canceled', status_code=400)
        query= Ride.update().where(Ride.c.id==ride_id, Ride.c.user_id==user_id).values(status=Ride_Status.canceled, fare=fare, date=datetime.now(tz=pytz.timezone('UTC')))
        await database.execute(query)
        return {'fare':fare, 'driver_id':ride.driver_id}
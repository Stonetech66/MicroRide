from fastapi import FastAPI, Depends, Body, HTTPException, WebSocket
from .dependencies import get_current_user
from .database import ride_table
from .producers import publish_driver_arrived, publish_ride_in_transit, publish_ride_completed


app= FastAPI()




@app.post('/rides/{ride_id}/completed/')
async def send_ride_completed(ride_id):
    ride=await ride_table.find_one({'id':ride_id})
    if not ride:
        raise HTTPException(detail='ride not found', status_code=404)
    elif ride['status'] == 'canceled':
        raise HTTPException(detail='ride already canceled', status_code=400)
    await ride_table.update_one({"id": ride_id},{"$set":{'status':'completed'}})
    await publish_ride_completed({'driver_id':ride['driver_id'], 'ride_id':ride['id'], 'user_id':ride['user_id']})
    return {'message':'success'}

@app.post('/rides/{ride_id}/in-transit/')
async def send_ride_in_transit(ride_id):
    ride=await ride_table.find_one({'id':ride_id})
    if not ride:
        raise HTTPException(detail='ride not found', status_code=404)
    elif ride['status'] == 'canceled':
        raise HTTPException(detail='ride already canceled', status_code=400)
    await ride_table.update_one({"id": ride_id, },{"$set":{'status':'in_transit'}})
    await publish_ride_in_transit({'driver_id':ride['driver_id'], 'ride_id':ride['id'], 'user_id':ride['user_id']})
    return {'message':'success'}

@app.post('/rides/{ride_id}/driver-arrived')
async def send_ride_driver_arrived(ride_id):
    ride=await ride_table.find_one({'id':ride_id})
    if not ride:
        raise HTTPException(detail='ride not found', status_code=404)
    elif ride['status'] == 'canceled':
        raise HTTPException(detail='ride already canceled', status_code=400)
    await ride_table.update_one({"id": ride_id, },{"$set":{'status':'arrived'}})
    await publish_driver_arrived({'driver_id':ride['driver_id'], 'ride_id':ride['id'], 'user_id':ride['user_id']})
    return {'message':'success'}


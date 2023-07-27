import uuid
from .database import driver_table

async def get_nearest_driver(location):
   pipeline= [
      {'$sample':{'size':1}}, 
      {'$match':{'status':'available'}}
      ]
   random_driver= driver_table.aggregate(pipeline)
   driver_id=None
   async for driver in random_driver:
      driver_id=driver['id']
   if not driver_id:
      return 'no drivers'
   return driver_id
import uuid
from .database import driver_table

async def get_closest_driver(location):
   pipeline= [{'$sample':{'size':1}}]
   random_driver= driver_table.aggregate(pipeline)
   driver_id=None
   async for driver in random_driver:
      driver_id=driver['id']
   if not driver_id:
      return 'no drivers'
   return driver_id
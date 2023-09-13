from motor import motor_asyncio
import os


MONGO_PASSWORD= os.getenv('MONGO_ROOT_PASSWORD')
MONGO_USER= os.getenv('MONGO_ROOT_USERNAME')
MONGO_HOST= os.getenv('MONGO_HOST')
MONGO_PORT= os.getenv('MONGO_PORT')
DATABASE_URL= f'mongodb://localhost/'
client=motor_asyncio.AsyncIOMotorClient(DATABASE_URL)
db=client['notification-service']
driver_collection=db['drivers']
ride_collection=db['rides']
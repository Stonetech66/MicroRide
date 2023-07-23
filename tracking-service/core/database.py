from motor import motor_asyncio
import os

MONGO_PASSWORD= os.getenv('MONGO_ROOT_PASSWORD')
MONGO_USER= os.getenv('MONGO_ROOT_USERNAME')
MONGO_HOST= os.getenv('MONGO_HOST')
MONGO_PORT= os.getenv('MONGO_PORT')
DATABASE_URL= f'mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/'
client=motor_asyncio.AsyncIOMotorClient(DATABASE_URL)
db=client['tracking-service']
ride_table=db['rides']
driver_table=db['drivers']
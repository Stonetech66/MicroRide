from motor import motor_asyncio
import os

# Define MongoDB connection details from environmental variables
MONGO_PASSWORD= os.getenv('MONGO_ROOT_PASSWORD')
MONGO_USER= os.getenv('MONGO_ROOT_USERNAME')
MONGO_HOST= os.getenv('MONGO_HOST')
MONGO_PORT= os.getenv('MONGO_PORT')

# Construct database URL
DATABASE_URL= f'mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}'


client=motor_asyncio.AsyncIOMotorClient(DATABASE_URL)

db=client['tracking-service'] 
ride_collection=db['rides'] 
driver_collection=db['drivers']
driver_tracking_collection=db['driver_tracking']

# Function to create database indexes
async def create_index():
    # Create 2dsphere index on location
    await driver_tracking_collection.create_index([('location', '2dsphere')])
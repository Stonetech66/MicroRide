from .database import driver_collection, driver_tracking_collection
from datetime import datetime, timedelta
import pytz
import os
from haversine import haversine

# Constants (configurable)
MAX_DRIVER_DISTANCE=os.getenv('MAX_DRIVER_DISTANCE',10000 ) # Maximum distance for driver search (in metres)

MAX_METRES_FOR_ARRIVAL=os.getenv('MAX_METRES_FOR_ARRIVAL',20) # Maximum distance to consider driver arrived (in metres)

DRIVER_LOCATION_UPDATE_INTERVAL=os.getenv('DRIVER_LOCATION_UPDATE_INTERVAL',30) # Interval for driver location updates (in seconds)


# Function to find nearest available driver
async def get_nearest_driver(location, driver_rejecting=None):
   # Define the query to find available drivers within the update interval 
   query={
      'status':'available',
      'timestamp':{
         '$gte':datetime.now(tz=pytz.timezone('UTC'))-timedelta(seconds=DRIVER_LOCATION_UPDATE_INTERVAL)
         }
      }
   
   # If a driver is rejecting a request, exclude them from consideration
   if driver_rejecting:
      query={
      'status':'available',
      'driver_id':{'$ne':driver_rejecting},
      'timestamp':{
         '$gte':datetime.now(tz=pytz.timezone('UTC'))-timedelta(seconds=DRIVER_LOCATION_UPDATE_INTERVAL)
         },
      }

   # MongoDB aggregation pipeline to find the nearest driver
   pipeline= [
      {'$geoNear':{
         'near':{
            'type':'Point', 'coordinates':location
            }, 
            'spherical':True,
            'distanceField':'distance',
            'maxDistance':MAX_DRIVER_DISTANCE,
            'query':query
         } 
      }, 
      {'$limit':1},
      {'$sort':{'timestamp':-1}},
      {'$project':{ '_id':0, 'timestamp':0,'distance':0}}
      ]
   
   # Execute the aggregation pipeline and return the nearest driver
   driver=await driver_tracking_collection.aggregate(pipeline).to_list(1)
   if driver:
      return driver[0]
   return None

# Function to calculate the estimated time of arrival (ETA) for a driver
async def get_driver_eta(driver_id, driver_current_coordinates=None, destination_coordinates=None, return_current_location=False):
   # Retrieves the driver`s rencent location data (3 most recent)
   driver_location=await driver_tracking_collection.find({'driver_id':driver_id}, projection={'_id':0, 'location':1, 'timestamp':1}).limit(3).sort('timestamp', -1).to_list(3)
   
   # Extract the coordinates for the three most recent locations
   loc1=driver_location[0]['location']['coordinates'] # location1
   loc2=driver_location[1]['location']['coordinates'] # location 2
   loc3=driver_location[2]['location']['coordinates'] # location 3
   
   # Extract the longititude and latitude for each location
   lon1, lat1=loc1[0], loc1[1] 
   lon2, lat2=loc2[0], loc2[1]
   lon3, lat3=loc3[0], loc3[1]
   
   # Calculate the timechange between the most recent locations
   timechange=driver_location[0]['timestamp']-driver_location[2]['timestamp']

   # Calculate the average distance between the three locations
   avgdistance=haversine((lat1, lon1), (lat2, lon2), unit='m')+haversine((lat2, lon2), (lat3, lon3), unit='m')/2

   # Calculate the average speed (distance / time) based on the recent locations
   avgspeed=avgdistance/timechange.total_seconds()

   # If the driver`s current coordinates are not provided, assume the last known location
   if not driver_current_coordinates:
      driver_current_coordinates=(lat1, lon1)
   
   # Calculate the driver distance to the destination
   driver_current_distance= haversine(driver_current_coordinates, destination_coordinates, unit='m')

   try:
      # Calculate the ETA based on the driver`s distance and average speed
      time= driver_current_distance/avgspeed
   except ZeroDivisionError:
      # Handle the case where the driver average speed is zero (driver not moving)
      if driver_current_distance <=  MAX_METRES_FOR_ARRIVAL:
         # If the driver is very close to the destination, ETA is set to 0
         time= 0
      else:
         # Otherwise, indicate a ride error (unable to calculate ETA)
         return  'ride error'
   
   if return_current_location: 
      # Returns the drivers current location and ETA in seconds
      return time, loc1
      
   # Returns the drivers ETA in seconds
   return time


   
   







 





 
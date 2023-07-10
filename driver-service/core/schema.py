from pydantic import BaseModel, Field
from typing import Union
from uuid import UUID
from datetime import datetime, date
from .models import Ride_Status




    
class RideDetails(BaseModel):
    id: UUID
    destination: str 
    pickup_location: str 
    driver_id: Union[str, None]
    status: Ride_Status
    fare: Union[float, None]
    paid: bool
    date: date

    class Config:
        orm_mode=True

class DriverCreate(BaseModel):
    country: str
    state: str
    birth_date:date
    bio: Union[str, None]

    
class DriverDetails(DriverCreate):
    id:str
    user_id:str



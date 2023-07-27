from pydantic import BaseModel
from typing import Union
from uuid import UUID
from datetime import date
from .models import Ride_Status, Driver_Status
from enum import Enum



    
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
    bio: Union[str, None]


    
class DriverDetails(DriverCreate):
    id:str
    user_id:str
    status: Driver_Status


class UpdateStatus(BaseModel):
   status:Driver_Status

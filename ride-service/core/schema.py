from pydantic import BaseModel
from typing import Union
from uuid import UUID
from datetime import datetime
from .models import Ride_Status


class RideBase(BaseModel):
    destination: str 
    pickup_location: str 

class BookRide(RideBase):
    destination: str 
    pickup_location: str 
    
class RideDetails(RideBase):
    id: UUID
    driver_id: Union[str, None]
    status: Ride_Status
    fare: Union[float, None]
    paid: bool
    date: datetime

    class Config:
        orm_mode=True
    

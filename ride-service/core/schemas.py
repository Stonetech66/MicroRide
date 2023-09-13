from pydantic import BaseModel, Field
from typing import Union
from uuid import UUID
from datetime import datetime
from .models import Ride_Status


class Location(BaseModel):
    lon: float = Field(le=180, ge=-180)
    lat: float=Field(le=90, ge=-90)

class RideBase(BaseModel):
    destination: list
    pickup_location: list

class BookRide(BaseModel):
    destination: Location
    pickup_location: Location

    
class RideDetails(RideBase):
    id: UUID
    driver_id: Union[str, None]
    status: Ride_Status
    fare: Union[float, None]
    paid: bool
    date: datetime

    class Config:
        orm_mode=True
    

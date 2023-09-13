from pydantic import BaseModel
from typing import Union
from uuid import UUID
from datetime import date, datetime
from .models import Ride_Status, Driver_Status
import enum 



class UpdateStatusEnum(str,enum.Enum):
    available= 'available'
    unavailable= 'unavailable'





class RideDetails(BaseModel):
    id: UUID
    destination: list
    pickup_location: list
    user_id: Union[str, None]
    status: Ride_Status
    fare: Union[float, None]
    paid: bool
    date: datetime

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


class RideSchema(BaseModel):
    ride_id:str
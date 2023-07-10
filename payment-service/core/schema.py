from pydantic import BaseModel

class PaymentSchema(BaseModel):
    ride_id: str 

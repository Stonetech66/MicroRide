from sqlalchemy import Column, String, Float, DateTime, Integer, Boolean, Table, MetaData, Enum, func, TIMESTAMP, ARRAY
import enum
metadata=MetaData()

class Ride_Status(enum.Enum):
    completed= 'completed'
    in_transit= 'in_transit'
    canceled= 'canceled'
    confirmed= 'confirmed'
    arrived= 'arrived'

Ride=Table(
    'rides',
    metadata,
    Column('id', String(36), primary_key=True),
    Column('user_id',String(36)),
    Column('driver_id', String(36),nullable=True ),
    Column('destination', ARRAY(Float), nullable=False),
    Column('pickup_location',ARRAY(Float), nullable=False),
    Column('fare',Float, nullable=True, server_default='0.0'),
    Column('status',Enum(Ride_Status), nullable=False),
    Column('paid',Boolean,server_default='false'),
    Column('date',TIMESTAMP(timezone=True), server_default=func.now()) 
    )



from sqlalchemy import Column, String, Float, Date, Integer, Boolean, Table, MetaData, Enum, func, TIMESTAMP, ForeignKey, ARRAY

import enum
metadata=MetaData()


class Driver_Status(str,enum.Enum):
    available= 'available'
    unavailable= 'unavailable'
    in_transit= 'in_transit'
    on_pickup='on_pickup'
    matched='matched'
    arrived= 'arrived'



Driver=Table(
    'drivers',
    metadata,
    Column('id', String(36), primary_key=True),
    Column('user_id',String(36), unique=True, nullable=False),
    Column('profile_pic',String(40), nullable=True),
    Column('bio',String(100), nullable=True),
    Column('country',String(100), nullable=True),
    Column('state',String(100), nullable=True),
    Column('status',Enum(Driver_Status), server_default='unavailable' ),
    Column('date',TIMESTAMP(timezone=True), server_default=func.now()) ,

)


class Ride_Status(str, enum.Enum):
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
    Column('driver_id', String(36),ForeignKey('drivers.id'), nullable=True ),
    Column('destination', ARRAY(Float), nullable=False),
    Column('pickup_location',ARRAY(Float), nullable=False),
    Column('fare',Float, nullable=True, server_default='0.0'),
    Column('status',Enum(Ride_Status), nullable=False),
    Column('paid',Boolean,server_default='false'),
    Column('date',TIMESTAMP(timezone=True), server_default=func.now()),
)


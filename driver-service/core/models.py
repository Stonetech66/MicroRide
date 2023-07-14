from sqlalchemy import Column, String, Float, Date, Integer, Boolean, Table, MetaData, Enum, func, TIMESTAMP, ForeignKey
from datetime import datetime
from sqlalchemy.sql import expression
import enum
metadata=MetaData()


Driver=Table(
    'drivers',
    metadata,
    Column('id', String(36), primary_key=True),
    Column('user_id',Integer, unique=True),
    Column('profile_pic',String(40), nullable=True),
    Column('bio',String(100), nullable=True),
    Column('country',String(100), nullable=True),
    Column('state',String(100), nullable=True),
    Column('birth_date',Date, nullable=True),
    Column('date',TIMESTAMP(timezone=True), server_default=func.now()) ,
)


class Ride_Status(enum.Enum):
    completed= 'completed'
    in_transit= 'in-transit'
    canceled= 'canceled'
    confirmed= 'confirmed'
    arrived= 'arrived'




Ride=Table(
    'rides',
    metadata,
    Column('id', String(36), primary_key=True),
    Column('user_id',String(36)),
    Column('driver_id', String(36),ForeignKey('drivers.id'), nullable=True ),
    Column('destination', String(200), nullable=False),
    Column('pickup_location',String(200), nullable=False),
    Column('fare',Float, nullable=True, server_default='0.0'),
    Column('status',Enum(Ride_Status), nullable=False),
    Column('paid',Boolean,server_default=expression.false()),
    Column('date',TIMESTAMP(timezone=True), server_default=func.now()),
)


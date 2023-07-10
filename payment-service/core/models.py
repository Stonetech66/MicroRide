from sqlalchemy import Column, String, Float, Date, Integer, Boolean, Table, MetaData, Enum, func, TIMESTAMP, ForeignKey
from datetime import datetime
from sqlalchemy.sql import expression
import enum

metadata=MetaData()

Payment= Table(
    'payments',
    metadata,
    Column('id', Integer, primary_key=True, index=True), 
    Column('user_id', String(36)),
    Column('amount', Float,), 
    Column('date',TIMESTAMP(timezone=True), server_default=func.now()) ,
    Column('ride_id', String(36),ForeignKey('rides.id'),unique=True),
    )

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
    Column('destination', String(200), nullable=False),
    Column('pickup_location',String(200), nullable=False),
    Column('fare',Float, nullable=True, server_default='0.0'),
    Column('status',Enum(Ride_Status), nullable=False),
    Column('paid',Boolean,server_default=expression.false()),
    Column('date',TIMESTAMP(timezone=True), server_default=func.now()),
)
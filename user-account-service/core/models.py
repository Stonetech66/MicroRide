from sqlalchemy import Column, String, Float, TIMESTAMP, Integer, Boolean, Table, MetaData, func
from datetime import datetime

metadata=MetaData()
User= Table(
    'users',
    metadata, 
    Column('id', String(36), primary_key=True),
    Column('email', String(100), nullable=False, unique=True),
    Column('password', String(100), nullable=False),
    Column('fullname',String(100), nullable=False),
    Column('date',TIMESTAMP(timezone=True), server_default=func.now()),
    )
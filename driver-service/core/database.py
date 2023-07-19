import databases
import sqlalchemy
import os 
POSTGRES_PASSWORD= os.getenv('POSTGRES_PASSWORD')
POSTGRES_USER= os.getenv('POSTGRES_USER')
POSTGRES_HOST= os.getenv('POSTGRES_HOST')
POSTGRES_DB= os.getenv('POSTGRES_DB')
POSTGRES_PORT= os.getenv('POSTGRES_PORT')
DATABASE_URL= f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'

database= databases.Database(DATABASE_URL) 

engine= sqlalchemy.create_engine(DATABASE_URL,)


import databases
import sqlalchemy
import os 
DATABASE_URL= os.getenv('DATABASE_URL')
database= databases.Database(DATABASE_URL) 

engine= sqlalchemy.create_engine(DATABASE_URL,)


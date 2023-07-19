from .models import User
from fastapi import HTTPException
from sqlalchemy import select
import uuid
from passlib.context import CryptContext

pwd_hash=CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash_password(password):
    return pwd_hash.hash(password)
def verify_password(plain_password, hashed_password):
    return pwd_hash.verify(plain_password, hashed_password)

class UserCrud:

    

    async def get_user_by_id(database, id):
        query= select(User).where(User.c.id==id)
        user= await database.fetch_one(query)
        return user

    async def create_user(database, schema):
        schema.password=hash_password(schema.password)
        query= User.insert().values(**schema.dict(), id=str(uuid.uuid4()))
        try:
            user= await database.execute(query)
            return user
        except:
            raise HTTPException(detail='user with this email already exists', status_code=400)

    
    async def get_user_by_email(database, email):
        query= select(User).where(User.c.email==email)
        user= await database.fetch_one(query)
        return user

    async def authenticate(database, email, password):
        query= select(User).where(User.c.email==email)
        user= await database.fetch_one(query)
        if user:
            if verify_password(password, user.password):
                return user
            raise HTTPException(detail="invalid email or password", status_code=401)
        raise HTTPException(detail="invalid email or password", status_code=401)

    

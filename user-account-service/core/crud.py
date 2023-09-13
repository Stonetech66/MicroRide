from .models import User
from fastapi import HTTPException
from sqlalchemy import select
import uuid
from .utils import password_manager
from asyncpg.exceptions import UniqueViolationError


class UserCrud:

    @staticmethod
    async def get_user_by_id(database, id):
        query= select(User).where(User.c.id==id)
        user= await database.fetch_one(query)
        return user

    @staticmethod
    async def create_user(database, schema):
        schema.password=password_manager.hash_password(schema.password)
        uid=str(uuid.uuid4())
        query= User.insert().values(**schema.dict(), id=uid)
        try:
            user= await database.execute(query)
            return uid
        except UniqueViolationError:
            raise HTTPException(detail='user with this email already exists', status_code=400)

    @staticmethod
    async def get_user_by_email(database, email):
        query= select(User).where(User.c.email==email)
        user= await database.fetch_one(query)
        return user

    @staticmethod
    async def authenticate(database, email, password):
        query= select(User).where(User.c.email==email)
        user= await database.fetch_one(query)
        if user:
            if password_manager.verify_password(password, user.password):
                return user
            raise HTTPException(detail="invalid email or password", status_code=401)
        raise HTTPException(detail="invalid email or password", status_code=401)

    

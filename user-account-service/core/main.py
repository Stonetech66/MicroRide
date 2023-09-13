from fastapi import FastAPI, HTTPException, Depends, Cookie, Header
from .dependencies import get_current_user
from . import schemas
from .database import database
from .crud import UserCrud
from fastapi_jwt_auth import AuthJWT
from fastapi.security import HTTPBearer

from fastapi.middleware.cors import CORSMiddleware
app=FastAPI(title='MicroRide user-acccount-service')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*']      
    )

@app.on_event('startup')
async def startup():
    await database.connect()

@app.on_event('shutdown')
async def shutdown():
    await database.disconnect()

@app.get('/')
async def app_probe():
    return {'message':'success'}

@app.get("/api/v1/user", response_model=schemas.UserDetails)
async def user_details(user:dict=Depends(get_current_user)):
    return user

@app.post('/api/v1/login', response_model=schemas.LoginDetails)
async def login(login:schemas.Login,Jwt:AuthJWT=Depends()):

    password, email=login.password, login.email
    user=await UserCrud.authenticate(database, password=password, email=email)
    access_token=Jwt.create_access_token(subject=user.id)
    refresh_token=Jwt.create_refresh_token(subject=user.id)
    return {'access_token':access_token, 'refresh_token':refresh_token, 'user':user}


@app.post('/api/v1/signup', summary='endpoint for users to signup', status_code=201)
async def signup(user:schemas.Signup, Jwt:AuthJWT=Depends()):

    if  await UserCrud.get_user_by_email(database, user.email):
        raise HTTPException(status_code=400, detail='user with this email already exists')
    user=await UserCrud.create_user(database, user)
    access_token=Jwt.create_access_token(subject=str(user))
    refresh_token=Jwt.create_refresh_token(subject=str(user))
    return {'access_token':access_token, 'refresh_token':refresh_token}




@app.post('/api/v1/refresh-token',)
def refresh_token(Jwt:AuthJWT=Depends(),  Authorization=Depends(HTTPBearer()),):
    exception=HTTPException(status_code=401, detail='invalid or expired refresh token')
    try:
        Jwt.jwt_refresh_token_required()
        current_user=Jwt.get_jwt_subject()
        access_token=Jwt.create_access_token(current_user)
        return {'access_token':access_token}
    except:
        raise exception
    
@app.post('/api/v1/logout')
def logout(Jwt:AuthJWT=Depends()):
    return {'message':'delete stored tokens from local storage'}

@app.post('/api/v1/verify-token')
def verify_token(Jwt:AuthJWT=Depends(), Authorization=Depends(HTTPBearer())):
    exception=HTTPException(status_code=401, detail='invalid or expired refresh token')
    try:
        current_user=Jwt.get_jwt_subject()
        exp=Jwt.get_raw_jwt()['exp']
        return {'user_id':current_user, 'exp':exp}
    except:
        raise exception
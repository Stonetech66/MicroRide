from fastapi import FastAPI, HTTPException, Depends, Cookie, Header
from .dependencies import get_current_user
from . import schema
from .database import database
from .crud import UserCrud
from fastapi_jwt_auth import AuthJWT

from fastapi.middleware.cors import CORSMiddleware
app=FastAPI(prefix='/v1', tags=["auth"])

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

@app.get("/user", response_model=schema.UserDetails)
async def user_details(user:dict=Depends(get_current_user)):
    return user

@app.post('/login', response_model=schema.LoginDetails)
async def login(login:schema.Login,Authorize:AuthJWT=Depends()):

    password, email=login.password, login.email
    user=await UserCrud.authenticate(database, password=password, email=email)
    access_token=Authorize.create_access_token(subject=user.id)
    refresh_token=Authorize.create_refresh_token(subject=user.id)
    return {'access_token':access_token, 'refresh_token':refresh_token, 'user':user}


@app.post('/signup', summary='endpoint for users to signup', status_code=201)
async def signup(user:schema.Signup, Authorize:AuthJWT=Depends()):

    if  await UserCrud.get_user_by_email(database, user.email):
        raise HTTPException(status_code=400, detail='user with this email already exists')
    user=await UserCrud.create_user(database, user)
    access_token=Authorize.create_access_token(subject=str(user))
    refresh_token=Authorize.create_refresh_token(subject=str(user))
    Authorize.set_access_cookies(access_token)
    Authorize.set_refresh_cookies(refresh_token)
    return {'access_token':access_token, 'refresh_token':refresh_token}




@app.post('/refresh-token')
def refresh_token(Authorization:AuthJWT=Depends(), refresh_token:str=Cookie(default=None), Bearer:str=Header(default=None)):
    exception=HTTPException(status_code=401, detail='invalid refresh token or token has expired')
    try:
        Authorization.jwt_refresh_token_required()
        current_user=Authorization.get_jwt_subject()
        access_token=Authorization.create_access_token(current_user)
        Authorization.set_access_cookies(access_token)

        return {'access_token':access_token}
    except:
        raise exception
    
@app.post('/logout')
def logout(Authorize:AuthJWT=Depends()):
    Authorize.unset_jwt_cookies()
    return {'message':'successfully logout'}

@app.post('/verify-token')
def verify_token(Authorization:AuthJWT=Depends()):
    exception=HTTPException(status_code=401, detail='invalid refresh token or token has expired')
    try:
        current_user=Authorization.get_jwt_subject()
        exp=Authorization.get_raw_jwt()['exp']
        return {'user_id':current_user, 'exp':exp}
    except:
        raise exception
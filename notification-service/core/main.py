from fastapi import FastAPI, Depends, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from .dependencies import get_current_websocket_user, get_current_websocket_driver


app= FastAPI()
from fastapi.middleware.cors import CORSMiddleware
app=FastAPI(prefix='/v1', tags=["auth"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*']      
    )

html2 = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>USER RIDE EVENTS</h1>
        <ul id='messages'>
        </ul>
        <script>
            const url= new URLSearchParams(window.location.search);
            const token= url.get('token')
            const host= window.location.host
            var ws = new WebSocket("ws://"+host+"/notification/api/v1/ws/ride/?token="+token);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                var data= JSON.stringify({"event_type":input.value})
                ws.send(data)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
    </html>"""

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
<h1>DRIVER RIDE EVENTS</h1>
        <ul id='messages'>
        </ul>
        <script>
            const url= new URLSearchParams(window.location.search);
            const token= url.get('token')
            const host= window.location.host
            var ws = new WebSocket("ws://"+host+"/notification/api/v1/ws/driver/?token="+token);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                var data= JSON.stringify({"event_type":input.value})
                ws.send(data)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
    </html>"""

@app.get('/')
async def app_probe():
    return {'message':'success'}

@app.get("/driver")
async def get():
    return HTMLResponse(html)

@app.get("/ride")
async def get():
    return HTMLResponse(html2)

@app.websocket('/api/v1/ws/ride/')
async def websocket_user_ride_notfication( websocket_auth=Depends(get_current_websocket_user)):
    websocket= websocket_auth
    try:
            while websocket:        
                await websocket.receive_text()
    except WebSocketDisconnect:
        pass



@app.websocket('/api/v1/ws/driver/')
async def websocket_driver_ride_notfication(websocket_auth=Depends(get_current_websocket_driver)):
    websocket= websocket_auth
    try:
        while websocket:        
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
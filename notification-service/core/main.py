from fastapi import FastAPI, Depends, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from .dependencies import get_current_websocket_user, get_current_websocket_driver


app= FastAPI()
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
            console.log(token)
            var ws = new WebSocket("ws://localhost:8003/ws/ride/?token="+token);
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
            console.log(token)
            var ws = new WebSocket("ws://localhost:8003/ws/driver/?token="+token);
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

@app.get("/driver")
async def get():
    return HTMLResponse(html)

@app.get("/ride")
async def get():
    return HTMLResponse(html2)

@app.websocket('/ws/ride/')
async def websocket_user_ride_notfication( websocket_auth=Depends(get_current_websocket_user)):
    websocket= websocket_auth
    try:
            while websocket:        
                await websocket.receive_text()
    except WebSocketDisconnect:
        pass



@app.websocket('/ws/driver/')
async def websocket_driver_ride_notfication(websocket_auth=Depends(get_current_websocket_driver)):
    websocket= websocket_auth
    try:
        while websocket:        
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
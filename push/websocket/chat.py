from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f0f2f5;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                margin: 0;
            }
            h1 {
                color: #333;
                margin-bottom: 10px;
            }
            h2 {
                color: #555;
                font-size: 1.2em;
                margin-bottom: 20px;
            }
            #ws-id {
                color: #007bff;
            }
            form {
                display: flex;
                margin-bottom: 20px;
                width: 100%;
                max-width: 500px;
            }
            #messageText {
                flex-grow: 1;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px 0 0 5px;
                font-size: 1em;
            }
            button {
                padding: 10px 15px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 0 5px 5px 0;
                cursor: pointer;
                font-size: 1em;
                transition: background-color 0.3s ease;
            }
            button:hover {
                background-color: #0056b3;
            }
            #messages {
                list-style-type: none;
                padding: 0;
                width: 100%;
                max-width: 500px;
                background-color: #fff;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                max-height: 400px;
                overflow-y: auto;
                margin-top: 0;
            }
            #messages li {
                padding: 10px 15px;
                border-bottom: 1px solid #eee;
                word-wrap: break-word;
            }
            #messages li:last-child {
                border-bottom: none;
            }
        </style>
    </head>
    <body>
        <h1>Integracion de Sistemas 1</h1>
        <h2>Web Socket Chat</h2>
        <h2>Cliente ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Enviar</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://10.10.1.196:8001/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
                // Desplazar hacia abajo para ver el mensaje más reciente
                messages.scrollTop = messages.scrollHeight;
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"Texto enviado: {data}", websocket)
            await manager.broadcast(f"Cliente #{client_id} dice: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Cliente #{client_id} abandonó el  chat")


if __name__ == "__main__":
    import uvicorn
    print("Iniciando chat sencillo -  IS2 - 2025 ...")
    print("Accede a: http://<TU-IP>:8001")
    print("WebSocket URL: ws://TU-IP:8000/ws/{client_id}")
    uvicorn.run("chat:app", host="0.0.0.0", port=8001, reload=True, log_level="info")
# websocket_demo.py - Ejemplo completo de WebSocket con FastAPI

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import json
import asyncio
import uuid
from datetime import datetime
from typing import List, Dict
import random
from pathlib import Path # Importa Path

app = FastAPI(title="Demo WebSocket - Sistema de Eventos en Tiempo Real")

# --- GESTOR DE CONEXIONES WEBSOCKET ---

class ConnectionManager:
    def __init__(self):
        # Diccionario para organizar conexiones por tipo
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.client_info: Dict[WebSocket, Dict] = {}
    
    async def connect(self, websocket: WebSocket, client_type: str = "general", client_id: str = None):
        """Conecta un nuevo cliente WebSocket"""
        await websocket.accept()
        
        # Inicializar lista si no existe
        if client_type not in self.active_connections:
            self.active_connections[client_type] = []
        
        # Agregar conexión
        self.active_connections[client_type].append(websocket)
        
        # Guardar información del cliente
        self.client_info[websocket] = {
            "type": client_type,
            "id": client_id or str(uuid.uuid4()),
            "connected_at": datetime.now().isoformat()
        }
        
        print(f"🔗 Cliente {client_type} conectado. Total: {len(self.active_connections[client_type])}")
        
        # Enviar mensaje de bienvenida
        await self.send_personal_message({
            "type": "connection_established",
            "message": f"Conectado como {client_type}",
            "client_id": self.client_info[websocket]["id"]
        }, websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Desconecta un cliente WebSocket"""
        if websocket in self.client_info:
            client_type = self.client_info[websocket]["type"]
            
            # Remover de la lista de conexiones activas
            if client_type in self.active_connections:
                self.active_connections[client_type].remove(websocket)
            
            # Remover información del cliente
            del self.client_info[websocket]
            
            print(f"❌ Cliente {client_type} desconectado. Restantes: {len(self.active_connections.get(client_type, []))}")
    
    async def send_personal_message(self, message: Dict, websocket: WebSocket):
        """Envía un mensaje a un cliente específico"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"❌ Error enviando mensaje personal: {e}")
    
    async def broadcast_to_type(self, message: Dict, client_type: str):
        """Envía un mensaje a todos los clientes de un tipo específico"""
        if client_type not in self.active_connections:
            return
        
        disconnected = []
        for connection in self.active_connections[client_type]:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"❌ Error en broadcast: {e}")
                disconnected.append(connection)
        
        # Limpiar conexiones desconectadas
        for conn in disconnected:
            self.disconnect(conn)
    
    async def broadcast_to_all(self, message: Dict):
        """Envía un mensaje a todos los clientes conectados"""
        for client_type in self.active_connections:
            await self.broadcast_to_type(message, client_type)
    
    def get_stats(self):
        """Obtiene estadísticas de conexiones"""
        stats = {}
        total = 0
        for client_type, connections in self.active_connections.items():
            count = len(connections)
            stats[client_type] = count
            total += count
        
        return {"total": total, "by_type": stats}

# Instancia global del gestor de conexiones
manager = ConnectionManager()

# --- SIMULADOR DE EVENTOS ---

class EventSimulator:
    def __init__(self, connection_manager: ConnectionManager):
        self.manager = connection_manager
        self.is_running = False
        self.sensors = ["TEMP_01", "HUMID_01", "PRESS_01", "LIGHT_01"]
    
    async def start_simulation(self):
        """Inicia la simulación de eventos"""
        self.is_running = True
        print("🚀 Iniciando simulación de eventos...")
        
        while self.is_running:
            # Generar evento aleatorio
            event_type = random.choice(["sensor_data", "alert", "system_status"])
            
            if event_type == "sensor_data":
                event = self.generate_sensor_data()
            elif event_type == "alert":
                event = self.generate_alert()
            else:
                event = self.generate_system_status()
            
            # Enviar a clientes apropiados
            if event_type == "sensor_data":
                await self.manager.broadcast_to_type(event, "dashboard")
                await self.manager.broadcast_to_type(event, "monitor")
            elif event_type == "alert":
                await self.manager.broadcast_to_all(event)
            else:
                await self.manager.broadcast_to_type(event, "admin")
            
            # Esperar antes del siguiente evento
            await asyncio.sleep(random.uniform(2, 5))
    
    def generate_sensor_data(self):
        """Genera datos simulados de sensores"""
        sensor = random.choice(self.sensors)
        
        # Valores simulados según el tipo de sensor
        if "TEMP" in sensor:
            value = round(random.uniform(18.0, 35.0), 1)
            unit = "°C"
        elif "HUMID" in sensor:
            value = round(random.uniform(30.0, 80.0), 1)
            unit = "%"
        elif "PRESS" in sensor:
            value = round(random.uniform(1010.0, 1030.0), 1)
            unit = "hPa"
        else:  # LIGHT
            value = round(random.uniform(100, 1000), 0)
            unit = "lux"
        
        return {
            "type": "sensor_data",
            "sensor_id": sensor,
            "value": value,
            "unit": unit,
            "timestamp": datetime.now().isoformat(),
            "location": f"Sala {random.randint(1, 5)}"
        }
    
    def generate_alert(self):
        """Genera alertas simuladas"""
        alert_types = ["high_temperature", "low_humidity", "sensor_offline", "battery_low"]
        alert_type = random.choice(alert_types)
        
        return {
            "type": "alert",
            "alert_type": alert_type,
            "message": f"Alerta: {alert_type.replace('_', ' ').title()}",
            "severity": random.choice(["low", "medium", "high"]),
            "sensor_id": random.choice(self.sensors),
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_system_status(self):
        """Genera estados del sistema"""
        return {
            "type": "system_status",
            "cpu_usage": round(random.uniform(10, 90), 1),
            "memory_usage": round(random.uniform(20, 80), 1),
            "active_connections": manager.get_stats()["total"],
            "uptime": "5h 23m",
            "timestamp": datetime.now().isoformat()
        }
    
    def stop_simulation(self):
        """Detiene la simulación"""
        self.is_running = False
        print("⏹️ Simulación detenida")

# Instancia del simulador
simulator = EventSimulator(manager)

# --- ENDPOINTS WEBSOCKET ---

@app.websocket("/ws/{client_type}")
async def websocket_endpoint(websocket: WebSocket, client_type: str, client_id: str = None):
    """Endpoint principal de WebSocket con tipos de cliente"""
    await manager.connect(websocket, client_type, client_id)
    
    try:
        while True:
            # Recibir mensajes del cliente
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Procesar diferentes tipos de mensajes
            if message.get("action") == "ping":
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }, websocket)
            
            elif message.get("action") == "broadcast":
                # Reenviar mensaje a otros clientes del mismo tipo
                broadcast_msg = {
                    "type": "user_message",
                    "from": manager.client_info[websocket]["id"],
                    "message": message.get("message", ""),
                    "timestamp": datetime.now().isoformat()
                }
                await manager.broadcast_to_type(broadcast_msg, client_type)
            
            elif message.get("action") == "get_stats":
                stats = manager.get_stats()
                await manager.send_personal_message({
                    "type": "stats",
                    "data": stats
                }, websocket)
            
            else:
                # Eco del mensaje
                await manager.send_personal_message({
                    "type": "echo",
                    "original": message,
                    "timestamp": datetime.now().isoformat()
                }, websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# --- ENDPOINTS HTTP ---
BASE_DIR = Path(__file__).resolve().parent
HTML_FILE_PATH = BASE_DIR / "server_simulator.html"

@app.get("/")
async def get_home():
    """
    Sirve el contenido del archivo server_simulator.html
    cuando se accede a la raíz de la aplicación.
    """
    try:
        with open(HTML_FILE_PATH, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Error: server_simulator.html no encontrado</h1>", status_code=404)
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error interno del servidor: {e}</h1>", status_code=500)

@app.get("/stats")
async def get_connection_stats():
    """Obtiene estadísticas de conexiones"""
    return manager.get_stats()

@app.post("/start-simulation")
async def start_event_simulation():
    """Inicia la simulación de eventos"""
    if not simulator.is_running:
        asyncio.create_task(simulator.start_simulation())
        return {"status": "started", "message": "Simulación iniciada"}
    return {"status": "already_running", "message": "La simulación ya está ejecutándose"}

@app.post("/stop-simulation")
async def stop_event_simulation():
    """Detiene la simulación de eventos"""
    simulator.stop_simulation()
    return {"status": "stopped", "message": "Simulación detenida"}

@app.post("/broadcast")
async def broadcast_message(message: Dict):
    """Envía un mensaje a todos los clientes conectados"""
    broadcast_data = {
        "type": "admin_broadcast",
        "message": message.get("message", ""),
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast_to_all(broadcast_data)
    return {"status": "sent", "message": "Mensaje enviado a todos los clientes"}


if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando servidor WebSocket IS2 - 2025 ...")
    print("📱 Accede a: http://localhost:8000")
    print("🔌 WebSocket URL: ws://localhost:8000/ws/{client_type}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
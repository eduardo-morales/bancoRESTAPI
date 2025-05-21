# webhook_server_fastapi.py - Implementación de un servidor webhooks con FastAPI

import time
import hmac
import json
import hashlib
import logging
from typing import List, Dict, Optional, Any
import asyncio
import httpx
from pydantic import BaseModel, HttpUrl
from fastapi import FastAPI, HTTPException, Header, BackgroundTasks, Request, Depends, status
from fastapi.responses import JSONResponse

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Inicialización de FastAPI
app = FastAPI(title="Webhook Server API", description="Servidor de webhooks implementado con FastAPI")

# Clave secreta para firmar webhooks
SECRET_KEY = "webhook_secret_key_12345"

# Base de datos en memoria para suscriptores
webhook_subscribers: Dict[str, Dict] = {}

# Modelos Pydantic para validación de datos
class WebhookSubscription(BaseModel):
    url: HttpUrl
    events: List[str]

class EventTrigger(BaseModel):
    event: str
    data: Optional[Dict[str, Any]] = {}

class WebhookResponse(BaseModel):
    id: str
    status: str

class EventResponse(BaseModel):
    status: str
    event: str

# Funciones auxiliares
def generate_signature(payload: Dict) -> str:
    """Genera una firma HMAC-SHA256 para el payload del webhook"""
    payload_str = json.dumps(payload, sort_keys=True).encode('utf-8')
    signature = hmac.new(
        SECRET_KEY.encode('utf-8'), 
        payload_str, 
        hashlib.sha256
    ).hexdigest()
    return signature

async def send_webhook(url: str, event: str, data: Dict) -> Optional[int]:
    """Envía una notificación webhook a un suscriptor de forma asíncrona"""
    payload = {
        "event": event,
        "timestamp": time.time(),
        "data": data
    }
    
    signature = generate_signature(payload)
    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Signature": signature
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                str(url), 
                json=payload, 
                headers=headers, 
                timeout=5.0
            )
            logger.info(f"Webhook enviado a {url}, respuesta: {response.status_code}")
            return response.status_code
        except httpx.RequestError as e:
            logger.error(f"Error al enviar webhook a {url}: {str(e)}")
            return None

async def notify_subscribers(event: str, data: Dict) -> None:
    """Notifica a todos los suscriptores interesados en un evento específico"""
    for subscriber_id, subscriber in webhook_subscribers.items():
        if event in subscriber['events']:
            url = subscriber['url']
            logger.info(f"Notificando a {subscriber_id} sobre evento {event}")
            status_code = await send_webhook(url, event, data)
            
            # Implementar reintentos en caso de fallo
            retries = 3
            while status_code not in [200, 201, 202] and retries > 0:
                logger.warning(f"Reintentando webhook para {subscriber_id}, intentos restantes: {retries}")
                await asyncio.sleep(2)  # Esperar antes de reintentar
                status_code = await send_webhook(url, event, data)
                retries -= 1

# Endpoints de la API
@app.post("/api/subscribe", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
async def subscribe_webhook(subscription: WebhookSubscription):
    """Endpoint para que los clientes se suscriban a webhooks"""
    subscriber_id = str(int(time.time() * 1000))  # ID único basado en timestamp
    
    webhook_subscribers[subscriber_id] = {
        "url": str(subscription.url),
        "events": subscription.events,
        "created_at": time.time()
    }
    
    logger.info(f"Nuevo suscriptor registrado: {subscriber_id}")
    return {"id": subscriber_id, "status": "subscribed"}

@app.delete("/api/unsubscribe/{subscriber_id}", response_model=WebhookResponse)
async def unsubscribe_webhook(subscriber_id: str):
    """Endpoint para cancelar suscripción a webhooks"""
    if subscriber_id in webhook_subscribers:
        del webhook_subscribers[subscriber_id]
        logger.info(f"Suscriptor eliminado: {subscriber_id}")
        return {"id": subscriber_id, "status": "unsubscribed"}
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail=f"Suscriptor {subscriber_id} no encontrado"
    )

@app.post("/api/trigger-event", response_model=EventResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_event(event_data: EventTrigger, background_tasks: BackgroundTasks):
    """Endpoint para desencadenar un evento y enviar webhooks"""
    event = event_data.event
    data = event_data.data or {}
    
    # Añadir tarea en segundo plano para enviar notificaciones
    background_tasks.add_task(notify_subscribers, event, data)
    
    logger.info(f"Evento {event} programado para notificación")
    return {"status": "processing", "event": event}


@app.get("/api/subscribers")
async def list_subscribers():
    """Endpoint para listar todos los suscriptores (solo para propósitos de demostración )"""
    return webhook_subscribers

# Middleware para logging y manejo de errores
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para registrar todas las solicitudes y manejar errores"""
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"{request.method} {request.url.path} completado en {process_time:.4f}s")
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"{request.method} {request.url.path} falló después de {process_time:.4f}s: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Error interno del servidor"}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fastapi-webhook-server:app", host="0.0.0.0", port=8000, reload=True)

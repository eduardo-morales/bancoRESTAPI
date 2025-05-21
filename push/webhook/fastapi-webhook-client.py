# webhook_client_fastapi.py - Implementación de un cliente para recibir webhooks con FastAPI

import hmac
import json
import hashlib
import logging
from typing import Dict, Any, Optional
import httpx
from pydantic import BaseModel
from fastapi import FastAPI, Request, Header, HTTPException, Depends, status
from fastapi.responses import JSONResponse

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Inicialización de FastAPI
app = FastAPI(title="Webhook Client API", description="Cliente para recibir webhooks implementado con FastAPI")

# Debería coincidir con la clave del servidor
SECRET_KEY = "webhook_secret_key_12345"

# URL del servidor webhook
WEBHOOK_SERVER_URL = "http://localhost:8000"

# Modelos Pydantic
class WebhookEvent(BaseModel):
    event: str
    timestamp: float
    data: Dict[str, Any]

class WebhookResponse(BaseModel):
    status: str

class SubscriptionRequest(BaseModel):
    events: list[str]
    callback_url: str

# Registro de eventos recibidos (simulación de base de datos)
received_events = []

# Funciones auxiliares
def generate_signature(payload: Dict) -> str:
    """Genera una firma HMAC-SHA256 para verificar la autenticidad del webhook"""
    payload_str = json.dumps(payload, sort_keys=True).encode('utf-8')
    signature = hmac.new(
        SECRET_KEY.encode('utf-8'), 
        payload_str, 
        hashlib.sha256
    ).hexdigest()
    return signature

def verify_signature(signature: str, payload: Dict) -> bool:
    """Verifica la firma del webhook contra el payload recibido"""
    expected_signature = generate_signature(payload)
    return hmac.compare_digest(signature, expected_signature)

async def process_event(event: str, data: Dict[str, Any]) -> None:
    """Procesa un evento recibido vía webhook"""
    if event == "user.created":
        logger.info(f"Procesando creación de usuario: {data.get('username')}")
        # Implementar lógica de negocio para usuario creado
    elif event == "order.completed":
        logger.info(f"Procesando orden completada: {data.get('order_id')}")
        # Implementar lógica de negocio para orden completada
    elif event == "payment.received":
        logger.info(f"Procesando pago recibido: {data.get('amount')} {data.get('currency')}")
        # Implementar lógica de negocio para pago recibido
    else:
        logger.info(f"Recibido evento genérico: {event}")
        # Implementar lógica para otros eventos

async def register_with_server(events: list[str], callback_url: str) -> Dict:
    """Registra este cliente con el servidor de webhooks"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{WEBHOOK_SERVER_URL}/api/subscribe", 
                json={"url": callback_url, "events": events}
            )
            if response.status_code == 201:
                return response.json()
            else:
                logger.error(f"Error al registrar con el servidor: {response.status_code} {response.text}")
                return {"error": "No se pudo registrar con el servidor"}
        except httpx.RequestError as e:
            logger.error(f"Error de conexión: {str(e)}")
            return {"error": str(e)}

# Endpoints
@app.post("/webhook", response_model=WebhookResponse)
async def receive_webhook(
    webhook_data: WebhookEvent,
    x_webhook_signature: Optional[str] = Header(None)
):
    """Endpoint que recibe notificaciones webhook"""
    # Verificar la firma del webhook
    if not x_webhook_signature:
        logger.warning("Solicitud webhook sin firma recibida")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firma no proporcionada"
        )
    
    if not verify_signature(x_webhook_signature, webhook_data.dict()):
        logger.warning("Solicitud webhook con firma inválida rechazada")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firma inválida"
        )
    
    # Guardar el evento recibido (simulación)
    received_events.append({
        "event": webhook_data.event,
        "timestamp": webhook_data.timestamp,
        "data": webhook_data.data
    })
    
    # Procesar el webhook de forma asíncrona
    logger.info(f"Webhook recibido: {webhook_data.event} a las {webhook_data.timestamp}")
    logger.info(f"Datos: {json.dumps(webhook_data.data)}")
    
    # Procesamiento asíncrono del evento
    await process_event(webhook_data.event, webhook_data.data)
    
    return {"status": "success"}

@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register_subscription(subscription: SubscriptionRequest):
    """Registra este cliente con el servidor de webhooks"""
    result = await register_with_server(subscription.events, subscription.callback_url)
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=result["error"]
        )
    
    return result

@app.get("/events")
async def list_events():
    """Lista todos los eventos recibidos (solo para demostración)"""
    return received_events

# Ejemplo de cómo desencadenar un evento en el servidor desde el cliente
@app.post("/trigger-test-event")
async def trigger_test_event(event_name: str = "test.event"):
    """
    Envía una solicitud al servidor para desencadenar un evento de prueba
    Este endpoint sirve como demostración de cómo un cliente puede iniciar un evento
    """
    test_data = {
        "event": event_name,
        "data": {
            "test_id": "123456",
            "message": "Este es un evento de prueba",
            "timestamp": "2023-05-21T10:30:00Z"
        }
    }
    logger.info(f"Desencadenando evento de prueba: {event_name}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{WEBHOOK_SERVER_URL}/api/trigger-event", 
                json=test_data
            )
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"Error al enviar evento de prueba: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Error al comunicarse con el servidor: {str(e)}"
            )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fastapi-webhook-client:app", host="0.0.0.0", port=8001, reload=True)

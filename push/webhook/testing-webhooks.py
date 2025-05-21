# test_webhooks.py - Script para probar los webhooks

import asyncio
import httpx
import json
import logging
from datetime import datetime

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuración de URLs
SERVER_URL = "http://localhost:8000"
CLIENT_URL = "http://localhost:8001"

async def test_webhook_integration():
    """Prueba completa del flujo de webhooks"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Paso 1: Registrar el cliente con el servidor
        logger.info("Paso 1: Registrando cliente con el servidor...")
        callback_url = f"{CLIENT_URL}/webhook"
        
        subscription_data = {
            "url": callback_url,
            "events": ["user.created", "order.completed", "payment.received"]
        }
        
        try:
            response = await client.post(f"{SERVER_URL}/api/subscribe", json=subscription_data)
            response.raise_for_status()
            subscriber_data = response.json()
            subscriber_id = subscriber_data["id"]
            logger.info(f"Cliente registrado exitosamente con ID: {subscriber_id}")
            
            # Paso 2: Desencadenar un evento en el servidor
            logger.info("Paso 2: Desencadenando evento 'user.created'...")
            event_data = {
                "event": "user.created",
                "data": {
                    "user_id": "usr_123456",
                    "username": "nuevo_usuario",
                    "email": "usuario@ejemplo.com",
                    "created_at": datetime.now().isoformat()
                }
            }
            
            response = await client.post(f"{SERVER_URL}/api/trigger-event", json=event_data)
            response.raise_for_status()
            logger.info(f"Evento desencadenado: {response.json()}")
            
            # Esperar a que el webhook sea procesado
            logger.info("Esperando a que el webhook sea procesado...")
            await asyncio.sleep(2)
            
            # Paso 3: Verificar que el cliente recibió el evento
            logger.info("Paso 3: Verificando eventos recibidos por el cliente...")
            response = await client.get(f"{CLIENT_URL}/events")
            response.raise_for_status()
            received_events = response.json()
            
            if received_events:
                logger.info(f"Cliente ha recibido {len(received_events)} eventos:")
                for idx, event in enumerate(received_events, 1):
                    logger.info(f"  Evento {idx}: {event['event']} a las {event['timestamp']}")
            else:
                logger.warning("El cliente no ha recibido ningún evento.")
            
            # Paso 4: Desencadenar otro evento
            logger.info("Paso 4: Desencadenando evento 'order.completed'...")
            event_data = {
                "event": "order.completed",
                "data": {
                    "order_id": "ord_789012",
                    "customer_id": "usr_123456",
                    "total": 129.99,
                    "items": 3,
                    "completed_at": datetime.now().isoformat()
                }
            }
            
            response = await client.post(f"{SERVER_URL}/api/trigger-event", json=event_data)
            response.raise_for_status()
            logger.info(f"Evento desencadenado: {response.json()}")
            
            # Esperar a que el webhook sea procesado
            await asyncio.sleep(2)
            
            # Paso 5: Cancelar la suscripción
            logger.info(f"Paso 5: Cancelando suscripción para ID: {subscriber_id}...")
            response = await client.delete(f"{SERVER_URL}/api/unsubscribe/{subscriber_id}")
            response.raise_for_status()
            logger.info(f"Suscripción cancelada: {response.json()}")
            
            # Paso 6: Verificar que no se reciben más eventos después de cancelar
            logger.info("Paso 6: Desencadenando evento después de cancelar suscripción...")
            event_data = {
                "event": "payment.received",
                "data": {
                    "payment_id": "pay_345678",
                    "order_id": "ord_789012",
                    "amount": 129.99,
                    "currency": "USD",
                    "received_at": datetime.now().isoformat()
                }
            }
            
            response = await client.post(f"{SERVER_URL}/api/trigger-event", json=event_data)
            response.raise_for_status()
            logger.info(f"Evento desencadenado después de cancelar suscripción: {response.json()}")
            
            # Esperar a que el webhook sea procesado (si lo fuera)
            await asyncio.sleep(2)
            
            # Verificar que no llegaron nuevos eventos
            response = await client.get(f"{CLIENT_URL}/events")
            response.raise_for_status()
            new_events = response.json()
            
            if len(new_events) > len(received_events):
                logger.warning(
                    f"¡El cliente recibió {len(new_events) - len(received_events)} eventos nuevos " 
                    "después de cancelar la suscripción!"
                )
            else:
                logger.info("Confirmado: No se recibieron más eventos después de cancelar la suscripción.")
            
         
            
            logger.info("Prueba de integración de webhooks completada.")
            
        except httpx.RequestError as e:
            logger.error(f"Error de conexión durante la prueba: {e}")
        except Exception as e:
            logger.error(f"Error inesperado durante la prueba: {e}")


async def main():
    """Función principal para ejecutar las pruebas"""
    logger.info("Iniciando pruebas de webhooks...")
    await test_webhook_integration()
    logger.info("Pruebas de webhooks completadas.")


if __name__ == "__main__":
    asyncio.run(main())
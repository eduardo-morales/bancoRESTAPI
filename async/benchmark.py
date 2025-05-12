import asyncio
import time
import httpx

### Este script mide el rendimiento de las APIs síncronas y asíncronas
# pip install fastapi uvicorn httpx

#Ejecuta las APIs: Abre dos terminales separadas y ejecuta cada API:
# python app_async.py
# python app_sync.py

# Ejecuta el script de benchmarking: Abre una tercera terminal y ejecuta el script de
#python benchmark.py

async def medir_rendimiento(url: str, num_requests: int):
    """Mide el tiempo total para realizar múltiples solicitudes a una URL."""
    start_time = time.time()
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for _ in range(num_requests)]
        await asyncio.gather(*tasks)
    end_time = time.time()
    duration = end_time - start_time
    print(f"Realizadas {num_requests} solicitudes a {url} en {duration:.2f} segundos.")
    return duration

async def main():
    num_requests = 5  # Puedes ajustar el número de solicitudes
    delay = 2         # Puedes ajustar el tiempo de espera de las tareas

    print("\n--- Rendimiento de la API Síncrona (una solicitud) ---")
    await medir_rendimiento(f"http://localhost:8001/sync/{delay}", 1)

    print("\n--- Rendimiento de la API Asíncrona (una solicitud) ---")
    await medir_rendimiento(f"http://localhost:8000/async/{delay}", 1)

    print("\n--- Rendimiento de la API Síncrona (múltiples solicitudes secuenciales) ---")
    await medir_rendimiento(f"http://localhost:8001/sync/secuencial/{num_requests}/{delay}", 1)

    print("\n--- Rendimiento de la API Asíncrona (múltiples solicitudes concurrentes) ---")
    await medir_rendimiento(f"http://localhost:8000/async/concurrente/{num_requests}/{delay}", 1)

if __name__ == "__main__":
    asyncio.run(main())
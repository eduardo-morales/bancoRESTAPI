from fastapi import FastAPI
import asyncio
import time

app = FastAPI()

## ENDPOINTS ASÍNCRONOS

async def tarea_asincrona(n: int) -> int:
    """Simula una tarea asíncrona que tarda un tiempo."""
    await asyncio.sleep(n)
    return n * 2

@app.get("/async/{delay}")
async def endpoint_asincrono(delay: int):
    """Endpoint asíncrono que ejecuta una tarea simulada."""
    start_time = time.time()
    resultado = await tarea_asincrona(delay)
    end_time = time.time()
    return {
        "mensaje": f"Tarea asíncrona completada después de {delay} segundos.",
        "resultado": resultado,
        "tiempo_ejecucion": end_time - start_time,
    }

@app.get("/async/concurrente/{num_tareas}/{delay}")
async def endpoint_asincrono_concurrente(num_tareas: int, delay: int):
    """Endpoint asíncrono que ejecuta múltiples tareas concurrentemente."""
    start_time = time.time()
    tareas = [tarea_asincrona(delay) for _ in range(num_tareas)]
    resultados = await asyncio.gather(*tareas)
    end_time = time.time()
    return {
        "mensaje": f"Ejecutadas {num_tareas} tareas asíncronas concurrentemente de {delay} segundos.",
        "resultados": resultados,
        "tiempo_ejecucion": end_time - start_time,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
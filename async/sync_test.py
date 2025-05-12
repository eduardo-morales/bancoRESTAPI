from fastapi import FastAPI
import time

app = FastAPI()

def tarea_sincrona(n: int) -> int:
    """Simula una tarea síncrona que bloquea la ejecución."""
    time.sleep(n)
    return n * 2

@app.get("/sync/{delay}")
def endpoint_sincrono(delay: int):
    """Endpoint síncrono que ejecuta una tarea simulada."""
    start_time = time.time()
    resultado = tarea_sincrona(delay)
    end_time = time.time()
    return {
        "mensaje": f"Tarea síncrona completada después de {delay} segundos.",
        "resultado": resultado,
        "tiempo_ejecucion": end_time - start_time,
    }

@app.get("/sync/secuencial/{num_tareas}/{delay}")
def endpoint_sincrono_secuencial(num_tareas: int, delay: int):
    """Endpoint síncrono que ejecuta múltiples tareas secuencialmente."""
    start_time = time.time()
    resultados = [tarea_sincrona(delay) for _ in range(num_tareas)]
    end_time = time.time()
    return {
        "mensaje": f"Ejecutadas {num_tareas} tareas síncronas secuencialmente de {delay} segundos.",
        "resultados": resultados,
        "tiempo_ejecucion": end_time - start_time,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) # Ejecutar en un puerto diferente
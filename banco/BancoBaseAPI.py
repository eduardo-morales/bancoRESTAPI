from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Union
from models.modelsBase import Cliente, init_db
import sqlite3
import requests
from fastapi.responses import JSONResponse


app = FastAPI()

# Conexión y configuración de la base de datos
DATABASE = "bancobase.db"
init_db(DATABASE)


#TODO Recursos a implementar
# 1 - Cliente
# Registrar - POST /clientes
# listar - GET /clientes
# consultar- GET /clientes/{CI} 
# actualizar- PUT /clientes/{CI}
# eliminar - DELETE /clientes/{CI}

# 2 - Deuda 
# - POST /deuda
# - GET /deuda
# - GET /deuda/{CI} 
# - PUT /deuda/{CI}
# - DELETE /deuda/{CI}

# 3 - Pago  
# - POST /pagos
# - GET /pagos
# - GET /pagos/{pk} 
# - PUT /pagos/{pk}
# - DELETE /pagos/{pk}

# 3 - Banco 
# - POST /pagos
# - GET /pagos
# - GET /pagos/{pk} 
# - PUT /pagos/{pk}
# - DELETE /pagos/{pk}

URL_TELCO = "http://localhost:8000/telco/"

@app.get("/deuda/{cedula}")
def consulta_deuda(cedula: int):
    response = requests.get(URL_TELCO+"deuda/"+str(cedula)).text
    try:
        deudas = response.json()
        print(deudas)
    except:
        raise HTTPException(status_code=404, detail="Deuda not found")
    
    return JSONResponse(content=deudas)
    


@app.post("/clientes/", response_model=Cliente)
def create_cliente(cliente: Cliente):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO clientes (cedula, nombre, apellido)
            VALUES (?, ?, ?)
        ''', (cliente.cedula, cliente.nombre, cliente.apellido))
        conn.commit()
        cliente.id = cursor.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Cliente con esta cedula ya existe")
    conn.close()
    return cliente

@app.get("/clientes/", response_model=List[Cliente])
def read_clientes(skip: int = 0, limit: int = 10):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, cedula, nombre, apellido
        FROM clientes
        LIMIT ? OFFSET ?
    ''', (limit, skip))
    rows = cursor.fetchall()
    conn.close()
    return [Cliente(id=row[0], cedula=row[1], nombre=row[2], apellido=row[3]) for row in rows]

@app.get("/clientes/{cliente_id}", response_model=Cliente)
def read_cliente(cliente_id: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, cedula, nombre, apellido
        FROM clientes
        WHERE id = ?
    ''', (cliente_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Cliente not found")
    return Cliente(id=row[0], cedula=row[1], nombre=row[2], apellido=row[3])

@app.put("/clientes/{cliente_id}", response_model=Cliente)
def update_cliente(cliente_id: int, cliente: Cliente):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE clientes
        SET cedula = ?, nombre = ?, apellido = ?
        WHERE id = ?
    ''', (cliente.cedula, cliente.nombre, cliente.apellido, cliente_id))
    conn.commit()
    conn.close()
    cliente.id = cliente_id
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Cliente not found")
    return cliente

@app.delete("/clientes/{cliente_id}")
def delete_cliente(cliente_id: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM clientes
        WHERE id = ?
    ''', (cliente_id,))
    conn.commit()
    conn.close()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Cliente not found")
    return {"message": "Cliente deleted"}

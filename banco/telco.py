from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Union
from models.modelsBase import Cliente, init_db
import requests

deuda_dummy = {
    "cliente_id": 1,
    "nro_factura": "123",
    "saldo_pendiente": 100000,
    "moneda": "GS",
}
app = FastAPI()

@app.get("/deuda/{cedula}",)
def consulta_deuda(cedula: int):
    print("Consulta deuda de telco con el parametro cedula: ", cedula)
    return deuda_dummy
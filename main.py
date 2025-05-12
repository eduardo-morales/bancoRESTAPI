from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    nombre: str
    precio: float
    is_offer: Union[bool, None] = None

repositorio = [
    {"id": 1, "nombre": "item1", "precio": 10.0, "is_offer": False},
    {"id": 2, "nombre": "item2", "precio": 20.0, "is_offer": True},
]

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/items/")
def create_item(item: Item):
    #logica de negocio y valiciio
    repositorio.append(item)
    #return item
    return {"nombre_item": item.nombre, "precio": item.precio, "en_oferta":item.is_offer}

#http://localhost:8000/items/1?nombre=eduardo""
@app.get("/items/{item_id}")
def read_item(item_id: int, tipo: Union[str, None] = None):
    #logica de negocio y valiciio
    return repositorio[item_id]#{"item_id": item_id, "q": tipo}

#htttp://localhost:8000/items?tipo="comestible"
@app.get("/items/")
def listar():
    #return {"item_id": item_id, "q": q}
    return repositorio

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):

    sql = "update items set nombre= "+item.nombre+", precio="+str(item.precio)+" where id ="+str(item_id) 
    print(sql)
    
    return {"nombre_item": item.nombre, "item_id": item_id,"en_oferta":item.is_offer}


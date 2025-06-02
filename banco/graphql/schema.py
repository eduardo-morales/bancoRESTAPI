import strawberry
import typing
from typing import List, Optional, Union
from strawberry.types import Info
from models import Cliente as ClienteModel, Cuenta as CuentaModel, Pagos as PagosModel, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload


@strawberry.type
class Cuenta:
    id: int
    cliente_id: int
    cuenta: int
    pagos: List["Pago"]

@strawberry.type
class Pago:
    id: int
    cuenta_id: int
    monto: int
    moneda: str
    numero_factura: str

@strawberry.type
class Cliente:
    id: int
    cedula: str
    nombre: str
    apellido: str
    cuentas: List[Cuenta]

@strawberry.type
class Query:

    # @strawberry.field
    # def all_clientes(self, info: Info) -> List[Cliente]:
    #     session = SessionLocal()
    #     clientes = session.query(ClienteModel).all()
    #     return clientes

    @strawberry.field
    def all_clientes(self, info: Info, nombre: Optional[str] = None) -> List[Cliente]:
        session = SessionLocal()
        query = session.query(ClienteModel).options(
                joinedload(ClienteModel.cuentas).joinedload(CuentaModel.pagos)
            )
        if nombre:
            query = query.filter(ClienteModel.nombre == nombre)
        clientes = query.all()
        return clientes
    
    @strawberry.field
    def pagos_por_cuenta(self, info: Info, cuenta: int) -> List[Pago]:
       '''A IMPLEMENTAR'''
       return None

    @strawberry.field
    def all_cuentas(self, info: Info) -> List[Cuenta]:
        session = SessionLocal()
        cuentas = session.query(CuentaModel).all()
        return cuentas

    @strawberry.field
    def all_pagos(self, info: Info) -> List[Pago]:
        session = SessionLocal()
        pagos = session.query(PagosModel).all()
        return pagos

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_cliente(self, info: Info, cedula: str, nombre: str, apellido: str) -> Cliente:
        session = SessionLocal()
        cliente = ClienteModel(cedula=cedula, nombre=nombre, apellido=apellido)
        session.add(cliente)
        session.commit()
        session.refresh(cliente)
        return cliente

    @strawberry.mutation
    def create_cuenta(self, info: Info, cliente_id: int, cuenta: int) -> Cuenta:
        session = SessionLocal()
        cuenta = CuentaModel(cliente_id=cliente_id, cuenta=cuenta)
        session.add(cuenta)
        session.commit()
        session.refresh(cuenta)
        return cuenta

    @strawberry.mutation
    def create_pago(self, info: Info,cuenta_id: int, monto: int, moneda: str, numero_factura: str) -> Pago:
        session = SessionLocal()
        pago = PagosModel(cuenta_id=cuenta_id, monto=monto, moneda=moneda, numero_factura=numero_factura)
        session.add(pago)
        session.commit()
        session.refresh(pago)
        return pago
    
    

schema = strawberry.Schema(query=Query, mutation=Mutation)

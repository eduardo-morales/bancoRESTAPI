import strawberry
from datetime import date
from typing import List, Optional
from strawberry.types import Info
from db import get_db

from models import (
    Colegio as ColegioModel,
    Alumno as AlumnoModel,
    Materia as MateriaModel,
    Matriculacion as MatriculacionModel
)

@strawberry.type
class Colegio:
    id: int
    nombre: str
    direccion: str

@strawberry.type
class Materia:
    id: int
    nombre: str
    curso: int

@strawberry.type
class Alumno:
    id: int
    nombre: str
    apellido: str
    fecha_nacimiento: date
    colegio: Colegio

@strawberry.type
class Matriculacion:
    id: int
    alumno: Alumno
    materia: Materia

# ----------- QUERIES ----------------

@strawberry.type
class Query:
    @strawberry.field
    def colegios(self, info: Info) -> List[Colegio]:
        db = next(get_db())
        return db.query(ColegioModel).all()

    @strawberry.field
    def alumnos(self, info: Info) -> List[Alumno]:
        db = next(get_db())
        return db.query(AlumnoModel).all()

    @strawberry.field
    def materias(self, info: Info) -> List[Materia]:
        db = next(get_db())
        return db.query(MateriaModel).all()

    @strawberry.field
    def matriculaciones(self, info: Info) -> List[Matriculacion]:
        db = next(get_db())
        return db.query(MatriculacionModel).all()

# ----------- MUTATIONS ----------------

@strawberry.type
class Mutation:

    @strawberry.mutation
    def crear_colegio(self, info: Info, nombre: str, direccion: str) -> Colegio:
        db = next(get_db())
        colegio = ColegioModel(nombre=nombre, direccion=direccion)
        db.add(colegio)
        db.commit()
        db.refresh(colegio)
        return colegio

    @strawberry.mutation
    def crear_alumno(self, info: Info, nombre: str, apellido: str, fecha_nacimiento: date, colegio_id: int) -> Alumno:
        db = next(get_db())
        alumno = AlumnoModel(nombre=nombre, apellido=apellido, fecha_nacimiento=fecha_nacimiento, colegio_id=colegio_id)
        db.add(alumno)
        db.commit()
        db.refresh(alumno)
        return alumno
    
    @strawberry.mutation
    def actualizar_alumno(
        self,
        info: Info,
        alumno_id: int,
        nombre: Optional[str] = None,
        apellido: Optional[str] = None,
        fecha_nacimiento: Optional[date] = None,
        colegio_id: Optional[int] = None
    ) -> Optional[Alumno]:
        db = next(get_db())
        alumno = db.query(AlumnoModel).get(alumno_id)
        if not alumno:
            raise Exception("Alumno no encontrado")

        if nombre is not None:
            alumno.nombre = nombre
        if apellido is not None:
            alumno.apellido = apellido
        if fecha_nacimiento is not None:
            alumno.fecha_nacimiento = fecha_nacimiento
        if colegio_id is not None:
            alumno.colegio_id = colegio_id

        db.commit()
        db.refresh(alumno)
        return alumno  
    
    @strawberry.mutation
    def eliminar_alumno(self, info: Info, alumno_id: int) -> bool:
        db = next(get_db())
        alumno = db.query(AlumnoModel).get(alumno_id)
        if not alumno:
            raise Exception("Alumno no encontrado")
        db.delete(alumno)
        db.commit()
        return True

    @strawberry.mutation
    def crear_materia(self, info: Info, nombre: str, curso: int) -> Materia:
        db = next(get_db())
        materia = MateriaModel(nombre=nombre, curso=curso)
        db.add(materia)
        db.commit()
        db.refresh(materia)
        return materia

    @strawberry.mutation
    def matricular_alumno(self, info: Info, alumno_id: int, materia_id: int) -> Matriculacion:
        db = next(get_db())
        matriculacion = MatriculacionModel(alumno_id=alumno_id, materia_id=materia_id)
        db.add(matriculacion)
        db.commit()
        db.refresh(matriculacion)
        return matriculacion

schema = strawberry.Schema(query=Query, mutation=Mutation)

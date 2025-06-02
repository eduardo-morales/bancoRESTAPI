from sqlalchemy import Column, Integer, String, Date, ForeignKey, Table
from sqlalchemy.orm import relationship
from db import Base

# Asociación muchos-a-muchos: alumnos <-> materias
class Colegio(Base):
    __tablename__ = "colegios"
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    direccion = Column(String)

    alumnos = relationship("Alumno", back_populates="colegio")

class Alumno(Base):
    __tablename__ = "alumnos"
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    apellido = Column(String)
    fecha_nacimiento = Column(Date)
    colegio_id = Column(Integer, ForeignKey("colegios.id"))

    colegio = relationship("Colegio", back_populates="alumnos")
    matriculaciones = relationship("Matriculacion", back_populates="alumno")

class Materia(Base):
    __tablename__ = "materias"
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    curso = Column(Integer)

    matriculaciones = relationship("Matriculacion", back_populates="materia")

class Matriculacion(Base):
    __tablename__ = "matriculaciones"
    id = Column(Integer, primary_key=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id"), nullable=False)
    materia_id = Column(Integer, ForeignKey("materias.id"), nullable=False)

    alumno = relationship("Alumno", back_populates="matriculaciones")
    materia = relationship("Materia", back_populates="matriculaciones")

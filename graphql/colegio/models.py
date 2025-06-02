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
    planes_estudios = relationship("PlanEstudios", back_populates="colegio")


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
    profesor_id = Column(Integer, ForeignKey("profesores.id"))
    matriculaciones = relationship("Matriculacion", back_populates="materia")
    planes_estudios = relationship("PlanEstudios", back_populates="materias")
    

class Profesores(Base):
    __tablename__ = "profesores"
    id = Column(Integer, primary_key=True)
    nombre = Column(String)

    materias = relationship("Materia", back_populates="profesor")

class Matriculacion(Base):
    __tablename__ = "matriculaciones"
    id = Column(Integer, primary_key=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id"), nullable=False)
    materia_id = Column(Integer, ForeignKey("materias.id"), nullable=False)
    anho_lectivo = Column(Integer, nullable=False)

    alumno = relationship("Alumno", back_populates="matriculaciones")
    materia = relationship("Materia", back_populates="matriculaciones")

class Curso(Base):
    id = Column(Integer, primary_key=True)
    curso= Column(Integer, nullable=False)
    seccion = Column(String, nullable=False)
    
class PlanEstudios(Base):
    __tablename__ = "planes_estudios"
    id = Column(Integer, primary_key=True)
    materia_id = Column(Integer, ForeignKey("materias.id"), nullable=False)
    colegio_id = Column(Integer, ForeignKey("colegios.id"), nullable=False)
    curso = Column(Integer, nullable=False)

    materia = relationship("Materia", back_populates="planes_estudios")
    colegio = relationship("Colegio", back_populates="planes_estudios")

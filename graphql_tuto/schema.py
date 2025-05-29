import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

@strawberry.type
class Colegio:
    name: str
    direccion: str

@strawberry.type
class Alumno:
    name: str
    age: int
    colegio: Colegio


@strawberry.type
class Query:
    @strawberry.field
    def consultar_usuario(self) -> Alumno:
        colegio = Colegio(name="Colegio Nacional de Buenos Aires", direccion="CABA, Argentina")
        return Alumno(name="Patrick", age=100, colegio=colegio)
    
    @strawberry.field
    def consultar_colegios(self) -> list[Colegio]:
        return [Colegio(name="Colegio Nacional de Buenos Aires", direccion="CABA, Argentina")]


schema = strawberry.Schema(query=Query)


graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
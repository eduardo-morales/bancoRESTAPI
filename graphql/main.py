from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from schema import schema
from db import init_db

app = FastAPI()

# Inicializa la base de datos y crea las tablas si no existen
init_db()

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
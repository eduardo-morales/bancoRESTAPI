# client_gql.py
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def get_clients_named(name):
    transport = RequestsHTTPTransport(
        url='http://localhost:8000/graphql',
        use_json=True,
    )

    client = Client(transport=transport, fetch_schema_from_transport=True)

    query = gql("""
    query ($name: String) {
      alumnos(nombre: $name) {
        id
        nombre
        apellido
      }
    }
    """)

    params = {"name": name}
    result = client.execute(query, variable_values=params)
    return result['alumnos']

if __name__ == "__main__":
    nombre = "Eduardo"
    clientes = get_clients_named(nombre)
    for cliente in clientes:
        print(f"ID: {cliente['id']},  Nombre: {cliente['nombre']}, Apellido: {cliente['apellido']}")

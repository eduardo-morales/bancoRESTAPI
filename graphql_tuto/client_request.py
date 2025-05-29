# client_requests.py
import requests

def get_alumnos():
    url = "http://localhost:8000/graphql"
    squery = """
    query {
      consultarUsuario {
        age,
        colegio {
          direccion
        }       
      }
    }
    """
    
    response = requests.post(url, json={'query': squery,})
    if response.status_code == 200:
        result = response.json()
        return result['data']
    else:
        raise Exception(f"Query failed to run by returning code of {response.status_code}. {response.text}")

if __name__ == "__main__":
    alumno = get_alumnos()
    print(alumno)
    #print(f"Edad: {alumno['age']}, Direccion del colegio: {alumno['colegio']['direccion']}")

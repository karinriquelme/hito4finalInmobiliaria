import os
import django
from django.db import connection

# Establecer la ruta base del proyecto Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

# Cambiar al directorio del proyecto Djangom 
os.chdir(BASE_DIR)



def fetch_data_from_db():
    with connection.cursor() as cursor:
        # Ejecutar la consulta SQL
        query = """
        SELECT 
          *
        FROM 
        web_inmueble
        
        """
        cursor.execute(query)
        # Obtener todos los resultados
        rows = cursor.fetchall()
    return rows


def save_data_to_txt(rows, file_path):
    with open(file_path, 'w') as file:
        for row in rows:
            file.write(str(row) + '\n')    
            
def export_data_to_txt():
    # Paso 1: Obtener los datos de la base de datos
    rows = fetch_data_from_db()

    # Paso 2: Guardar los datos en un archivo de texto
    file_path = 'solicitudes_arriendo.txt'
    save_data_to_txt(rows, file_path)

    print(f"Data saved to {file_path}")

if __name__ == '__main__':
    export_data_to_txt()
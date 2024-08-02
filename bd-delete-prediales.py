import sqlite3
import os 

# Conexión a la base de datos
conn = sqlite3.connect('db.sqlite3')

# Creación del cursor
cursor = conn.cursor()

# Eliminación de registros de la tabla PredialSearch
cursor.execute('DELETE FROM prediales')

# Confirmación de la transacción
conn.commit()

# Cierre de la conexión
conn.close()

# Respuesta
print('Se han eliminado los registros de la tabla PredialSearch.')

# Borrar todos los pdfs en la carpeta media
for file in os.listdir('media'):
    if file.endswith('.pdf'):
        os.remove(f'media/{file}')
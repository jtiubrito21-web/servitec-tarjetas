SERVITEC TARJETAS - VERSION PERSISTENTE

NUEVO
- Base persistente con PostgreSQL usando DATABASE_URL
- Vista mejorada para telefonos
- Editar registros
- Eliminar registros

LOCAL
1. pip install -r requirements.txt
2. python app.py
3. abrir http://127.0.0.1:5000

RENDER
1. Crear una base PostgreSQL en Render
2. Copiar la External Database URL
3. En el Web Service > Environment:
   DATABASE_URL = pegar la URL
   SECRET_KEY = una clave larga
4. Deploy nuevamente

LOGIN
Usuario: admin
Contraseña: 1234

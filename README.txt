
SISTEMA SERVITEC - TARJETAS DE INTERNET

INICIO RÁPIDO

1. Descomprime el archivo ZIP.
2. Abre la carpeta.
3. En la barra de dirección de la carpeta escribe: cmd
4. En la ventana negra ejecuta:

pip install -r requirements.txt

5. Luego ejecuta:

python app.py

6. Abre en tu navegador:

http://127.0.0.1:5000

DATOS DE INGRESO
Usuario: admin
Contraseña: 1234

PUNTOS DE VENTA CONFIGURADOS
- Seño Manuela
- Jacinta Terraza
- Don Martín
- Ana Pastor
- Isabela Pastor
- Marta Bernal
- Jacinto Raymundo
- Doña María
- Punto 9
- Punto 10

CAMBIAR CONTRASEÑA
Abre el archivo app.py y busca estas líneas:

USUARIO_ADMIN = "admin"
CLAVE_ADMIN = "1234"

Puedes cambiar la contraseña allí.

SUBIR A INTERNET
Cuando quieras subirlo a Render:
Build Command:
pip install -r requirements.txt

Start Command:
gunicorn app:app

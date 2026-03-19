
from flask import Flask, request, redirect, url_for, render_template_string, session, send_file, flash
import sqlite3
from pathlib import Path
from io import BytesIO
import qrcode

app = Flask(__name__)
app.secret_key = "servitec-2026-clave-segura-987654321"

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data.db"

PUNTOS = [
    "Seño Manuela",
    "Jacinta Terraza",
    "Don Martín",
    "Ana Pastor",
    "Isabela Pastor",
    "Marta Bernal",
    "Jacinto Raymundo",
    "Doña María",
    "Punto 9",
    "Punto 10",
]

USUARIO_ADMIN = "admin"
CLAVE_ADMIN = "1234"

HTML_BASE = """
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ titulo }}</title>
<style>
    :root{
        --negro:#0f1115;
        --gris:#171a21;
        --verde:#0f5132;
        --verde2:#198754;
        --verde3:#1f7a4d;
        --claro:#f5f7f8;
        --borde:#2b303b;
        --texto:#e9ecef;
        --muted:#aab2bd;
        --blanco:#ffffff;
        --warning:#ffc107;
    }
    *{box-sizing:border-box}
    body{
        margin:0;
        font-family:Arial, Helvetica, sans-serif;
        background:linear-gradient(180deg,#101318,#0d0f13);
        color:var(--texto);
    }
    .topbar{
        background:#0b0d11;
        border-bottom:1px solid var(--borde);
        padding:16px 22px;
        display:flex;
        align-items:center;
        justify-content:space-between;
        gap:12px;
        position:sticky;
        top:0;
    }
    .brand{
        font-size:22px;
        font-weight:700;
        color:#fff;
    }
    .brand span{color:#39d98a}
    .wrap{
        max-width:1200px;
        margin:24px auto;
        padding:0 16px;
    }
    .card{
        background:rgba(23,26,33,.96);
        border:1px solid var(--borde);
        border-radius:18px;
        padding:20px;
        margin-bottom:18px;
        box-shadow:0 10px 24px rgba(0,0,0,.20);
    }
    h1,h2,h3{margin-top:0}
    .nav{
        display:flex;
        flex-wrap:wrap;
        gap:10px;
    }
    .btn{
        display:inline-block;
        background:var(--verde2);
        color:#fff;
        padding:10px 15px;
        border-radius:12px;
        text-decoration:none;
        border:none;
        cursor:pointer;
        font-weight:700;
    }
    .btn:hover{filter:brightness(1.05)}
    .btn.dark{background:#212734}
    .btn.outline{background:transparent;border:1px solid #2f8f60}
    .btn.red{background:#7a1c1c}
    .grid{
        display:grid;
        grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
        gap:14px;
    }
    label{
        display:block;
        margin-bottom:6px;
        font-weight:700;
        color:#dfe5eb;
        font-size:14px;
    }
    input,select,textarea{
        width:100%;
        padding:11px 12px;
        border-radius:12px;
        border:1px solid #394150;
        background:#0f1319;
        color:#fff;
        outline:none;
    }
    textarea{min-height:120px; resize:vertical}
    table{
        width:100%;
        border-collapse:collapse;
    }
    th,td{
        padding:11px;
        border-bottom:1px solid #2c3340;
        text-align:left;
        vertical-align:top;
        font-size:14px;
    }
    th{
        background:#11161d;
        color:#fff;
    }
    .badge{
        display:inline-block;
        padding:5px 10px;
        border-radius:999px;
        font-size:12px;
        font-weight:700;
    }
    .ok{background:#173a2b;color:#78e0ab}
    .pending{background:#4e3b09;color:#ffd667}
    .muted{color:var(--muted)}
    .flash{
        background:#133322;
        border:1px solid #215f3f;
        color:#d9ffea;
        padding:12px 14px;
        border-radius:12px;
        margin-bottom:16px;
    }
    .two{
        display:grid;
        grid-template-columns:1.3fr .7fr;
        gap:18px;
    }
    .stats{
        display:grid;
        grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
        gap:14px;
    }
    .stat{
        background:#10161d;
        border:1px solid #2d3441;
        border-radius:16px;
        padding:18px;
    }
    .stat .n{
        font-size:28px;
        font-weight:700;
        color:#fff;
        margin-top:8px;
    }
    .center{text-align:center}
    .qr-img{
        width:170px;
        height:170px;
        background:#fff;
        padding:8px;
        border-radius:14px;
    }
    .loginbox{
        max-width:430px;
        margin:60px auto;
    }
    .small{font-size:12px}
    @media(max-width:900px){
        .two{grid-template-columns:1fr}
    }
</style>
</head>
<body>
    {% if mostrar_menu %}
    <div class="topbar">
        <div class="brand">Servi<span>Tec</span> - Tarjetas de Internet</div>
        <div class="nav">
            <a class="btn dark" href="{{ url_for('inicio') }}">Inicio</a>
            {% if session.get('user') %}
            <a class="btn" href="{{ url_for('nuevo') }}">Nuevo Registro</a>
            <a class="btn dark" href="{{ url_for('registros') }}">Registros</a>
            <a class="btn dark" href="{{ url_for('puntos') }}">Puntos y QR</a>
            <a class="btn red" href="{{ url_for('logout') }}">Salir</a>
            {% endif %}
        </div>
    </div>
    {% endif %}
    <div class="wrap">
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for m in messages %}
                    <div class="flash">{{ m }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        {{ body|safe }}
    </div>
</body>
</html>
"""

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS registros(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            punto TEXT NOT NULL,
            fecha TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            plan TEXT NOT NULL,
            precio REAL NOT NULL,
            total REAL NOT NULL,
            codigos TEXT NOT NULL,
            estado TEXT NOT NULL,
            fecha_pago TEXT,
            forma_pago TEXT
        )
    """)
    conn.commit()
    conn.close()

def render_page(titulo, body, mostrar_menu=True, **context):
    html = render_template_string(body, **context)
    return render_template_string(
        HTML_BASE,
        titulo=titulo,
        body=html,
        mostrar_menu=mostrar_menu,
        session=session
    )

def login_required():
    return session.get("user") == USUARIO_ADMIN

@app.route("/")
def inicio():
    if not login_required():
        return redirect(url_for("login"))

    conn = get_db()
    total_registros = conn.execute("SELECT COUNT(*) FROM registros").fetchone()[0]
    total_tarjetas = conn.execute("SELECT COALESCE(SUM(cantidad),0) FROM registros").fetchone()[0]
    total_pendiente = conn.execute("SELECT COALESCE(SUM(total),0) FROM registros WHERE estado='Pendiente'").fetchone()[0]
    ultimos = conn.execute("SELECT * FROM registros ORDER BY id DESC LIMIT 8").fetchall()
    conn.close()

    body = """
    <div class="two">
        <div class="card">
            <h2>Panel principal</h2>
            <p class="muted">Sistema para control de paquetes de tarjetas por punto de venta.</p>
            <div class="stats">
                <div class="stat">
                    <div class="muted">Registros</div>
                    <div class="n">{{ total_registros }}</div>
                </div>
                <div class="stat">
                    <div class="muted">Tarjetas entregadas</div>
                    <div class="n">{{ total_tarjetas }}</div>
                </div>
                <div class="stat">
                    <div class="muted">Saldo pendiente</div>
                    <div class="n">Q {{ '%.2f'|format(total_pendiente) }}</div>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>Acceso rápido</h2>
            <div class="nav">
                <a class="btn" href="{{ url_for('nuevo') }}">Registrar paquete</a>
                <a class="btn dark" href="{{ url_for('puntos') }}">Ver QR</a>
                <a class="btn dark" href="{{ url_for('registros') }}">Historial</a>
            </div>
            <p class="small muted" style="margin-top:16px;">
                Usuario inicial: <b>admin</b><br>
                Clave inicial: <b>1234</b><br>
                Puedes cambiarla después en el archivo <b>app.py</b>.
            </p>
        </div>
    </div>

    <div class="card">
        <h2>Últimos registros</h2>
        <table>
            <thead>
                <tr>
                    <th>Fecha</th>
                    <th>Punto</th>
                    <th>Cantidad</th>
                    <th>Plan</th>
                    <th>Total</th>
                    <th>Pago</th>
                </tr>
            </thead>
            <tbody>
                {% for r in ultimos %}
                <tr>
                    <td>{{ r['fecha'] }}</td>
                    <td>{{ r['punto'] }}</td>
                    <td>{{ r['cantidad'] }}</td>
                    <td>{{ r['plan'] }}</td>
                    <td>Q {{ '%.2f'|format(r['total']) }}</td>
                    <td>
                        {% if r['estado'] == 'Cancelado' %}
                            <span class="badge ok">Cancelado</span>
                        {% else %}
                            <span class="badge pending">Pendiente</span>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
                {% if not ultimos %}
                <tr><td colspan="6" class="muted">Aún no hay registros.</td></tr>
                {% endif %}
            </tbody>
        </table>
    </div>
    """
    return render_page("Inicio", body, total_registros=total_registros, total_tarjetas=total_tarjetas, total_pendiente=total_pendiente, ultimos=ultimos)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form.get("usuario", "").strip()
        c = request.form.get("clave", "").strip()
        if u == USUARIO_ADMIN and c == CLAVE_ADMIN:
            session["user"] = USUARIO_ADMIN
            return redirect(url_for("inicio"))
        flash("Usuario o contraseña incorrectos.")

    body = """
    <div class="loginbox card">
        <h2>Ingreso al sistema</h2>
        <p class="muted">Acceso de administrador</p>
        <form method="post">
            <div style="margin-bottom:14px;">
                <label>Usuario</label>
                <input name="usuario" required>
            </div>
            <div style="margin-bottom:14px;">
                <label>Contraseña</label>
                <input name="clave" type="password" required>
            </div>
            <button class="btn" type="submit">Entrar</button>
        </form>
    </div>
    """
    return render_page("Login", body, mostrar_menu=False)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    if not login_required():
        return redirect(url_for("login"))

    if request.method == "POST":
        punto = request.form.get("punto")
        fecha = request.form.get("fecha")
        cantidad = request.form.get("cantidad")
        plan = request.form.get("plan")
        precio = request.form.get("precio")
        codigos = request.form.get("codigos")
        estado = request.form.get("estado")
        fecha_pago = request.form.get("fecha_pago")
        forma_pago = request.form.get("forma_pago")

        try:
            cantidad = int(cantidad)
            precio = float(precio)
            total = cantidad * precio
        except Exception:
            flash("Cantidad o precio inválido.")
            return redirect(url_for("nuevo"))

        conn = get_db()
        conn.execute(
            "INSERT INTO registros (punto, fecha, cantidad, plan, precio, total, codigos, estado, fecha_pago, forma_pago) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (punto, fecha, cantidad, plan, precio, total, codigos, estado, fecha_pago, forma_pago)
        )
        conn.commit()
        conn.close()
        flash("Registro guardado correctamente.")
        return redirect(url_for("registros"))

    body = """
    <div class="card">
        <h2>Registrar paquete de tarjetas</h2>
        <form method="post">
            <div class="grid">
                <div>
                    <label>Punto de venta</label>
                    <select name="punto" required>
                        {% for p in puntos %}<option value="{{ p }}">{{ p }}</option>{% endfor %}
                    </select>
                </div>
                <div>
                    <label>Fecha</label>
                    <input type="date" name="fecha" required>
                </div>
                <div>
                    <label>Cantidad</label>
                    <input type="number" min="1" name="cantidad" required>
                </div>
                <div>
                    <label>Plan</label>
                    <select name="plan" required>
                        <option>Hora</option>
                        <option>Día</option>
                        <option>Semana</option>
                        <option>Mes</option>
                    </select>
                </div>
                <div>
                    <label>Precio Unitario</label>
                    <input type="number" step="0.01" min="0" name="precio" required>
                </div>
                <div>
                    <label>Estado de pago</label>
                    <select name="estado" required>
                        <option>Cancelado</option>
                        <option>Pendiente</option>
                    </select>
                </div>
                <div>
                    <label>Fecha de pago</label>
                    <input type="date" name="fecha_pago">
                </div>
                <div>
                    <label>Forma de pago</label>
                    <select name="forma_pago">
                        <option value="">Seleccione</option>
                        <option>Efectivo</option>
                        <option>Transferencia</option>
                        <option>Depósito</option>
                    </select>
                </div>
            </div>
            <div style="margin-top:14px;">
                <label>Códigos de tarjetas</label>
                <textarea name="codigos" placeholder="Escribe una tarjeta por línea o separadas por coma" required></textarea>
            </div>
            <div style="margin-top:16px;">
                <button class="btn" type="submit">Guardar registro</button>
            </div>
        </form>
    </div>
    """
    return render_page("Nuevo registro", body, puntos=PUNTOS)

@app.route("/registros")
def registros():
    if not login_required():
        return redirect(url_for("login"))

    conn = get_db()
    data = conn.execute("SELECT * FROM registros ORDER BY id DESC").fetchall()
    conn.close()

    body = """
    <div class="card">
        <h2>Historial de registros</h2>
        <table>
            <thead>
                <tr>
                    <th>Fecha</th>
                    <th>Punto</th>
                    <th>Cantidad</th>
                    <th>Plan</th>
                    <th>Precio</th>
                    <th>Total</th>
                    <th>Pago</th>
                    <th>Fecha pago</th>
                    <th>Forma</th>
                </tr>
            </thead>
            <tbody>
                {% for r in data %}
                <tr>
                    <td>{{ r['fecha'] }}</td>
                    <td>{{ r['punto'] }}</td>
                    <td>{{ r['cantidad'] }}</td>
                    <td>{{ r['plan'] }}</td>
                    <td>Q {{ '%.2f'|format(r['precio']) }}</td>
                    <td>Q {{ '%.2f'|format(r['total']) }}</td>
                    <td>
                        {% if r['estado'] == 'Cancelado' %}
                        <span class="badge ok">Cancelado</span>
                        {% else %}
                        <span class="badge pending">Pendiente</span>
                        {% endif %}
                    </td>
                    <td>{{ r['fecha_pago'] or '' }}</td>
                    <td>{{ r['forma_pago'] or '' }}</td>
                </tr>
                <tr>
                    <td colspan="9" class="muted"><b>Códigos:</b><br><div style="white-space:pre-line">{{ r['codigos'] }}</div></td>
                </tr>
                {% endfor %}
                {% if not data %}
                <tr><td colspan="9" class="muted">No hay registros todavía.</td></tr>
                {% endif %}
            </tbody>
        </table>
    </div>
    """
    return render_page("Registros", body, data=data)

@app.route("/puntos")
def puntos():
    if not login_required():
        return redirect(url_for("login"))

    body = """
    <div class="card">
        <h2>Puntos de venta y QR</h2>
        <p class="muted">Cada punto puede abrir su enlace o escanear su código QR para ver sus datos.</p>
        <div class="grid">
            {% for p in puntos %}
            <div class="card center" style="margin-bottom:0;">
                <h3>{{ p }}</h3>
                <img class="qr-img" src="{{ url_for('qr_punto', punto=p) }}">
                <p class="small"><a class="btn outline" href="{{ url_for('vista_publica', punto=p) }}" target="_blank">Abrir enlace</a></p>
            </div>
            {% endfor %}
        </div>
    </div>
    """
    return render_page("Puntos", body, puntos=PUNTOS)

@app.route("/qr/<path:punto>")
def qr_punto(punto):
    url = request.host_url.rstrip("/") + url_for("vista_publica", punto=punto)
    img = qrcode.make(url)
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

@app.route("/p/<path:punto>")
def vista_publica(punto):
    conn = get_db()
    data = conn.execute("SELECT * FROM registros WHERE punto=? ORDER BY id DESC", (punto,)).fetchall()
    total_tarjetas = conn.execute("SELECT COALESCE(SUM(cantidad),0) FROM registros WHERE punto=?", (punto,)).fetchone()[0]
    pendiente = conn.execute("SELECT COALESCE(SUM(total),0) FROM registros WHERE punto=? AND estado='Pendiente'", (punto,)).fetchone()[0]
    conn.close()

    body = """
    <div class="card">
        <h2>{{ punto }}</h2>
        <p class="muted">Consulta del punto de venta</p>
        <div class="stats">
            <div class="stat">
                <div class="muted">Registros</div>
                <div class="n">{{ data|length }}</div>
            </div>
            <div class="stat">
                <div class="muted">Tarjetas</div>
                <div class="n">{{ total_tarjetas }}</div>
            </div>
            <div class="stat">
                <div class="muted">Saldo pendiente</div>
                <div class="n">Q {{ '%.2f'|format(pendiente) }}</div>
            </div>
        </div>
    </div>

    <div class="card">
        <h2>Historial</h2>
        <table>
            <thead>
                <tr>
                    <th>Fecha</th>
                    <th>Cantidad</th>
                    <th>Plan</th>
                    <th>Total</th>
                    <th>Pago</th>
                    <th>Fecha pago</th>
                    <th>Forma</th>
                </tr>
            </thead>
            <tbody>
                {% for r in data %}
                <tr>
                    <td>{{ r['fecha'] }}</td>
                    <td>{{ r['cantidad'] }}</td>
                    <td>{{ r['plan'] }}</td>
                    <td>Q {{ '%.2f'|format(r['total']) }}</td>
                    <td>
                        {% if r['estado'] == 'Cancelado' %}
                        <span class="badge ok">Cancelado</span>
                        {% else %}
                        <span class="badge pending">Pendiente</span>
                        {% endif %}
                    </td>
                    <td>{{ r['fecha_pago'] or '' }}</td>
                    <td>{{ r['forma_pago'] or '' }}</td>
                </tr>
                <tr>
                    <td colspan="7" class="muted"><b>Códigos:</b><br><div style="white-space:pre-line">{{ r['codigos'] }}</div></td>
                </tr>
                {% endfor %}
                {% if not data %}
                <tr><td colspan="7" class="muted">Sin registros todavía.</td></tr>
                {% endif %}
            </tbody>
        </table>
    </div>
    """
    return render_page(punto, body, punto=punto, data=data, total_tarjetas=total_tarjetas, pendiente=pendiente)

init_db()

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

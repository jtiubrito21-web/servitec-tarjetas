
from flask import Flask, request, redirect, url_for, render_template_string, session, send_file, flash
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
import qrcode, os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "servitec-2026-clave-segura-987654321")

database_url = os.environ.get("DATABASE_URL", "sqlite:///data.db")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

PUNTOS = ["Seño Manuela","Jacinta Terraza","Don Martín","Ana Pastor","Isabela Pastor","Marta Bernal","Jacinto Raymundo","Doña María","Punto 9","Punto 10"]
USUARIO_ADMIN = os.environ.get("ADMIN_USER", "admin")
CLAVE_ADMIN = os.environ.get("ADMIN_PASSWORD", "1234")

class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    punto = db.Column(db.String(120), nullable=False)
    fecha = db.Column(db.String(20), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    plan = db.Column(db.String(20), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    codigos = db.Column(db.Text, nullable=False)
    estado = db.Column(db.String(20), nullable=False)
    fecha_pago = db.Column(db.String(20))
    forma_pago = db.Column(db.String(50))

with app.app_context():
    db.create_all()

BASE = """
<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ titulo }}</title>
<style>
:root{--n:#0f1115;--g:#171a21;--g2:#11161d;--v:#198754;--vo:#0f5132;--t:#e9ecef;--m:#b8c0cc;--b:#2b303b;--r:#a11b1b}
*{box-sizing:border-box} body{margin:0;font-family:Arial,Helvetica,sans-serif;background:linear-gradient(180deg,#101318,#0d0f13);color:var(--t)}
.top{background:#0b0d11;border-bottom:1px solid var(--b);padding:14px 18px;display:flex;justify-content:space-between;align-items:center;gap:12px;position:sticky;top:0;z-index:5;flex-wrap:wrap}
.brand{font-size:24px;font-weight:700;color:#fff}.brand span{color:#39d98a}.wrap{max-width:1200px;margin:20px auto;padding:0 12px 30px}
.nav{display:flex;flex-wrap:wrap;gap:8px}.btn{display:inline-block;background:var(--v);color:#fff;padding:10px 14px;border-radius:12px;text-decoration:none;border:none;cursor:pointer;font-weight:700;font-size:14px}
.btn.dark{background:#212734}.btn.outline{background:transparent;border:1px solid #2f8f60}.btn.red{background:var(--r)}.btn.small{padding:7px 10px;border-radius:10px;font-size:13px}
.card{background:rgba(23,26,33,.96);border:1px solid var(--b);border-radius:18px;padding:16px;margin-bottom:16px;box-shadow:0 10px 24px rgba(0,0,0,.20)}
h1,h2,h3{margin-top:0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px}
.stat{background:#10161d;border:1px solid #2d3441;border-radius:16px;padding:16px}.stat .n{font-size:28px;font-weight:700;color:#fff;margin-top:8px;word-break:break-word}
label{display:block;margin-bottom:6px;font-weight:700;font-size:14px}input,select,textarea{width:100%;padding:11px 12px;border-radius:12px;border:1px solid #394150;background:#0f1319;color:#fff;outline:none}
textarea{min-height:120px;resize:vertical}.muted{color:var(--m)}.flash{background:#133322;border:1px solid #215f3f;color:#d9ffea;padding:12px 14px;border-radius:12px;margin-bottom:16px}
.badge{display:inline-block;padding:5px 10px;border-radius:999px;font-size:12px;font-weight:700}.ok{background:#173a2b;color:#78e0ab}.pending{background:#4e3b09;color:#ffd667}
.center{text-align:center}.qr-img{width:170px;height:170px;background:#fff;padding:8px;border-radius:14px}.loginbox{max-width:430px;margin:50px auto}.two{display:grid;grid-template-columns:1.25fr .75fr;gap:16px}
.table-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch}table{width:100%;border-collapse:collapse;min-width:780px}th,td{padding:11px;border-bottom:1px solid #2c3340;text-align:left;vertical-align:top;font-size:14px}th{background:var(--g2);color:#fff}
.small{font-size:12px}.code-box{white-space:pre-line;word-break:break-word;max-width:100%}.mobile-cards{display:none}.record-card{background:#10161d;border:1px solid #2d3441;border-radius:16px;padding:14px;margin-bottom:12px}
.row-actions{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}.field{margin-bottom:8px;font-size:14px}.field b{color:#fff}
@media(max-width:900px){.two{grid-template-columns:1fr}}@media(max-width:768px){.top{padding:12px}.brand{font-size:20px}.wrap{padding:0 10px 24px}.card{padding:14px}table{min-width:680px}}
@media(max-width:620px){.desktop-table{display:none}.mobile-cards{display:block}.qr-img{width:150px;height:150px}.btn{width:100%;text-align:center}.nav .btn{width:auto}.top .nav{width:100%}}
</style></head><body>{% if mostrar_menu %}<div class="top"><div class="brand">Servi<span>Tec</span> - Tarjetas de Internet</div><div class="nav">{% if session.get('user') %}<a class="btn dark" href="{{ url_for('inicio') }}">Inicio</a><a class="btn" href="{{ url_for('nuevo') }}">Nuevo</a><a class="btn dark" href="{{ url_for('registros') }}">Registros</a><a class="btn dark" href="{{ url_for('puntos') }}">Puntos y QR</a><a class="btn red" href="{{ url_for('logout') }}">Salir</a>{% endif %}</div></div>{% endif %}
<div class="wrap">{% with messages = get_flashed_messages() %}{% if messages %}{% for m in messages %}<div class="flash">{{ m }}</div>{% endfor %}{% endif %}{% endwith %}{{ body|safe }}</div></body></html>
"""

def render_page(titulo, body, mostrar_menu=True, **context):
    html = render_template_string(body, **context)
    return render_template_string(BASE, titulo=titulo, body=html, mostrar_menu=mostrar_menu, session=session)

def logged():
    return session.get("user") == USUARIO_ADMIN


@app.route("/")
def inicio():
    return redirect(url_for("nuevo"))
 
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if request.form.get("usuario","").strip() == USUARIO_ADMIN and request.form.get("clave","").strip() == CLAVE_ADMIN:
            session["user"] = USUARIO_ADMIN
            return redirect(url_for("inicio"))
        flash("Usuario o contraseña incorrectos.")
    body = '<div class="loginbox card"><h2>Ingreso al sistema</h2><p class="muted">Acceso de administrador</p><form method="post"><div style="margin-bottom:14px;"><label>Usuario</label><input name="usuario" required></div><div style="margin-bottom:14px;"><label>Contraseña</label><input name="clave" type="password" required></div><button class="btn" type="submit">Entrar</button></form></div>'
    return render_page("Login", body, mostrar_menu=False)

@app.route("/logout")
def logout():
    session.clear(); return redirect(url_for("login"))

@app.route("/nuevo", methods=["GET","POST"])
def nuevo():
    if not logged(): return redirect(url_for("login"))
    if request.method == "POST":
        try:
            cantidad = int(request.form.get("cantidad","0")); precio = float(request.form.get("precio","0"))
        except ValueError:
            flash("Cantidad o precio inválido."); return redirect(url_for("nuevo"))
        reg = Registro(punto=request.form.get("punto"), fecha=request.form.get("fecha"), cantidad=cantidad, plan=request.form.get("plan"), precio=precio, total=cantidad*precio, codigos=request.form.get("codigos"), estado=request.form.get("estado"), fecha_pago=request.form.get("fecha_pago") or None, forma_pago=request.form.get("forma_pago") or None)
        db.session.add(reg); db.session.commit(); flash("Registro guardado correctamente."); return redirect(url_for("registros"))
    body = """
    <div class="card"><h2>Registrar paquete de tarjetas</h2><form method="post"><div class="grid">
    <div><label>Punto de venta</label><select name="punto" required>{% for p in puntos %}<option value="{{ p }}">{{ p }}</option>{% endfor %}</select></div>
    <div><label>Fecha</label><input type="date" name="fecha" required></div>
    <div><label>Cantidad</label><input type="number" min="1" name="cantidad" required></div>
    <div><label>Plan</label><select name="plan" required><option>Hora</option><option>Día</option><option>Semana</option><option>Mes</option></select></div>
    <div><label>Precio Unitario</label><input type="number" step="0.01" min="0" name="precio" required></div>
    <div><label>Estado de pago</label><select name="estado" required><option>Cancelado</option><option>Pendiente</option></select></div>
    <div><label>Fecha de pago</label><input type="date" name="fecha_pago"></div>
    <div><label>Forma de pago</label><select name="forma_pago"><option value="">Seleccione</option><option>Efectivo</option><option>Transferencia</option><option>Depósito</option></select></div>
    </div><div style="margin-top:14px;"><label>Códigos de tarjetas</label><textarea name="codigos" placeholder="Escribe una tarjeta por línea o separadas por coma" required></textarea></div><div style="margin-top:16px;"><button class="btn" type="submit">Guardar registro</button></div></form></div>
    """
    return render_page("Nuevo registro", body, puntos=PUNTOS)

@app.route("/editar/<int:registro_id>", methods=["GET","POST"])
def editar(registro_id):
    if not logged(): return redirect(url_for("login"))
    reg = Registro.query.get_or_404(registro_id)
    if request.method == "POST":
        try:
            cantidad = int(request.form.get("cantidad","0")); precio = float(request.form.get("precio","0"))
        except ValueError:
            flash("Cantidad o precio inválido."); return redirect(url_for("editar", registro_id=registro_id))
        reg.punto=request.form.get("punto"); reg.fecha=request.form.get("fecha"); reg.cantidad=cantidad; reg.plan=request.form.get("plan"); reg.precio=precio; reg.total=cantidad*precio; reg.codigos=request.form.get("codigos"); reg.estado=request.form.get("estado"); reg.fecha_pago=request.form.get("fecha_pago") or None; reg.forma_pago=request.form.get("forma_pago") or None
        db.session.commit(); flash("Registro actualizado correctamente."); return redirect(url_for("registros"))
    body = """
    <div class="card"><h2>Editar registro</h2><form method="post"><div class="grid">
    <div><label>Punto de venta</label><select name="punto" required>{% for p in puntos %}<option value="{{ p }}" {% if reg.punto == p %}selected{% endif %}>{{ p }}</option>{% endfor %}</select></div>
    <div><label>Fecha</label><input type="date" name="fecha" value="{{ reg.fecha }}" required></div>
    <div><label>Cantidad</label><input type="number" min="1" name="cantidad" value="{{ reg.cantidad }}" required></div>
    <div><label>Plan</label><select name="plan" required>{% for p in ['Hora','Día','Semana','Mes'] %}<option value="{{ p }}" {% if reg.plan == p %}selected{% endif %}>{{ p }}</option>{% endfor %}</select></div>
    <div><label>Precio Unitario</label><input type="number" step="0.01" min="0" name="precio" value="{{ reg.precio }}" required></div>
    <div><label>Estado de pago</label><select name="estado" required>{% for e in ['Cancelado','Pendiente'] %}<option value="{{ e }}" {% if reg.estado == e %}selected{% endif %}>{{ e }}</option>{% endfor %}</select></div>
    <div><label>Fecha de pago</label><input type="date" name="fecha_pago" value="{{ reg.fecha_pago or '' }}"></div>
    <div><label>Forma de pago</label><select name="forma_pago"><option value="">Seleccione</option>{% for f in ['Efectivo','Transferencia','Depósito'] %}<option value="{{ f }}" {% if reg.forma_pago == f %}selected{% endif %}>{{ f }}</option>{% endfor %}</select></div>
    </div><div style="margin-top:14px;"><label>Códigos de tarjetas</label><textarea name="codigos" required>{{ reg.codigos }}</textarea></div><div style="margin-top:16px;" class="row-actions"><button class="btn" type="submit">Guardar cambios</button><a class="btn dark" href="{{ url_for('registros') }}">Cancelar</a></div></form></div>
    """
    return render_page("Editar registro", body, reg=reg, puntos=PUNTOS)

@app.route("/eliminar/<int:registro_id>", methods=["POST"])
def eliminar(registro_id):
    if not logged(): return redirect(url_for("login"))
    reg = Registro.query.get_or_404(registro_id); db.session.delete(reg); db.session.commit(); flash("Registro eliminado correctamente."); return redirect(url_for("registros"))

@app.route("/registros")
def registros():
    if not logged(): return redirect(url_for("login"))
    data = Registro.query.order_by(Registro.id.desc()).all()
    body = """
    <div class="card"><h2>Historial de registros</h2>
    <div class="desktop-table table-wrap"><table><thead><tr><th>Fecha</th><th>Punto</th><th>Cantidad</th><th>Plan</th><th>Total</th><th>Pago</th><th>Fecha pago</th><th>Forma</th><th>Acciones</th></tr></thead><tbody>
    {% for r in data %}<tr><td>{{ r.fecha }}</td><td>{{ r.punto }}</td><td>{{ r.cantidad }}</td><td>{{ r.plan }}</td><td>Q {{ '%.2f'|format(r.total) }}</td><td>{% if r.estado == 'Cancelado' %}<span class="badge ok">Cancelado</span>{% else %}<span class="badge pending">Pendiente</span>{% endif %}</td><td>{{ r.fecha_pago or '' }}</td><td>{{ r.forma_pago or '' }}</td><td><div class="row-actions"><a class="btn small dark" href="{{ url_for('editar', registro_id=r.id) }}">Editar</a><form method="post" action="{{ url_for('eliminar', registro_id=r.id) }}" onsubmit="return confirm('¿Eliminar este registro?');"><button class="btn small red" type="submit">Eliminar</button></form></div></td></tr>
    <tr><td colspan="9" class="muted"><b>Códigos:</b><br><div class="code-box">{{ r.codigos }}</div></td></tr>{% endfor %}
    {% if not data %}<tr><td colspan="9" class="muted">No hay registros todavía.</td></tr>{% endif %}</tbody></table></div>
    <div class="mobile-cards">{% for r in data %}<div class="record-card"><div class="field"><b>Fecha:</b> {{ r.fecha }}</div><div class="field"><b>Punto:</b> {{ r.punto }}</div><div class="field"><b>Cantidad:</b> {{ r.cantidad }}</div><div class="field"><b>Plan:</b> {{ r.plan }}</div><div class="field"><b>Total:</b> Q {{ '%.2f'|format(r.total) }}</div><div class="field"><b>Pago:</b> {% if r.estado == 'Cancelado' %}<span class="badge ok">Cancelado</span>{% else %}<span class="badge pending">Pendiente</span>{% endif %}</div><div class="field"><b>Fecha pago:</b> {{ r.fecha_pago or '' }}</div><div class="field"><b>Forma:</b> {{ r.forma_pago or '' }}</div><div class="field"><b>Códigos:</b><div class="code-box">{{ r.codigos }}</div></div><div class="row-actions"><a class="btn small dark" href="{{ url_for('editar', registro_id=r.id) }}">Editar</a><form method="post" action="{{ url_for('eliminar', registro_id=r.id) }}" onsubmit="return confirm('¿Eliminar este registro?');"><button class="btn small red" type="submit">Eliminar</button></form></div></div>{% endfor %}{% if not data %}<div class="record-card muted">No hay registros todavía.</div>{% endif %}</div></div>
    """
    return render_page("Registros", body, data=data)

@app.route("/puntos")
def puntos():
    if not logged(): return redirect(url_for("login"))
    body = '<div class="card"><h2>Puntos de venta y QR</h2><p class="muted">Cada punto puede abrir su enlace o escanear su código QR para ver sus datos.</p><div class="grid">{% for p in puntos %}<div class="card center" style="margin-bottom:0;"><h3>{{ p }}</h3><img class="qr-img" src="{{ url_for("qr_punto", punto=p) }}"><p class="small"><a class="btn outline" href="{{ url_for("vista_publica", punto=p) }}" target="_blank">Abrir enlace</a></p></div>{% endfor %}</div></div>'
    return render_page("Puntos", body, puntos=PUNTOS)

@app.route("/qr/<path:punto>")
def qr_punto(punto):
    url = request.host_url.rstrip("/") + url_for("vista_publica", punto=punto)
    img = qrcode.make(url); buf = BytesIO(); img.save(buf, format="PNG"); buf.seek(0)
    return send_file(buf, mimetype="image/png")

@app.route("/p/<path:punto>")
def vista_publica(punto):
    data = Registro.query.filter_by(punto=punto).order_by(Registro.id.desc()).all()
    total_tarjetas = db.session.query(db.func.coalesce(db.func.sum(Registro.cantidad), 0)).filter(Registro.punto==punto).scalar()
    pendiente = db.session.query(db.func.coalesce(db.func.sum(Registro.total), 0)).filter(Registro.punto==punto, Registro.estado=="Pendiente").scalar()
    body = """
    <div class="card"><h2>{{ punto }}</h2><p class="muted">Consulta del punto de venta</p><div class="stats"><div class="stat"><div class="muted">Registros</div><div class="n">{{ data|length }}</div></div><div class="stat"><div class="muted">Tarjetas</div><div class="n">{{ total_tarjetas }}</div></div><div class="stat"><div class="muted">Saldo pendiente</div><div class="n">Q {{ '%.2f'|format(pendiente or 0) }}</div></div></div></div>
    <div class="card"><h2>Historial</h2><div class="desktop-table table-wrap"><table><thead><tr><th>Fecha</th><th>Cantidad</th><th>Plan</th><th>Total</th><th>Pago</th><th>Fecha pago</th><th>Forma</th></tr></thead><tbody>
    {% for r in data %}<tr><td>{{ r.fecha }}</td><td>{{ r.cantidad }}</td><td>{{ r.plan }}</td><td>Q {{ '%.2f'|format(r.total) }}</td><td>{% if r.estado == 'Cancelado' %}<span class="badge ok">Cancelado</span>{% else %}<span class="badge pending">Pendiente</span>{% endif %}</td><td>{{ r.fecha_pago or '' }}</td><td>{{ r.forma_pago or '' }}</td></tr><tr><td colspan="7" class="muted"><b>Códigos:</b><br><div class="code-box">{{ r.codigos }}</div></td></tr>{% endfor %}
    {% if not data %}<tr><td colspan="7" class="muted">Sin registros todavía.</td></tr>{% endif %}</tbody></table></div>
    <div class="mobile-cards">{% for r in data %}<div class="record-card"><div class="field"><b>Fecha:</b> {{ r.fecha }}</div><div class="field"><b>Cantidad:</b> {{ r.cantidad }}</div><div class="field"><b>Plan:</b> {{ r.plan }}</div><div class="field"><b>Total:</b> Q {{ '%.2f'|format(r.total) }}</div><div class="field"><b>Pago:</b> {% if r.estado == 'Cancelado' %}<span class="badge ok">Cancelado</span>{% else %}<span class="badge pending">Pendiente</span>{% endif %}</div><div class="field"><b>Fecha pago:</b> {{ r.fecha_pago or '' }}</div><div class="field"><b>Forma:</b> {{ r.forma_pago or '' }}</div><div class="field"><b>Códigos:</b><div class="code-box">{{ r.codigos }}</div></div></div>{% endfor %}{% if not data %}<div class="record-card muted">Sin registros todavía.</div>{% endif %}</div></div>
    """
    return render_page(punto, body, punto=punto, data=data, total_tarjetas=total_tarjetas, pendiente=pendiente)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

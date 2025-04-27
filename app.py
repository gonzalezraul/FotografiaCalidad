from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os
import mysql.connector
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__, static_url_path='/static', static_folder='static')

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos MySQL
db_config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'ssl_ca': os.getenv('DB_CA_CERT'),
}

@app.route("/")
def home():
    return render_template("index.html")

# Ruta para suscribirse a la newsletter (guarda nombre y correo en la base de datos de Aiven)
@app.route('/newsletter', methods=['GET', 'POST'])
def newsletter():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')

        if not name or not email or '@' not in email:
            print("[DEBUG] Datos inválidos en newsletter")
            return render_template("newsletter.html", error="Por favor, ingresa un nombre y un email válido.")

        try:
            # Conexión a la base de datos
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            query = "INSERT INTO suscriptores (name, email) VALUES (%s, %s)"
            cursor.execute(query, (name, email))
            conn.commit()
            cursor.close()
            conn.close()
            print(f"[DEBUG] Suscriptor guardado en BD: {name}, {email}")
            return render_template("newsletter.html", success="¡Te has suscrito correctamente a la Newsletter!")
        except mysql.connector.Error as err:
            print(f"[ERROR] Error al insertar en BD: {err}")
            return render_template("newsletter.html", error="Error al procesar la suscripción.")
    return render_template("newsletter.html")

# Ruta para obtener todos los suscriptores (util para pruebas--puedes borrar si no requieres)
@app.route('/suscriptores', methods=['GET'])
def obtener_suscriptores():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM suscriptores")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'suscriptores': rows}), 200
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500

if __name__ == '__main__':
    app.run(debug=True)
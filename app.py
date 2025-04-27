from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os
import mysql.connector
from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInput
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
    'database': os.getenv('DB_NAME')
}

# Configuración de HubSpot
hubspot_api_key = os.getenv('HUBSPOT_API_KEY')
hubspot_client = HubSpot(access_token=hubspot_api_key)

# Configuración del correo
sender_email = os.getenv('SENDER_EMAIL')
sender_password = os.getenv('SENDER_PASSWORD')
smtp_host = os.getenv('SMTP_HOST', 'smtp-relay.sendinblue.com')  # Servidor SMTP de Brevo
smtp_port = int(os.getenv('SMTP_PORT', 587))  # Puerto SMTP para TLS (por defecto 587)

def crear_contacto_hubspot(nombre, email):
    contacto_input = SimplePublicObjectInput(
        properties={
            "firstname": nombre,
            "email": email
        }
    )
    try:
        print(f"[DEBUG] Intentando crear contacto en HubSpot con: {nombre}, {email}")
        respuesta = hubspot_client.crm.contacts.basic_api.create(
            simple_public_object_input=contacto_input,
            _request_timeout=10
        )
        print(f"[DEBUG] Respuesta de HubSpot: {respuesta}")
        return respuesta.id
    except Exception as e:
        print(f"[ERROR] Error al crear contacto en HubSpot: {e}")
        return None

@app.route("/")
def home():
    return render_template("index.html")

# Ruta para insertar datos (suscripción) y sincronizar con HubSpot
@app.route('/insert', methods=['POST'])
def insert_data():
    data = request.json
    name = data.get('name')
    email = data.get('email')

    if name and email:
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            query = "INSERT INTO suscriptores (name, email) VALUES (%s, %s)"
            cursor.execute(query, (name, email))
            conn.commit()
            cursor.close()
            conn.close()

            # Sincronizar el contacto en HubSpot
            hubspot_result = crear_contacto_hubspot(name, email)
            if hubspot_result:
                return jsonify({
                    'message': 'Datos insertados y sincronizados en HubSpot correctamente',
                    'hubspot_contact_id': hubspot_result
                }), 201
            else:
                return jsonify({'error': 'Error al sincronizar con HubSpot'}), 500
        except mysql.connector.Error as err:
            return jsonify({'error': str(err)}), 500
    else:
        return jsonify({'error': 'Faltan datos'}), 400

# Ruta para suscribirse a la newsletter (guarda nombre y correo)
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

            # Sincronizar con HubSpot
            hubspot_result = crear_contacto_hubspot(name, email)
            if not hubspot_result:
                print("[DEBUG] HubSpot no devolvió ID, falla en sincronización.")
                return render_template("newsletter.html", error="Suscripción guardada, pero falló la sincronización con HubSpot.")

            print(f"[DEBUG] Contacto creado en HubSpot con id: {hubspot_result}")
            return render_template("newsletter.html", success="¡Te has suscrito correctamente a la Newsletter!")
        except mysql.connector.Error as err:
            print(f"[ERROR] Error al insertar en BD: {err}")
            return render_template("newsletter.html", error="Error al procesar la suscripción.")
    return render_template("newsletter.html")

# Ruta para obtener todos los suscriptores
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
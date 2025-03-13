from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
CORS(app, resources={r"/receive": {"origins": "http://127.0.0.1:5000"}})

# Configuration de la connexion à MariaDB
db_config = {
    'host': 'localhost',
    'database': 'network_scanner',
    'user': 'toto',
    'password': 'toto'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MariaDB: {e}")
        return None

@app.route('/receive', methods=['POST', 'OPTIONS'])
def receive_data():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        print("Received data:", data)

        # Connexion à la base de données
        connection = get_db_connection()
        if not connection:
            return jsonify({
                'success': False,
                'error': 'Failed to connect to database'
            }), 500

        cursor = connection.cursor()

        # Vérifier le type de données reçues
        if 'hostname' in data and 'network_interfaces' in data:
            # Données de type system-info
            # Insérer dans system_info
            cursor.execute(
                "INSERT INTO system_info (hostname) VALUES (%s)",
                (data['hostname'],)
            )
            system_info_id = cursor.lastrowid

            # Insérer les interfaces réseau
            for interface in data['network_interfaces']:
                for address in interface['addresses']:
                    cursor.execute(
                        """
                        INSERT INTO network_interfaces (system_info_id, name, status, address_type, address, cidr, netmask)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            system_info_id,
                            interface['name'],
                            interface['status'],
                            address['type'],
                            address['address'],
                            address.get('cidr', None),
                            address.get('netmask', None)
                        )
                    )

        elif 'success' in data and 'devices' in data:
            # Données de type scan-results
            for device in data['devices']:
                # Insérer dans scan_results
                cursor.execute(
                    """
                    INSERT INTO scan_results (interface_name, ip, hostname, status)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        device['interface_name'],
                        device['ip'],
                        device['hostname'],
                        device['status']
                    )
                )
                scan_result_id = cursor.lastrowid

                # Insérer les ports ouverts
                for port in device['ports']:
                    cursor.execute(
                        """
                        INSERT INTO open_ports (scan_result_id, port, service)
                        VALUES (%s, %s, %s)
                        """,
                        (
                            scan_result_id,
                            port['port'],
                            port['service']
                        )
                    )

        # Valider les modifications
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({
            'success': True,
            'message': 'Data received and stored successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
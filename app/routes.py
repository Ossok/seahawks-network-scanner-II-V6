from flask import Blueprint, render_template, jsonify, request
import nmap
import socket
import platform
import os
import subprocess
import psutil
import ipaddress
import requests
import schedule
import json
from datetime import datetime

main = Blueprint('main', __name__)

# Chemin vers le fichier de configuration
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.json')

# Fonction pour charger la configuration
def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

# Fonction pour sauvegarder la configuration
def save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)

# Fonction pour obtenir les informations système (indépendante du contexte)
def get_system_info_data():
    hostname = socket.gethostname()
    
    network_interfaces = []
    for interface_name, interface_addresses in psutil.net_if_addrs().items():
        if interface_name.startswith(('vEthernet', 'VMware', 'docker', 'vboxnet')):
            continue
            
        interface_info = {
            'name': interface_name,
            'addresses': [],
            'status': 'down'
        }
        
        if interface_name in psutil.net_if_stats():
            stats = psutil.net_if_stats()[interface_name]
            interface_info['status'] = 'up' if stats.isup else 'down'
        
        for addr in interface_addresses:
            if addr.family == socket.AF_INET:
                try:
                    ip = addr.address
                    netmask = addr.netmask
                    if netmask:
                        prefix_length = ipaddress.IPv4Network(f'0.0.0.0/{netmask}', False).prefixlen
                        cidr = f"{ip}/{prefix_length}"
                    else:
                        cidr = f"{ip}/32"
                        
                    interface_info['addresses'].append({
                        'type': 'IPv4',
                        'address': ip,
                        'cidr': cidr,
                        'netmask': netmask
                    })
                except Exception as e:
                    interface_info['addresses'].append({
                        'type': 'IPv4',
                        'address': addr.address,
                        'cidr': f"{addr.address}/unknown",
                        'netmask': addr.netmask
                    })
            elif addr.family == socket.AF_INET6:
                interface_info['addresses'].append({
                    'type': 'IPv6',
                    'address': addr.address
                })
        
        if interface_info['addresses']:
            network_interfaces.append(interface_info)
    
    return {
        'hostname': hostname,
        'network_interfaces': network_interfaces
    }

# Fonction pour scanner le réseau (indépendante du contexte)
def scan_network_data():
    network_interfaces = []
    for interface_name, interface_addresses in psutil.net_if_addrs().items():
        if interface_name.startswith(('vEthernet', 'VMware', 'docker', 'vboxnet')):
            continue
        if interface_name in psutil.net_if_stats() and psutil.net_if_stats()[interface_name].isup:
            for addr in interface_addresses:
                if addr.family == socket.AF_INET:
                    interface_info = {
                        'name': interface_name,
                        'ip': addr.address
                    }
                    network_interfaces.append(interface_info)
    
    scanner = nmap.PortScanner()
    scan_results = []
    for interface in network_interfaces:
        local_ip = interface['ip']
        interface_name = interface['name']
        scanner.scan(local_ip, arguments='-sS -F')
        device_info = {
            'interface_name': interface_name,
            'ip': local_ip,
            'hostname': socket.gethostname(),
            'status': 'up',
            'ports': []
        }
        if local_ip in scanner.all_hosts():
            if 'tcp' in scanner[local_ip]:
                for port, port_info in scanner[local_ip]['tcp'].items():
                    if port_info['state'] == 'open':
                        device_info['ports'].append({
                            'port': port,
                            'service': port_info['name']
                        })
        scan_results.append(device_info)

    return {
        'success': True,
        'devices': scan_results,
        'app_version': '1.1.0'
    }

# Fonction pour envoyer les données (indépendante du contexte)
def send_data_to_server():
    try:
        config = load_config()
        target_url = config.get('target_url')
        
        if not target_url:
            print("Target URL not set. Skipping data sending.")
            return
        
        # Obtenir les données sans dépendre du contexte Flask
        system_info_data = get_system_info_data()
        scan_data = scan_network_data()
        
        # Envoyer les données
        headers = {'Content-Type': 'application/json'}
        response_system = requests.post(target_url, json=system_info_data, headers=headers, timeout=10)
        response_scan = requests.post(target_url, json=scan_data, headers=headers, timeout=10)
        
        if response_system.status_code == 200 and response_scan.status_code == 200:
            print(f"Data successfully sent to {target_url} at {datetime.now()}")
        else:
            print(f"Failed to send data to {target_url}. System Info Status: {response_system.status_code}, Scan Status: {response_scan.status_code}")
            
    except Exception as e:
        print(f"Error sending data: {str(e)}")

# Planifier l'envoi toutes les 10 minutes
schedule.every(10).minutes.do(send_data_to_server)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/api/system-info')
def get_system_info():
    return jsonify(get_system_info_data())

@main.route('/api/scan', methods=['POST'])
def scan_network():
    try:
        return jsonify(scan_network_data())
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/ping/<ip>')
def ping_server(ip):
    try:
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', ip]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        output = stdout.decode('cp850' if platform.system().lower() == 'windows' else 'utf-8')
        
        if process.returncode == 0:
            latency = None
            for line in output.split('\n'):
                if 'temps=' in line.lower():
                    try:
                        temps_str = line.split('temps=')[1].split('ms')[0].strip()
                        temps_str = temps_str.replace(',', '.')
                        latency = int(float(temps_str))
                        break
                    except:
                        continue
                elif 'time=' in line.lower():
                    try:
                        latency = float(line.split('time=')[1].split(' ms')[0].strip())
                        break
                    except:
                        continue

            return jsonify({
                'status': 'success',
                'message': 'Server reachable',
                'ip': ip,
                'latency': latency,
                'latency_unit': 'ms'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Server unreachable',
                'ip': ip
            }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@main.route('/api/send-to-machine', methods=['POST'])
def send_to_machine():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        target_url = data.get('target_url')
        data_type = data.get('data_type')

        if not target_url or not data_type:
            return jsonify({
                'success': False,
                'error': 'Missing target_url or data_type'
            }), 400

        if data_type == 'system-info':
            data_to_send = get_system_info_data()
        elif data_type == 'scan-results':
            data_to_send = scan_network_data()
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid data_type. Use "system-info" or "scan-results"'
            }), 400

        headers = {'Content-Type': 'application/json'}
        response = requests.post(target_url, json=data_to_send, headers=headers, timeout=10)

        if response.status_code == 200:
            return jsonify({
                'success': True,
                'message': f'Data ({data_type}) successfully sent to {target_url}'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to send data to {target_url}. Status code: {response.status_code}'
            }), 500

    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'Network error while sending data: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Internal error: {str(e)}'
        }), 500

@main.route('/api/set-target-url', methods=['POST'])
def set_target_url():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        target_url = data.get('target_url')
        if not target_url:
            return jsonify({
                'success': False,
                'error': 'Missing target_url'
            }), 400

        config = load_config()
        config['target_url'] = target_url
        save_config(config)

        return jsonify({
            'success': True,
            'message': f'Target URL set to {target_url}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error setting target URL: {str(e)}'
        }), 500

@main.route('/api/get-target-url', methods=['GET'])
def get_target_url():
    try:
        config = load_config()
        return jsonify({
            'success': True,
            'target_url': config.get('target_url', '')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error retrieving target URL: {str(e)}'
        }), 500

@main.route('/api/next-send-time', methods=['GET'])
def get_next_send_time():
    try:
        next_run = schedule.next_run()
        if next_run:
            time_remaining = int((next_run - datetime.now()).total_seconds())
            return jsonify({
                'success': True,
                'time_remaining': max(0, time_remaining)
            })
        return jsonify({
            'success': False,
            'error': 'No scheduled run found'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
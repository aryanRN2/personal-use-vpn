from flask import Flask, render_template, request, jsonify
from vpn_manager import VpnManager
import os

app = Flask(__name__)
vpn = VpnManager(config_dir=os.path.abspath(os.path.dirname(__file__)))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify(vpn.status())

@app.route('/api/generate-keys', methods=['POST'])
def generate_keys():
    keys = vpn.generate_keys()
    if "error" in keys:
        return jsonify(keys), 500
    return jsonify(keys)

@app.route('/api/save-config', methods=['POST'])
def save_config():
    data = request.json
    try:
        vpn.generate_config(
            private_key=data['private_key'],
            client_ip=data['client_ip'],
            server_pubkey=data['server_pubkey'],
            server_endpoint=data['server_endpoint'],
            allowed_ips=data.get('allowed_ips', '0.0.0.0/0, ::/0')
        )
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/connect', methods=['POST'])
def connect():
    data = request.json
    enable_kill_switch = data.get('kill_switch', False)
    server_endpoint = data.get('server_endpoint')

    res = vpn.connect()
    if res['status'] == 'success' and enable_kill_switch and server_endpoint:
        vpn.enable_kill_switch(server_endpoint)
        
    return jsonify(res)

@app.route('/api/disconnect', methods=['POST'])
def disconnect():
    res = vpn.disconnect()
    return jsonify(res)

if __name__ == '__main__':
    # Running on 0.0.0.0 locally for access, usually on 5000
    app.run(host='127.0.0.1', port=5000, debug=True)

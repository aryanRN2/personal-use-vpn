import subprocess
import os
import psutil

class VpnManager:
    def __init__(self, config_dir="./"):
        self.config_dir = config_dir
        self.config_path = os.path.join(self.config_dir, "wg0.conf")
        self.pf_rule_path = os.path.join(self.config_dir, "pf_vpn.conf")

    def generate_keys(self):
        try:
            privkey_proc = subprocess.run(['wg', 'genkey'], capture_output=True, text=True, check=True)
            privkey = privkey_proc.stdout.strip()
            
            pubkey_proc = subprocess.run(['wg', 'pubkey'], input=privkey, capture_output=True, text=True, check=True)
            pubkey = pubkey_proc.stdout.strip()
            
            return {"private_key": privkey, "public_key": pubkey}
        except subprocess.CalledProcessError as e:
            return {"error": str(e)}

    def generate_config(self, private_key, client_ip, server_pubkey, server_endpoint, allowed_ips="0.0.0.0/0, ::/0"):
        config_content = f"""[Interface]
PrivateKey = {private_key}
Address = {client_ip}
DNS = 1.1.1.1, 1.0.0.1

[Peer]
PublicKey = {server_pubkey}
AllowedIPs = {allowed_ips}
Endpoint = {server_endpoint}
PersistentKeepalive = 25
"""
        with open(self.config_path, 'w') as f:
            f.write(config_content)
        return True

    def connect(self):
        try:
            # Requires sudo. To use without password prompt, add wg-quick to sudoers.
            subprocess.run(['sudo', 'wg-quick', 'up', self.config_path], check=True)
            return {"status": "success"}
        except subprocess.CalledProcessError as e:
            return {"status": "error", "message": str(e)}

    def disconnect(self):
        try:
            subprocess.run(['sudo', 'wg-quick', 'down', self.config_path], check=True)
            self.disable_kill_switch()
            return {"status": "success"}
        except subprocess.CalledProcessError as e:
            return {"status": "error", "message": str(e)}

    def status(self):
        try:
            proc = subprocess.run(['sudo', 'wg', 'show', 'wg0'], capture_output=True, text=True)
            if proc.returncode == 0 and proc.stdout.strip():
                return {"connected": True, "details": proc.stdout}
            return {"connected": False}
        except Exception:
            return {"connected": False}

    def enable_kill_switch(self, server_endpoint):
        try:
            server_ip = server_endpoint.split(':')[0]
            server_port = server_endpoint.split(':')[1] if ':' in server_endpoint else "51820"
            
            pf_rules = f"""
block drop all
pass on utun+
pass on lo0
pass out inet proto udp from any to {server_ip} port {server_port}
"""
            with open(self.pf_rule_path, 'w') as f:
                f.write(pf_rules)
                
            subprocess.run(['sudo', 'pfctl', '-e'], check=False) 
            subprocess.run(['sudo', 'pfctl', '-f', self.pf_rule_path], check=True)
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def disable_kill_switch(self):
        try:
            # Flush all rules and disable pf
            subprocess.run(['sudo', 'pfctl', '-F', 'all'], check=True)
            subprocess.run(['sudo', 'pfctl', '-d'], check=False) 
            return {"status": "success"}
        except subprocess.CalledProcessError as e:
            return {"status": "error", "message": str(e)}

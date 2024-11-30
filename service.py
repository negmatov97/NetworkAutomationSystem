from flask import jsonify, Blueprint, send_file,  request, json
from gen_token import token_required
import os, datetime
import paramiko
import re
import pandas as pd
import time
import logging
import traceback

import Filters_Default



service = Blueprint('service', __name__)

username = os.environ.get('BACKUPUSER')
password = os.environ.get('BACKUPPASS')



###############################################


# Set up logging configuration
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


@service.route('/test_config', methods=['POST'])
@token_required
def configure_vlan_and_ports_tp(current_user):
    allowed_roles = ["S_admin", "D_admin", "RO_admin"]
    if current_user.roles not in allowed_roles:
        logging.debug("User does not have the required role.")
        return jsonify({"message": "Sizning Huqularingiz cheklangan"}), 401

    try:
        data = request.json
        ip = data['ip']  # Accessing the first element of 'ip'
        vlan_id = data['vlan_id']
        vlan_name = data['vlan_name']
        required_port = data['required_port']
        descriptions = data['descriptions']

        logging.debug(f"Received data: IP={ip}, VLAN ID={vlan_id}, VLAN Name={vlan_name}, "
                      f"Required Ports={required_port}, Descriptions={descriptions}")

        if len(descriptions) < required_port:
            logging.debug("Number of descriptions is less than the required ports.")
            return jsonify({"error": "Number of descriptions provided is less than the required ports"}), 400

        logging.debug("Connecting to SSH")
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(ip, username=username, password=password)
        logging.debug(f"Connected to {ip}.")

        ssh_session = ssh_client.invoke_shell()
        ssh_session.send(f"enable\r")
        ssh_session.send(f"terminal length 0\r")
        ssh_session.send("configure\r")
        ssh_session.send(f"show vlan\r")
        time.sleep(4)
        vlan_output = ssh_session.recv(65535).decode()
        logging.debug(f"VLAN Output: {vlan_output}")

        vlan_already_exists = False
        for line in vlan_output.split("\n"):
            if line.strip().startswith(str(vlan_id)):
                vlan_already_exists = True
                logging.debug(f"VLAN {vlan_id} already exists.")
                break

        if not vlan_already_exists:
            ssh_session.send(f"vlan {vlan_id}\r")
            ssh_session.send(f"name {vlan_name}\r")
            ssh_session.send("exit\r")
            time.sleep(1)
            logging.debug(f"Created VLAN {vlan_id} with name {vlan_name}.")

        # Run "show int eth status" command and filter results
        ssh_session.send(f"show interface status\r")
        time.sleep(1)
        status_output = ssh_session.recv(65535).decode()
        logging.debug(f"Interface status output: {status_output}")

        link_up_ports = Filters_Default.TP_Link.filter_interface_status_tp_link(status_output)

        if not link_up_ports:
            logging.debug("No suitable ports found in status check.")
            ssh_client.close()
            return jsonify({"error": "No suitable ports found in status check"}), 404

        selected_ports = link_up_ports[:required_port]
        for idx, port in enumerate(selected_ports):
            description = descriptions[idx]
            logging.debug(f"Configuring port {port['Port']} with description {description}")
            ssh_session.send(f"interface gigabitEthernet {port['Port']}\r")
            ssh_session.send(f"description {description}\r")
            ssh_session.send(f"switchport general allowed vlan {vlan_id} untagged\r")
            ssh_session.send(f"switchport pvid {vlan_id}\r")
            ssh_session.send(f"no shutdown\r")
            ssh_session.send("exit\r")

        ssh_session.send("copy running-config startup-config\r")
        ssh_session.send("y\r")
        ssh_client.close()
        logging.debug("Configuration saved and SSH connection closed.")

        return jsonify({
            "vlan_created": not vlan_already_exists,
            "configured_interface": [
                {
                    "interface": port["Port"],
                    "description": descriptions[idx]
                }
                for idx, port in enumerate(selected_ports)
            ],
            "vlan_id": vlan_id,
            "vlan_name": vlan_name
        })

    except Exception as e:
        logging.error(f"Error during VLAN configuration: {str(e)}")
        return jsonify({"error": str(e)}), 500


########################################################################################################################

def filter_configuration(config_text):
    """
    Switch konfiguratsiya ma'lumotlarini filtrlash va JSON formatga moslashtirish.
    VLAN ID va nomlari, interfeys ma'lumotlari (Pandas bilan), va boshqa bo'limlar.
    """
    vlan_section = []
    interfaces = []
    ntp_section = []
    logging_section = []

    # Har bir qatorni qayta ishlash
    lines = config_text.split("\n")
    current_interface = None
    current_interface_config = []

    for line in lines:
        line = line.strip()

        # VLAN konfiguratsiyasi
        if line.startswith("vlan"):
            vlan_data = {"id": None, "name": None}
            vlan_parts = line.split()
            if len(vlan_parts) > 1:
                vlan_data["id"] = vlan_parts[1]
            vlan_section.append(vlan_data)
        elif line.startswith("name") and vlan_section:
            vlan_section[-1]["name"] = line.split(" ", 1)[1]

        # Interfeys konfiguratsiyasi
        elif line.lower().startswith("interface"):
            # Oldingi interfeysni saqlash
            if current_interface and current_interface_config:
                interfaces.append({
                    "Interface": current_interface,
                    "Config": "\n".join(current_interface_config)
                })
            current_interface = line.split(" ", 1)[1]
            current_interface_config = [line]
        elif current_interface and line:
            current_interface_config.append(line)

        # NTP serverlari
        elif line.startswith("ntp server"):
            ntp_section.append(line)

        # Logging konfiguratsiyasi
        elif line.startswith("logging"):
            logging_section.append(line)

    # Oxirgi interfeysni qo‘shish
    if current_interface and current_interface_config:
        interfaces.append({
            "Interface": current_interface,
            "Config": "\n".join(current_interface_config)
        })

    # Interfeyslarni Pandas DataFrame ga o‘tkazish
    if interfaces:
        interfaces_df = pd.DataFrame(interfaces)
        interfaces_json = interfaces_df.to_dict(orient="records")
    else:
        interfaces_json = []

    # Filtrlash natijasini qaytarish
    return {
        "vlan_configuration": vlan_section,
        "interfaces": interfaces_json,
        "ntp_servers": ntp_section,
        "logging_configuration": logging_section,
    }


@service.route('/filter_config', methods=['POST'])
def filter_config():
    """
    Konfiguratsiyani filtrlash API.
    """
    data = request.json
    ip = data.get("ip")
    username = data.get("username")
    password = data.get("password")
    command = data.get("command")

    if not ip or not username or not password or not command:
        return jsonify({"error": "IP, username, password, va command talab qilinadi"}), 400

    try:
        # Paramiko orqali SSH ulanish
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(ip, username=username, password=password)

        # SSH orqali buyruqni bajarish
        stdin, stdout, stderr = ssh_client.exec_command(command)
        command_output = stdout.read().decode()
        ssh_client.close()

        # Filtrlash funksiyasini chaqirish
        filtered_data = filter_configuration(command_output)

        # Natijani qaytarish
        return jsonify(filtered_data)

    except paramiko.AuthenticationException:
        return jsonify({"error": "Authentication failed. Please check your credentials."}), 401
    except paramiko.SSHException as ssh_error:
        return jsonify({"error": f"SSH connection failed: {str(ssh_error)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
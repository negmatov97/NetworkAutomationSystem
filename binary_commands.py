import os
from flask import json, jsonify
from gen_token import token_required
import paramiko
import time
import Filters_Default
import logging



username = os.environ.get('BACKUPUSER')
password = os.environ.get('BACKUPPASS')

class NagDevice:
    @staticmethod
    @token_required

    def show_version(current_user, ip):

        allowed_roles = ["S_admin", "D_admin", "RO_admin"]
        if not current_user.roles in allowed_roles:
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

        try:
            # Create a Paramiko SSH client and connect
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=username, password=password)

            ssh_session = ssh_client.invoke_shell()
            ssh_session.send(f"enable\r")
            ssh_session.send(f"terminal length 0\r")
            ssh_session.send(f"show version\r")
            time.sleep(1)
            output = ssh_session.recv(65535).decode()

            # Close the SSH connection
            ssh_client.close()
            formatted_output = output.strip('\r\n')
            checked_output = formatted_output.replace('\r\n', ' ')

            response = {
                'ip': ip,
                'version_info': checked_output
            }

            return jsonify(response)

        except Exception as e:
            return jsonify({"error": str(e)})



    @token_required
    def create_vlan(current_user, ip, vlan_id, vlan_name):

        allowed_roles = ["S_admin", "D_admin", "RO_admin"]
        if not current_user.roles in allowed_roles:
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

        try:
            # Create a Paramiko SSH client and connect
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=username, password=password)

            ssh_session = ssh_client.invoke_shell()
            ssh_session.send(f"enable\r")
            time.sleep(1)
            ssh_session.send(f"terminal length 0\r")
            time.sleep(1)
            ssh_session.send(f"show vlan id {vlan_id}\r")
            time.sleep(2)
            vlan_output = ssh_session.recv(65535).decode()

            vlan_arleady_exits = False
            for  line in vlan_output.split('\n'):
                if line.strip().startswith(str(vlan_id)):
                    vlan_arleady_exits = True
                    break

            if vlan_arleady_exits:
                logging.warning(f"{vlan_id} vlan mavjud")
                ssh_client.close()
                return jsonify({"error": f"ID: {vlan_id} vlan mavjud"})


            if not vlan_arleady_exits:
                ssh_session.send(f"conf t\r")
                ssh_session.send(f"vlan {vlan_id}\r")
                ssh_session.send(f"name {vlan_name}\r")
                ssh_session.send(f"exit\r")

            ssh_session.send(f"end\r")
            ssh_session.send(f"copy running-config startup-config\r")
            time.sleep(1)
            ssh_session.send(f"y\r")
            time.sleep(1)
            ssh_session.send(f"exit\r")
            # output = ssh_session.recv(65535).decode()
            # Close the SSH connection
            ssh_client.close()
            # formated_json = json.dumps(output, indent=2)
            # return formated_json

            return jsonify({
                "configuration_report": [{
                    "vlan_id": vlan_id,
                    "vlan_name": vlan_name,
                    "success": True
                }]
            })
        except paramiko.AuthenticationException:
            return jsonify({"error": "Authentication failed. Please check your credentials."})
        except Exception as e:
            return jsonify({"error": "Unexpected error occurred: " + str(e)})


    @token_required
    def delete_vlan(current_user, ip, vlan_id):

        allowed_roles = ["S_admin", "D_admin", "RO_admin"]
        if not current_user.roles in allowed_roles:
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'})

        try:
            # Create a Paramiko SSH client and connect
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=username, password=password)

            ssh_session = ssh_client.invoke_shell()
            ssh_session.send(f"enable\r")
            ssh_session.send(f"terminal length 0\r")
            ssh_session.send(f"show vlan id {vlan_id}\r")
            vlan_output = ssh_session.recv(65535).decode()

            vlan_exists = False
            for line in vlan_output.split('\n'):
                if line.strip().startswith(str(vlan_id)):
                    vlan_exists = True
                    break

            if not vlan_exists:
                logging.warning(f"{ip} qurilmada ID: {vlan_id} vlan mavjud emas")
                return jsonify({"error": f"{ip} qurilmada ID: {vlan_id} vlan mavjud emas"})


            ssh_session.send(f"conf t\r")
            ssh_session.send(f"no interface vlan {vlan_id}\r")
            ssh_session.send(f"no vlan {vlan_id}\r")
            ssh_session.send(f"end\r")
            ssh_session.send(f"copy running-config startup-config\r")
            time.sleep(1)
            ssh_session.send(f"y\r")
            time.sleep(1)
            ssh_session.send(f"exit\r")


            # Close the SSH connection
            ssh_client.close()

            return jsonify({
                "configuration_report": [{
                    "vlan_id": vlan_id,
                    "success": True
                }]
            })

        except paramiko.AuthenticationException:
            return jsonify({"error": "Authentication failed. Please check your credentials."})
        except Exception as e:
            return jsonify({"error": "Unexpected error occurred: " + str(e)})


    @token_required
    def logging_server(current_user, ip, log_server, log_level_num):

        allowed_roles = ["S_admin", "D_admin", "RO_admin"]
        if current_user.roles not in allowed_roles:
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'})

        # Mapping log_level_num to corresponding log_level strings
        log_level_map = {
            2: "critical",
            4: "warnings",
            6: "informational",
            7: "debugging"
        }

        log_level = log_level_map.get(log_level_num)
        if log_level is None:
            return jsonify({'message': "Noto‘g‘ri log darajasi"})

        try:
            # Create a Paramiko SSH client and connect
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=username, password=password)

            ssh_session = ssh_client.invoke_shell()
            ssh_session.send(f"enable\r")
            ssh_session.send(f"conf t\r")
            ssh_session.send(f"logging {log_server} facility local7 level {log_level}\r")
            ssh_session.send(f"logging flash level informational\r")
            ssh_session.send(f"logging executed-commands enable\r")
            ssh_session.send(f"logging loghost sequence-number\r")
            ssh_session.send(f"end\r")
            ssh_session.send(f"copy running-config startup-config\r")
            time.sleep(1)
            ssh_session.send(f"y\r")
            time.sleep(1)
            ssh_session.send(f"exit\r")
            # output = ssh_session.recv(65535).decode()

            # Close the SSH connection
            ssh_client.close()
            # formated_json = json.dumps(output, indent=2)
            # return formated_json

            return jsonify({
                "configuration_report": [{
                    "log_server": log_server,
                    "success": True
                }]
            })

        except paramiko.AuthenticationException:
            return jsonify({"error": "Authentication failed. Please check your credentials."})
        except Exception as e:
            return jsonify({"error": "Unexpected error occurred: " + str(e)})


    @token_required
    def nacs_server(current_user, ip, nacs_server, nacs_key):

        allowed_roles = ["S_admin", "D_admin", "RO_admin"]
        if not current_user.roles in allowed_roles:
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'})

        # username = user
        # password = passw

        try:
            # Create a Paramiko SSH client and connect
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=username, password=password)

            ssh_session = ssh_client.invoke_shell()
            ssh_session.send(f"enable\r")
            ssh_session.send(f"conf t\r")
            ssh_session.send(f"banner motd Tarmoq qurulmasiga ruxsatsiz kirish qonunga muvofiq ta'qib qilinadi\r")
            ssh_session.send(f"banner login Tarmoq qurulmasiga ruxsatsiz kirish qonunga muvofiq ta'qib qilinadi\r")
            ssh_session.send(f"tacacs-server authentication host {nacs_server} key 0 {nacs_key}\r")
            ssh_session.send(f"authentication line console login tacacs local\r")
            ssh_session.send(f"authentication line vty login tacacs local\r")
            ssh_session.send(f"authentication line web login tacacs local\r")
            ssh_session.send(f"authorization line console exec tacacs local\r")
            ssh_session.send(f"authorization line vty exec tacacs local\r")
            ssh_session.send(f"authorization line web exec tacacs local\r")
            ssh_session.send(f"aaa authorization config-commands\r")
            ssh_session.send(f"authorization line vty command 15 tacacs local\r")
            ssh_session.send(f"accounting line console exec start-stop tacacs\r")
            ssh_session.send(f"accounting line vty exec start-stop tacacs\r")
            ssh_session.send(f"accounting line console command 15 start-stop tacacs\r")
            ssh_session.send(f"accounting line vty command 15 start-stop tacacs\r")
            ssh_session.send(f"end\r")
            ssh_session.send(f"copy running-config startup-config\r")
            time.sleep(1)
            ssh_session.send(f"y\r")
            time.sleep(1)
            ssh_session.send(f"exit\r")
            # output = ssh_session.recv(65535).decode()

            # Close the SSH connection
            ssh_client.close()
            # formated_json = json.dumps(output, indent=2)
            # return formated_json

            return jsonify({
                "configuration_report": [{
                    "nacs_server": nacs_server,
                    "success": True
                }]
            })

        except paramiko.AuthenticationException:
            return jsonify({"error": "Authentication failed. Please check your credentials."})
        except Exception as e:
            return jsonify({"error": "Unexpected error occurred: " + str(e)})


    @token_required
    def auth_default(current_user, ip):

        allowed_roles = ["S_admin", "D_admin", "RO_admin"]
        if not current_user.roles in allowed_roles:
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'})

        # username = user
        # password = passw

        try:
            # Create a Paramiko SSH client and connect
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=username, password=password)

            ssh_session = ssh_client.invoke_shell()
            ssh_session.send(f"enable\r")
            ssh_session.send(f"conf t\r")
            ssh_session.send(f"authentication logging enable\r")
            ssh_session.send(f"banner motd Tarmoq qurulmasiga ruxsatsiz kirish qonunga muvofiq ta'qib qilinadi\r")
            ssh_session.send(f"banner login Tarmoq qurulmasiga ruxsatsiz kirish qonunga muvofiq ta'qib qilinadi\r")
            ssh_session.send(f"authentication line console login local\r")
            ssh_session.send(f"authentication line vty login local\r")
            ssh_session.send(f"authentication line web login local\r")
            ssh_session.send(f"authorization line console exec local\r")
            ssh_session.send(f"authorization line vty exec local\r")
            ssh_session.send(f"authorization line web exec local\r")
            ssh_session.send(f"end\r")
            ssh_session.send(f"copy running-config startup-config\r")
            time.sleep(1)
            ssh_session.send(f"y\r")
            time.sleep(1)
            ssh_session.send(f"exit\r")
            # output = ssh_session.recv(65535).decode()

            # Close the SSH connection
            ssh_client.close()
            # formated_json = json.dumps(output, indent=2)
            # return formated_json

            return jsonify({
                "configuration_report": [{
                    "success": True
                }]
            })

        except paramiko.AuthenticationException:
            return jsonify({"error": "Authentication failed. Please check your credentials."})
        except Exception as e:
            return jsonify({"error": "Unexpected error occurred: " + str(e)})


    @token_required
    def add_user(current_user, ip, new_username, new_password, privilage):


        allowed_roles = ["S_admin", "D_admin", "RO_admin"]
        if not current_user.roles in allowed_roles:
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'})


        try:
            # Create a Paramiko SSH client and connect
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=username, password=password)

            ssh_session = ssh_client.invoke_shell()
            ssh_session.send(f"enable\r")
            ssh_session.send(f"conf t\r")
            ssh_session.send(f"username {new_username} privilage {privilage} password {new_password}\r")
            ssh_session.send(f"end\r")
            ssh_session.send(f"copy running-config startup-config\r")
            time.sleep(1)
            ssh_session.send(f"y\r")
            time.sleep(1)
            ssh_session.send(f"exit\r")
            # output = ssh_session.recv(65535).decode()

            # Close the SSH connection
            ssh_client.close()
            # formated_json = json.dumps(output, indent=2)
            # return formated_json

            return jsonify({
                "configuration_report": [{
                    "new_username": new_username,
                    "privilage": privilage,
                    "success": True
                }]
            })

        except paramiko.AuthenticationException:
            return jsonify({"error": "Authentication failed. Please check your credentials."})
        except Exception as e:
            return jsonify({"error": "Unexpected error occurred: " + str(e)})

    @token_required
    def delete_user(current_user, ip, new_username):

        allowed_roles = ["S_admin", "D_admin", "RO_admin"]
        if not current_user.roles in allowed_roles:
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'})

        try:
            # Create a Paramiko SSH client and connect
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=username, password=password)

            ssh_session = ssh_client.invoke_shell()
            ssh_session.send(f"enable\r")
            ssh_session.send(f"conf t\r")
            ssh_session.send(f"no username {new_username} \r")
            ssh_session.send(f"end\r")
            ssh_session.send(f"copy running-config startup-config\r")
            time.sleep(1)
            ssh_session.send(f"y\r")
            time.sleep(1)
            ssh_session.send(f"exit\r")
            # output = ssh_session.recv(65535).decode()

            # Close the SSH connection
            ssh_client.close()
            # formated_json = json.dumps(output, indent=2)
            # return formated_json

            return jsonify({
                "configuration_report": [{
                    "new_username": new_username,
                    "success": True
                }]
            })

        except paramiko.AuthenticationException:
            return jsonify({"error": "Authentication failed. Please check your credentials."})
        except Exception as e:
            return jsonify({"error": "Unexpected error occurred: " + str(e)})


    @token_required
    def snmp_config(current_user, ip, snmp_host ,snpm_key):

        allowed_roles = ["S_admin", "D_admin", "RO_admin"]
        if not current_user.roles in allowed_roles:
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'})

        try:
            # Create a Paramiko SSH client and connect
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=username, password=password)

            ssh_session = ssh_client.invoke_shell()
            ssh_session.send(f"enable\r")
            ssh_session.send(f"conf t\r")
            ssh_session.send(f"snmp-server enable\r")
            ssh_session.send(f"snmp-server timeout 300\r")
            ssh_session.send(f"snmp-server securityip disable\r")
            ssh_session.send(f"snmp-server host {snmp_host} v2c {snpm_key}\r")
            ssh_session.send(f"snmp-server community ro 7 {snpm_key}\r")
            ssh_session.send(f"snmp-server enable traps\r")
            ssh_session.send(f"snmp-server enable traps mac-notification\r")
            ssh_session.send(f"snmp-server enable traps if-ber max-warning-value 50\r")
            ssh_session.send(f"snmp-server enable traps if-packet-lost-rate max-warning-value 50\r")
            ssh_session.send(f"snmp-server enable traps cpu-used-per max-warning-value 44\r")
            ssh_session.send(f"snmp-server enable traps mem-used-per max-warning-value 50\r")
            ssh_session.send(f"snmp-server enable traps element-state-to-down\r")
            ssh_session.send(f"snmp-server ddm-mib disable\r")
            ssh_session.send(f"snmp-server ddm-electronic-hidden disable\r")
            ssh_session.send(f"end\r")
            ssh_session.send(f"copy running-config startup-config\r")
            time.sleep(1)
            ssh_session.send(f"y\r")
            time.sleep(1)
            ssh_session.send(f"exit\r")
            # output = ssh_session.recv(65535).decode()

            # Close the SSH connection
            ssh_client.close()
            # formated_json = json.dumps(output, indent=2)
            # return formated_json

            return jsonify({
                "configuration_report": [{
                    "snmp_host": snmp_host,
                    "success": True
                }]
            })

        except paramiko.AuthenticationException:
            return jsonify({"error": "Authentication failed. Please check your credentials."})
        except Exception as e:
            return jsonify({"error": "Unexpected error occurred: " + str(e)})

    @token_required
    def ntp_config(current_user, ip, ntp_server_primary, ntp_server_secondary):

        allowed_roles = ["S_admin", "D_admin", "RO_admin"]
        if not current_user.roles in allowed_roles:
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'})

        try:
            # Create a Paramiko SSH client and connect
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=username, password=password)

            ssh_session = ssh_client.invoke_shell()
            ssh_session.send(f"enable\r")
            ssh_session.send(f"conf t\r")
            ssh_session.send(f"ntp enable\r")
            ssh_session.send(f"ntp server {ntp_server_primary}\r")
            ssh_session.send(f"ntp server {ntp_server_secondary}\r")
            ssh_session.send(f"end\r")
            ssh_session.send(f"copy running-config startup-config\r")
            time.sleep(1)
            ssh_session.send(f"y\r")
            time.sleep(1)
            ssh_session.send(f"exit\r")
            # output = ssh_session.recv(65535).decode()

            # Close the SSH connection
            ssh_client.close()
            # formated_json = json.dumps(output, indent=2)
            # return formated_json

            return jsonify({
                "configuration_report": [{
                    "ntp_server_primary": ntp_server_primary,
                    "ntp_server_secondary": ntp_server_secondary,
                    "success": True
                }]
            })

        except paramiko.AuthenticationException:
            return jsonify({"error": "Authentication failed. Please check your credentials."})
        except Exception as e:
            return jsonify({"error": "Unexpected error occurred: " + str(e)})

    @token_required
    def configure_vlan_and_ports(current_user, ip, vlan_id, vlan_name, required_port, descriptions):
        try:
            # Validate that descriptions match the required_port count
            if len(descriptions) < required_port:
                return jsonify({"error": "Number of descriptions provided is less than the required ports"})

            # Create a Paramiko SSH client and connect
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=username, password=password)

            # Run "show vlan" command to check if VLAN already exists
            ssh_session = ssh_client.invoke_shell()
            ssh_session.send("terminal length 0\r")
            time.sleep(1)
            ssh_session.send("show vlan\r")
            time.sleep(2)  # Allow time for the output
            vlan_output = ssh_session.recv(65535).decode()

            # Check VLAN existence directly in the output
            vlan_already_exists = False
            for line in vlan_output.split("\n"):
                if line.strip().startswith(str(vlan_id)):
                    vlan_already_exists = True
                    break

            # If VLAN does not exist, create it
            if not vlan_already_exists:
                ssh_session.send(f"conf t\r")
                ssh_session.send(f"vlan {vlan_id}\r")
                ssh_session.send(f"name {vlan_name}\r")
                ssh_session.send(f"exit\r")
                ssh_session.send(f"end\r")
                ssh_session.send(f"copy running-config startup-config\r")
                time.sleep(1)
                ssh_session.send(f"y\r")
                time.sleep(1)

            # Run "show int eth status" command and filter results
            ssh_session.send("show int eth status\r")
            time.sleep(2)
            int_status_output = ssh_session.recv(65535).decode()
            filtered_interfaces = Filters_Default.Nag_filter.filter_interface_status(int_status_output)

            if not filtered_interfaces:
                ssh_client.close()
                return jsonify({"error": "No matching interfaces found"})

            # Select the required number of ports
            selected_interfaces = filtered_interfaces[:required_port]

            # Configure each selected interface with description and VLAN
            ssh_session.send(f"conf t\r")
            for idx, interface in enumerate(selected_interfaces):
                description = descriptions[idx]  # Use the provided description for the interface
                ssh_session.send(f"interface ethernet {interface['Interface']}\r")
                ssh_session.send(f"description {description}\r")
                ssh_session.send(f"switchport access vlan {vlan_id}\r")
                ssh_session.send(f"no shutdown\r")
                ssh_session.send(f"exit\r")
            ssh_session.send(f"end\r")
            ssh_session.send(f"copy running-config startup-config\r")
            time.sleep(1)
            ssh_session.send(f"y\r")
            time.sleep(1)
            ssh_session.send(f"exit\r")
            config_output = ssh_session.recv(65535).decode()

            # Close the SSH connection
            ssh_client.close()

            return jsonify({
                "configuration_report": [{
                    "vlan_configurations": [
                        {
                        "vlan_id": vlan_id,
                        "vlan_name": vlan_name
                    }
                    ],
                    "configured_interfaces": [
                        {
                            "interface": iface["Interface"],
                            "description": descriptions[idx]
                        }
                        for idx, iface in enumerate(selected_interfaces)
                    ],
                    "success": True
                }]
            })

        except paramiko.AuthenticationException:
            return jsonify({"error": "Authentication failed. Please check your credentials."})
        except Exception as e:
            return jsonify({"error": "Unexpected error occurred: " + str(e)})



"""
        TP-link qurilmalari uchun sozlamalar Class
    """
class TplinkDevice:
    @staticmethod
    @token_required
    def show_system_info(current_user, ip, vlan_id, vlan_name):

        allowed_roles = ["S_admin", "D_admin", "RO_admin"]
        if not current_user.roles in allowed_roles:
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'})

        # username = user
        # password = passw

        try:
            # Create a Paramiko SSH client and connect
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=username, password=password)

            ssh_session = ssh_client.invoke_shell()
            ssh_session.send(f"enable\r")
            ssh_session.send(f"terminal length 0\r")
            ssh_session.send(f"show system-info\r")
            time.sleep(1)
            output = ssh_session.recv(65535).decode()

            # Close the SSH connection
            ssh_client.close()
            formated_json = json.dumps(output, indent=2)
            return formated_json
        except Exception as e:
            return "Error: " + str(e)


    @token_required
    def create_vlan(current_user, ip, vlan_id, vlan_name):

        allowed_roles = ["S_admin", "D_admin", "RO_admin"]
        if not current_user.roles in allowed_roles:
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'})

        try:
            logging.debug(f"Connecting SSH")
            # Create a Paramiko SSH client and connect
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=username, password=password)

            ssh_session = ssh_client.invoke_shell()
            ssh_session.send(f"enable\r")
            time.sleep(1)
            ssh_session.send(f"terminal length 0\r")
            time.sleep(1)
            ssh_session.send(f"configure\r")
            time.sleep(1)
            ssh_session.send(f"show vlan id {vlan_id}\r")
            time.sleep(1)
            vlan_output = ssh_session.recv(65535).decode()

            vlan_arleady_exits = False
            for line in vlan_output.split("\n"):
                if line.strip().startswith(str(vlan_id)):
                    vlan_arleady_exits = True
                    break

            if vlan_arleady_exits:
                logging.warning(f"{ip} qurilmada ID: {vlan_id} vlan mavjud"),
                return jsonify({"error": f" {ip} qurilmada ID: {vlan_id} vlan mavjud"})

            if not vlan_arleady_exits:
                ssh_session.send(f"vlan {vlan_id}\r")
                ssh_session.send(f"name {vlan_name}\r")
                ssh_session.send(f"exit\r")

            ssh_session.send(f"end\r")
            ssh_session.send(f"copy running-config startup-config\r")
            time.sleep(1)
            ssh_session.send(f"y\r")
            time.sleep(1)
            ssh_client.close()
            # formated_json = json.dumps(output, indent=2)
            # return formated_json

            return jsonify({
                "configuration_report": [{
                    "vlan_id": vlan_id,
                    "vlan_name": vlan_name,
                    "success": True
                }]
            })

        except paramiko.AuthenticationException:
            return jsonify({"error": "Authentication failed. Please check your credentials."})
        except Exception as e:
            return jsonify({"error": "Unexpected error occurred: " + str(e)})


    @token_required
    def delete_vlan(current_user, ip, vlan_id):

        allowed_roles = ["S_admin", "D_admin", "RO_admin"]
        if not current_user.roles in allowed_roles:
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'})

        try:
            # Create a Paramiko SSH client and connect
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=username, password=password)

            ssh_session = ssh_client.invoke_shell()
            ssh_session.send(f"enable\r")
            ssh_session.send(f"terminal length 0\r")
            ssh_session.send(f"configure\r")
            ssh_session.send(f"show vlan id {vlan_id}\r")
            vlan_output = ssh_session.recv(65535).decode()

            vlan_exists = False
            for line in vlan_output.split('\n'):
                if line.strip().startswith(str(vlan_id)):
                    vlan_exists = True
                    break

            if not vlan_exists:
                logging.warning(f"{ip} qurilmada ID: {vlan_id} vlan mavjud emas"),
                return jsonify({"error": f" {ip} qurilmada ID: {vlan_id} vlan mavjud emas"})

            ssh_session.send(f"no vlan {vlan_id}\r")
            ssh_session.send(f"exit\r")
            ssh_session.send(f"end\r")
            ssh_session.send(f"copy running-config startup-config\r")
            time.sleep(1)
            ssh_session.send(f"y\r")
            time.sleep(1)
            ssh_session.send(f"exit\r")
            # output = ssh_session.recv(65535).decode()

            # Close the SSH connection
            ssh_client.close()
            # formated_json = json.dumps(output, indent=2)
            # return formated_json

            return jsonify({
                "configuration_report": [{
                    "vlan_id": vlan_id,
                    "success": True
                }]
            })
        except paramiko.AuthenticationException:
            return jsonify({"error": "Authentication failed. Please check your credentials."})
        except Exception as e:
            return jsonify({"error": "Unexpected error occurred: " + str(e)})

    @token_required
    def logging_server(current_user, ip, log_server, log_level_num):

        allowed_roles = ["S_admin", "D_admin", "RO_admin"]
        if current_user.roles not in allowed_roles:
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'})


        try:
            # Create a Paramiko SSH client and connect
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=username, password=password)

            ssh_session = ssh_client.invoke_shell()
            ssh_session.send(f"enable\r")
            ssh_session.send(f"configure\r")
            ssh_session.send(f"logging host index 1 {log_server} {log_level_num}\r")
            ssh_session.send(f"logging console level 7\r")
            ssh_session.send(f"logging buffer level 5\r")
            ssh_session.send(f"logging file flash level 5\r")
            ssh_session.send(f"logging console\r")
            ssh_session.send(f"logging buffer\r")
            ssh_session.send(f"command log\r")
            ssh_session.send(f"end\r")
            ssh_session.send(f"copy running-config startup-config\r")
            time.sleep(1)
            ssh_session.send(f"y\r")
            time.sleep(1)
            ssh_session.send(f"exit\r")
            # output = ssh_session.recv(65535).decode()

            # Close the SSH connection
            ssh_client.close()
            # formated_json = json.dumps(output, indent=2)
            # return formated_json
            return jsonify({
                "configuration_report": [{
                    "log_server": log_server,
                    "massage": True
                }]
            })

        except paramiko.AuthenticationException:
            return jsonify({"error": "Authentication failed. Please check your credentials."})
        except Exception as e:
            return jsonify({"error": "Unexpected error occurred: " + str(e)})

    @token_required
    def nacs_server(current_user, ip, nacs_server, nacs_key):

        allowed_roles = ["S_admin", "D_admin", "RO_admin"]
        if current_user.roles not in allowed_roles:
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'})


        try:
            # Create a Paramiko SSH client and connect
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=username, password=password)

            ssh_session = ssh_client.invoke_shell()
            ssh_session.send(f"enable\r")
            ssh_session.send(f"configure\r")
            ssh_session.send(f"tacacs-server host {nacs_server} port 49 timeout 5 key 0 {nacs_key}\r")
            ssh_session.send(f"aaa authentication login default tacacs local\r")
            ssh_session.send(f"aaa authentication enable default tacacs local\r")
            ssh_session.send(f"aaa authentication login console tacacs local\r")
            ssh_session.send(f"aaa authentication login vty tacacs local\r")
            ssh_session.send(f"end\r")
            ssh_session.send(f"copy running-config startup-config\r")
            time.sleep(1)
            ssh_session.send(f"exit\r")
            # output = ssh_session.recv(65535).decode()

            # Close the SSH connection
            ssh_client.close()
            # formated_json = json.dumps(output, indent=2)
            # return formated_json
            return jsonify({
                "configuration_report": [{
                    "nacs_server": nacs_server,
                    "success": True
                }]
            })
        except paramiko.AuthenticationException:
            return jsonify({"error": "Authentication failed. Please check your credentials."})
        except Exception as e:
            return jsonify({"error": "Unexpected error occurred: " + str(e)})

    @token_required
    def auth_default(current_user, ip):

        allowed_roles = ["S_admin", "D_admin", "RO_admin"]
        if current_user.roles not in allowed_roles:
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'})

        try:
            # Create a Paramiko SSH client and connect
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=username, password=password)

            ssh_session = ssh_client.invoke_shell()
            ssh_session.send(f"enable\r")
            ssh_session.send(f"configure\r")
            ssh_session.send(f"aaa authentication login default local\r")
            ssh_session.send(f"aaa authentication enable default local\r")
            ssh_session.send(f"aaa authentication login console local\r")
            ssh_session.send(f"aaa authentication login vty local\r")
            ssh_session.send(f"end\r")
            ssh_session.send(f"copy running-config startup-config\r")
            time.sleep(1)
            ssh_session.send(f"exit\r")
            output = ssh_session.recv(65535).decode()

            # Close the SSH connection
            ssh_client.close()
            # formated_json = json.dumps(output, indent=2)
            # return formated_json
            return jsonify({
                "configuration_report": [{
                    "success": True,
                }]
            })

        except paramiko.AuthenticationException:
            return jsonify({"error": "Authentication failed. Please check your credentials."})
        except Exception as e:
            return jsonify({"error": "Unexpected error occurred: " + str(e)})

    @token_required
    def snmp_config(current_user, ip, snmp_host ,snpm_key):

        allowed_roles = ["S_admin", "D_admin", "RO_admin"]
        if not current_user.roles in allowed_roles:
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'})

        try:
            # Create a Paramiko SSH client and connect
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=username, password=password)

            ssh_session = ssh_client.invoke_shell()
            ssh_session.send(f"enable\r")
            ssh_session.send(f"configure\r")
            ssh_session.send(f"snmp-server community {snpm_key} read-only viewDefault\r")
            ssh_session.send(f"snmp-server host {snmp_host} 162 {snpm_key} smode v2c slev noAuthNoPriv type trap\r")
            ssh_session.send(f"snmp-server traps security ip-mac-binding\r")
            ssh_session.send(f"snmp-server traps security dhcp-filter\r")
            ssh_session.send(f"snmp-server traps lldp rematableschange\r")
            ssh_session.send(f"snmp-server traps lldp topologychange\r")
            ssh_session.send(f"snmp-server traps flash\r")
            ssh_session.send(f"snmp-server traps spanning-tree topologychange\r")
            ssh_session.send(f"snmp-server traps cpu\r")
            ssh_session.send(f"snmp-server traps memory\r")
            ssh_session.send(f"snmp-server traps vlan create\r")
            ssh_session.send(f"snmp-server traps vlan delete\r")
            ssh_session.send(f"snmp-server traps storm-control\r")
            ssh_session.send(f"snmp-server traps rate-limit\r")
            ssh_session.send(f"snmp-server traps acl\r")
            ssh_session.send(f"snmp-server traps loopback-detection\r")
            ssh_session.send(f"snmp-server traps temperature\r")
            ssh_session.send(f"snmp-server traps voltage\r")
            ssh_session.send(f"snmp-server traps bias_current\r")
            ssh_session.send(f"snmp-server traps tx_power\r")
            ssh_session.send(f"snmp-server traps rx_power\r")
            ssh_session.send(f"snmp-server traps ip change\r")
            ssh_session.send(f"snmp-server traps ip duplicate\r")
            ssh_session.send(f"end\r")
            ssh_session.send(f"copy running-config startup-config\r")
            time.sleep(1)
            ssh_session.send(f"y\r")
            time.sleep(1)
            ssh_session.send(f"exit\r")
            # output = ssh_session.recv(65535).decode()

            # Close the SSH connection
            ssh_client.close()
            # formated_json = json.dumps(output, indent=2)
            # return formated_json
            return jsonify({
                "configuration_report": [{
                    "snmp_host": snmp_host,
                    "snmp_key": snpm_key
                }]
            })
        except paramiko.AuthenticationException:
            return jsonify({"error": "Authentication failed. Please check your credentials."})
        except Exception as e:
            return jsonify({"error": "Unexpected error occurred: " + str(e)})

    @token_required
    def add_user(current_user, ip, new_username, new_password, privilage):

        allowed_roles = ["S_admin", "D_admin", "RO_admin"]
        if not current_user.roles in allowed_roles:
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'})

        priv_level_map = {
            15: "admin",
            7: "user",
        }

        priv_level = priv_level_map.get(privilage)
        if priv_level is None:
            return jsonify({'message': "Noto‘g‘ri huquq darajasi"})

        try:
            # Create a Paramiko SSH client and connect
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=username, password=password)

            ssh_session = ssh_client.invoke_shell()
            ssh_session.send(f"enable\r")
            ssh_session.send(f"configure\r")
            ssh_session.send(f"user name {new_username} privilege {priv_level} password 0 {new_password}\r")
            ssh_session.send(f"end\r")
            ssh_session.send(f"copy running-config startup-config\r")
            time.sleep(1)
            ssh_session.send(f"y\r")
            time.sleep(1)
            ssh_session.send(f"exit\r")
            output = ssh_session.recv(65535).decode()

            # Close the SSH connection
            ssh_client.close()
            # formated_json = json.dumps(output, indent=2)
            # return formated_json
            return jsonify({
                "configuration_report": [{
                    "new_username": new_username,
                    "privilage": priv_level,
                    "new_password": new_password
                }]
            })
        except paramiko.AuthenticationException:
            return jsonify({"error": "Authentication failed. Please check your credentials."})
        except Exception as e:
            return jsonify({"error": "Unexpected error occurred: " + str(e)})

    @token_required
    def delete_user(current_user, ip,  new_username):

        allowed_roles = ["S_admin", "D_admin", "RO_admin"]
        if not current_user.roles in allowed_roles:
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'})

        try:
            # Create a Paramiko SSH client and connect
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=username, password=password)

            ssh_session = ssh_client.invoke_shell()
            ssh_session.send(f"enable\r")
            ssh_session.send(f"configure\r")
            ssh_session.send(f"no user name {new_username}\r")
            ssh_session.send(f"end\r")
            ssh_session.send(f"copy running-config startup-config\r")
            time.sleep(1)
            ssh_session.send(f"y\r")
            time.sleep(1)
            ssh_session.send(f"exit\r")
            # output = ssh_session.recv(65535).decode()

            # Close the SSH connection
            ssh_client.close()
            # formated_json = json.dumps(output, indent=2)
            # return formated_json
            return jsonify({
                "configuration_report": [{
                    "new_username": new_username,
                    "success": True
                }]
            })
        except paramiko.AuthenticationException:
            return jsonify({"error": "Authentication failed. Please check your credentials."})
        except Exception as e:
            return jsonify({"error": "Unexpected error occurred: " + str(e)})


    @token_required
    def ntp_config(current_user, ip, ntp_server_primary, ntp_server_secondary):

        allowed_roles = ["S_admin", "D_admin", "RO_admin"]
        if not current_user.roles in allowed_roles:
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'})

        try:
            # Create a Paramiko SSH client and connect
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=username, password=password)

            ssh_session = ssh_client.invoke_shell()
            ssh_session.send(f"enable\r")
            ssh_session.send(f"configure\r")
            ssh_session.send(f"system-time ntp UTC+05:00 {ntp_server_primary} {ntp_server_secondary} 24\r")
            ssh_session.send(f"end\r")
            ssh_session.send(f"copy running-config startup-config\r")
            time.sleep(1)
            ssh_session.send(f"y\r")
            time.sleep(1)
            ssh_session.send(f"exit\r")
            # output = ssh_session.recv(65535).decode()

            ssh_client.close()
            # formated_json = json.dumps(output, indent=2)
            # return
            return jsonify({
                "configuration_report" : [{
                    "ntp_server_primary": ntp_server_primary,
                    "ntp_server_secondary": ntp_server_secondary
                }]
            })

        except paramiko.AuthenticationException:
            return jsonify({"error": "Authentication failed. Please check your credentials."})
        except Exception as e:
            return jsonify({"error": "Unexpected error occurred: " + str(e)})

    @token_required
    def configure_vlan_and_ports_tp(current_user, ip, vlan_id, vlan_name, required_port, descriptions):

        allowed_roles = ["S_admin", "D_admin", "RO_admin"]
        if current_user.roles not in allowed_roles:
            return jsonify({"message": "Sizning Huqularingiz cheklangan"})

        try:

            logging.debug(f"Received data: IP={ip}, VLAN ID={vlan_id}, VLAN Name={vlan_name}, "
                          f"Required Ports={required_port}, Descriptions={descriptions}")

            if len(descriptions) < required_port:
                logging.debug("Number of descriptions is less than the required ports.")
                return jsonify({"error": "Number of descriptions provided is less than the required ports"})

            logging.debug("Connecting to SSH")
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=username, password=password)

            ssh_session = ssh_client.invoke_shell()
            ssh_session.send(f"enable\r")
            ssh_session.send(f"terminal length 0\r")
            ssh_session.send("configure\r")
            ssh_session.send(f"show vlan\r")
            time.sleep(2)
            vlan_output = ssh_session.recv(65535).decode()

            vlan_already_exists = False
            for line in vlan_output.split("\n"):
                if line.strip().startswith(str(vlan_id)):
                    vlan_already_exists = True
                    break

            if not vlan_already_exists:
                ssh_session.send(f"vlan {vlan_id}\r")
                ssh_session.send(f"name {vlan_name}\r")
                ssh_session.send("exit\r")
                time.sleep(1)

            # Har doim "show int eth status" ni bajarish
            ssh_session.send(f"show interface status\r")
            time.sleep(1)
            status_output = ssh_session.recv(65535).decode()
            link_up_ports = Filters_Default.TP_Link.filter_interface_status_tp_link(status_output)

            if not link_up_ports:
                ssh_client.close()
                return jsonify({"error": "No suitable ports found in status check"})

            selected_ports = link_up_ports[:required_port]
            for idx, port in enumerate(selected_ports):
                description = descriptions[idx]  # Descriptionni interfeysga yuklash
                ssh_session.send(f"interface gigabitEthernet {port['Port']}\r")
                ssh_session.send(f"description {description}\r")
                ssh_session.send(f"switchport general allowed vlan {vlan_id} untagged\r")
                ssh_session.send(f"switchport pvid {vlan_id}\r")
                ssh_session.send(f"no shutdown\r")
                ssh_session.send("exit\r")

            ssh_session.send("copy running-config startup-config\r")
            ssh_session.send("y\r")
            ssh_client.close()

            return jsonify({
                "configuration_report": [{
                    "vlan_configurations": [
                        {
                            "vlan_id": vlan_id,
                            "vlan_name": vlan_name
                        }
                    ],
                    "configured_interfaces": [
                        {
                            "interface": port["Port"],
                            "description": descriptions[idx]
                        }
                        for idx, port in enumerate(selected_ports)
                    ],
                    "success": True
                }]
            })

        except paramiko.AuthenticationException:
            return jsonify({"error": "Authentication failed. Please check your credentials."})
        except Exception as e:
            logging.error(f"Error during VLAN configuration: {str(e)}")


class DCNDevice:
    @staticmethod
    @token_required

    def show_version(current_user, ip):

        allowed_roles = ["S_admin", "D_admin", "RO_admin"]
        if not current_user.roles in allowed_roles:
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'})

        try:
            # Create a Paramiko SSH client and connect
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=username, password=password)

            ssh_session = ssh_client.invoke_shell()
            ssh_session.send(f"enable\r")
            ssh_session.send(f"terminal length 0\r")
            ssh_session.send(f"show version\r")
            time.sleep(1)
            output = ssh_session.recv(65535).decode()

            # Close the SSH connection
            ssh_client.close()
            formatted_output = output.strip('\r\n')
            checked_output = formatted_output.replace('\r\n', ' ')

            response = {
                'ip': ip,
                'version_info': checked_output
            }

            return jsonify(response)

        except Exception as e:
            return jsonify({"error": str(e)})

    @token_required
    def create_vlan(current_user, ip, vlan_id, vlan_name):

        allowed_roles = ["S_admin", "D_admin", "RO_admin"]
        if not current_user.roles in allowed_roles:
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'})

        try:
            # Create a Paramiko SSH client and connect
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=username, password=password)

            ssh_session = ssh_client.invoke_shell()
            ssh_session.send(f"enable\r")
            ssh_session.send(f"terminal length 0\r")
            ssh_session.send(f"show vlan id {vlan_id}\r")
            vlan_output = ssh_session.recv(65535).decode()

            vlan_arleady_exits = False
            for line in vlan_output.split('\n'):
                if line.strip().startswith(str(vlan_id)):
                    vlan_arleady_exits = True
                    break

            if vlan_arleady_exits:
                logging.warning(f"ID: {vlan_id} vlan mavjud")
                ssh_client.close()
                return jsonify({"error": f"VLAN ID: {vlan_id} mavjud"})

            if not vlan_arleady_exits:
                ssh_session.send(f"conf t\r")
                ssh_session.send(f"vlan {vlan_id}\r")
                ssh_session.send(f"name {vlan_name}\r")
                ssh_session.send(f"exit\r")

            ssh_session.send(f"end\r")
            ssh_session.send(f"copy running-config startup-config\r")
            time.sleep(1)
            ssh_session.send(f"y\r")
            time.sleep(1)
            ssh_session.send(f"exit\r")
            # output = ssh_session.recv(65535).decode()
            # Close the SSH connection
            ssh_client.close()
            # formated_json = json.dumps(output, indent=2)
            # return formated_json

            return jsonify({
                "configuration_report": [{
                    "vlan_id": vlan_id,
                    "vlan_name": vlan_name,
                    "success": True
                }]
            })
        except paramiko.AuthenticationException:
            return jsonify({"error": "Authentication failed. Please check your credentials."})
        except Exception as e:
            return jsonify({"error": "Unexpected error occurred: " + str(e)})

    @token_required
    def delete_vlan(current_user, ip, vlan_id):

        allowed_roles = ["S_admin", "D_admin", "RO_admin"]
        if not current_user.roles in allowed_roles:
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'})

        try:
            # Create a Paramiko SSH client and connect
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=username, password=password)

            ssh_session = ssh_client.invoke_shell()
            ssh_session.send(f"enable\r")
            time.sleep(1)
            ssh_session.send(f"terminal length 0\r")
            time.sleep(1)
            ssh_session.send(f"show vlan id {vlan_id}\r")
            time.sleep(2)
            vlan_output = ssh_session.recv(65535).decode()

            vlan_exists = False
            for line in vlan_output.split('\n'):
                if line.strip().startswith(str(vlan_id)):
                    vlan_exists = True
                    break

            if not vlan_exists:
                logging.warning(f"ID: {vlan_id} vlan mavjud emas")
                ssh_client.close()
                return jsonify({"error": f"VLAN ID: {vlan_id} mavjud emas"})


            ssh_session.send(f"conf t\r")
            ssh_session.send(f"no vlan {vlan_id}\r")
            ssh_session.send(f"end\r")
            ssh_session.send(f"copy running-config startup-config\r")
            time.sleep(1)
            ssh_session.send(f"y\r")
            time.sleep(1)
            ssh_session.send(f"exit\r")

            # Close the SSH connection
            ssh_client.close()

            return jsonify({
                "configuration_report": [{
                    "vlan_id": vlan_id,
                    "success": True
                }]
            })

        except paramiko.AuthenticationException:
            return jsonify({"error": "Authentication failed. Please check your credentials."})
        except Exception as e:
            return jsonify({"error": "Unexpected error occurred: " + str(e)})

    @token_required
    def logging_server(current_user, ip, log_server, log_level_num):

        allowed_roles = ["S_admin", "D_admin", "RO_admin"]
        if current_user.roles not in allowed_roles:
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'})

        # Mapping log_level_num to corresponding log_level strings
        log_level_map = {
            2: "critical",
            4: "warnings",
            6: "informational",
            7: "debugging"
        }

        log_level = log_level_map.get(log_level_num)
        if log_level is None:
            return jsonify({'message': "Noto‘g‘ri log darajasi"})
        try:
            # Create a Paramiko SSH client and connect
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=username, password=password)

            ssh_session = ssh_client.invoke_shell()
            ssh_session.send(f"enable\r")
            ssh_session.send(f"conf t\r")
            ssh_session.send(f"logging {log_server} facility local7 level {log_level}\r")
            ssh_session.send(f"logging flash level informational\r")
            ssh_session.send(f"logging executed-commands enable\r")
            ssh_session.send(f"logging loghost sequence-number\r")
            ssh_session.send(f"end\r")
            ssh_session.send(f"copy running-config startup-config\r")
            time.sleep(1)
            ssh_session.send(f"y\r")
            time.sleep(1)
            ssh_session.send(f"exit\r")
            output = ssh_session.recv(65535).decode()

            # Close the SSH connection
            ssh_client.close()
            # formated_json = json.dumps(output, indent=2)
            # return formated_json

            return jsonify({
                "configuration_report" : [{
                    "log_server": log_server,
                    "success": True
                }]
            })

        except paramiko.AuthenticationException:
            return jsonify({"error": "Authentication failed. Please check your credentials."})
        except Exception as e:
            return jsonify({"error": "Unexpected error occurred: " + str(e)})

    @token_required
    def nacs_server(current_user, ip, nacs_server, nacs_key):

        allowed_roles = ["S_admin", "D_admin", "RO_admin"]
        if not current_user.roles in allowed_roles:
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'})

        # username = user
        # password = passw

        try:
            # Create a Paramiko SSH client and connect
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=username, password=password)

            ssh_session = ssh_client.invoke_shell()
            ssh_session.send(f"enable\r")
            ssh_session.send(f"conf t\r")
            ssh_session.send(f"authentication logging enable\r")
            ssh_session.send(f"banner motd Tarmoq qurulmasiga ruxsatsiz kirish qonunga muvofiq ta'qib qilinadi\r")
            ssh_session.send(f"banner login Tarmoq qurulmasiga ruxsatsiz kirish qonunga muvofiq ta'qib qilinadi\r")
            ssh_session.send(f"tacacs-server authentication host {nacs_server} key 0 {nacs_key}\r")
            ssh_session.send(f"authentication line console login tacacs local\r")
            ssh_session.send(f"authentication line vty login tacacs local\r")
            ssh_session.send(f"authentication line web login tacacs local\r")
            ssh_session.send(f"authorization line console exec tacacs local\r")
            ssh_session.send(f"authorization line vty exec tacacs local\r")
            ssh_session.send(f"authorization line web exec tacacs local\r")
            ssh_session.send(f"aaa authorization config-commands\r")
            ssh_session.send(f"authorization line vty command 15 tacacs local\r")
            ssh_session.send(f"accounting line console exec start-stop tacacs\r")
            ssh_session.send(f"accounting line vty exec start-stop tacacs\r")
            ssh_session.send(f"accounting line console command 15 start-stop tacacs\r")
            ssh_session.send(f"accounting line vty command 15 start-stop tacacs\r")
            ssh_session.send(f"end\r")
            ssh_session.send(f"copy running-config startup-config\r")
            time.sleep(1)
            ssh_session.send(f"y\r")
            time.sleep(1)
            ssh_session.send(f"exit\r")
            # output = ssh_session.recv(65535).decode()

            # Close the SSH connection
            ssh_client.close()
            # formated_json = json.dumps(output, indent=2)
            # return formated_json

            return jsonify({
                "configuration_report" : [{
                    "nacs_server": nacs_server,
                    "success": True
                }]
            })

        except paramiko.AuthenticationException:
            return jsonify({"error": "Authentication failed. Please check your credentials."})
        except Exception as e:
            return jsonify({"error": "Unexpected error occurred: " + str(e)})

    @token_required
    def auth_default(current_user, ip):

        allowed_roles = ["S_admin", "D_admin", "RO_admin"]
        if not current_user.roles in allowed_roles:
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'})

        # username = user
        # password = passw

        try:
            # Create a Paramiko SSH client and connect
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=username, password=password)

            ssh_session = ssh_client.invoke_shell()
            ssh_session.send(f"enable\r")
            ssh_session.send(f"conf t\r")
            ssh_session.send(f"authentication logging enable\r")
            ssh_session.send(f"banner motd Tarmoq qurulmasiga ruxsatsiz kirish qonunga muvofiq ta'qib qilinadi\r")
            ssh_session.send(f"banner login Tarmoq qurulmasiga ruxsatsiz kirish qonunga muvofiq ta'qib qilinadi\r")
            ssh_session.send(f"authentication line console login local\r")
            ssh_session.send(f"authentication line vty login local\r")
            ssh_session.send(f"authentication line web login local\r")
            ssh_session.send(f"authorization line console exec local\r")
            ssh_session.send(f"authorization line vty exec local\r")
            ssh_session.send(f"authorization line web exec local\r")
            ssh_session.send(f"end\r")
            ssh_session.send(f"copy running-config startup-config\r")
            time.sleep(1)
            ssh_session.send(f"y\r")
            time.sleep(1)
            ssh_session.send(f"exit\r")
            # output = ssh_session.recv(65535).decode()

            # Close the SSH connection
            ssh_client.close()
            # formated_json = json.dumps(output, indent=2)
            # return formated_json
            return jsonify({
                "configuration_report" : [{
                    "success": True
                }]
            })

        except paramiko.AuthenticationException:
            return jsonify({"error": "Authentication failed. Please check your credentials."})
        except Exception as e:
            return jsonify({"error": "Unexpected error occurred: " + str(e)})

    @token_required
    def add_user(current_user, ip, new_username, new_password, privilage):

        allowed_roles = ["S_admin", "D_admin", "RO_admin"]
        if not current_user.roles in allowed_roles:
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'})

        try:
            # Create a Paramiko SSH client and connect
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=username, password=password)

            ssh_session = ssh_client.invoke_shell()
            ssh_session.send(f"enable\r")
            ssh_session.send(f"conf t\r")
            ssh_session.send(f"username {new_username} privilege {privilage} password 0 {new_password}\r")
            ssh_session.send(f"end\r")
            ssh_session.send(f"copy running-config startup-config\r")
            time.sleep(1)
            ssh_session.send(f"y\r")
            time.sleep(1)
            ssh_session.send(f"exit\r")
            # output = ssh_session.recv(65535).decode()

            # Close the SSH connection
            ssh_client.close()
            # formated_json = json.dumps(output, indent=2)
            # return formated_json

            return jsonify({
                "configuration_report" : [{
                    "new_username": new_username,
                    "privilage":  privilage,
                    "success": True
                }]
            })

        except paramiko.AuthenticationException:
            return jsonify({"error": "Authentication failed. Please check your credentials."})
        except Exception as e:
            return jsonify({"error": "Unexpected error occurred: " + str(e)})

    @token_required
    def delete_user(current_user, ip, new_username):

        allowed_roles = ["S_admin", "D_admin", "RO_admin"]
        if not current_user.roles in allowed_roles:
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'})

        try:
            # Create a Paramiko SSH client and connect
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=username, password=password)

            ssh_session = ssh_client.invoke_shell()
            ssh_session.send(f"enable\r")
            ssh_session.send(f"conf t\r")
            ssh_session.send(f"no username {new_username} \r")
            ssh_session.send(f"end\r")
            ssh_session.send(f"copy running-config startup-config\r")
            time.sleep(1)
            ssh_session.send(f"y\r")
            time.sleep(1)
            ssh_session.send(f"exit\r")
            # output = ssh_session.recv(65535).decode()

            # Close the SSH connection
            ssh_client.close()
            # formated_json = json.dumps(output, indent=2)
            # return formated_json

            return jsonify({
                "configuration_report" : [{
                    "new_username": new_username,
                    "success": True
                }]
            })

        except paramiko.AuthenticationException:
            return jsonify({"error": "Authentication failed. Please check your credentials."})
        except Exception as e:
            return jsonify({"error": "Unexpected error occurred: " + str(e)})



    @token_required
    def snmp_config(current_user, ip, snmp_host ,snpm_key):

        allowed_roles = ["S_admin", "D_admin", "RO_admin"]
        if not current_user.roles in allowed_roles:
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'})

        try:
            # Create a Paramiko SSH client and connect
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=username, password=password)

            ssh_session = ssh_client.invoke_shell()
            ssh_session.send(f"enable\r")
            ssh_session.send(f"conf t\r")
            ssh_session.send(f"snmp-server enable\r")
            ssh_session.send(f"snmp-server timeout 300\r")
            ssh_session.send(f"snmp-server securityip disable\r")
            ssh_session.send(f"snmp-server host {snmp_host} v2c {snpm_key}\r")
            ssh_session.send(f"snmp-server community ro 7 {snpm_key}\r")
            ssh_session.send(f"snmp-server enable traps\r")
            ssh_session.send(f"snmp-server enable traps mac-notification\r")
            ssh_session.send(f"snmp-server enable traps if-ber max-warning-value 50\r")
            ssh_session.send(f"snmp-server enable traps if-packet-lost-rate max-warning-value 50\r")
            ssh_session.send(f"snmp-server enable traps cpu-used-per max-warning-value 44\r")
            ssh_session.send(f"snmp-server enable traps mem-used-per max-warning-value 50\r")
            ssh_session.send(f"snmp-server enable traps element-state-to-down\r")
            ssh_session.send(f"snmp-server ddm-mib disable\r")
            ssh_session.send(f"snmp-server ddm-electronic-hidden disable\r")
            ssh_session.send(f"end\r")
            ssh_session.send(f"copy running-config startup-config\r")
            time.sleep(1)
            ssh_session.send(f"y\r")
            time.sleep(1)
            ssh_session.send(f"exit\r")
            # output = ssh_session.recv(65535).decode()

            # Close the SSH connection
            ssh_client.close()
            # formated_json = json.dumps(output, indent=2)
            # return formated_json

            return jsonify({
                "configuration_report" : [{
                    "snmp_host": snmp_host,
                    "success": True
                }]
            })

        except paramiko.AuthenticationException:
            return jsonify({"error": "Authentication failed. Please check your credentials."})
        except Exception as e:
            return jsonify({"error": "Unexpected error occurred: " + str(e)})

    @token_required
    def ntp_config(current_user, ip, ntp_server_primary, ntp_server_secondary):

        allowed_roles = ["S_admin", "D_admin", "RO_admin"]
        if not current_user.roles in allowed_roles:
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'})

        try:
            # Create a Paramiko SSH client and connect
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=username, password=password)

            ssh_session = ssh_client.invoke_shell()
            ssh_session.send(f"enable\r")
            ssh_session.send(f"conf t\r")
            ssh_session.send(f"ntp enable\r")
            ssh_session.send(f"ntp server {ntp_server_primary}\r")
            ssh_session.send(f"ntp server {ntp_server_secondary}\r")
            ssh_session.send(f"end\r")
            ssh_session.send(f"copy running-config startup-config\r")
            time.sleep(1)
            ssh_session.send(f"y\r")
            time.sleep(1)
            ssh_session.send(f"exit\r")
            # output = ssh_session.recv(65535).decode()

            # Close the SSH connection
            ssh_client.close()
            # formated_json = json.dumps(output, indent=2)
            # return formated_json

            return jsonify({
                "configuration_report" : [{
                    "ntp_server_primary": ntp_server_primary,
                    "ntp_server_secondary": ntp_server_secondary,
                    "success": True
                }]
            })

        except paramiko.AuthenticationException:
            return jsonify({"error": "Authentication failed. Please check your credentials."})
        except Exception as e:
            return jsonify({"error": "Unexpected error occurred: " + str(e)})

    @token_required
    def configure_vlan_and_ports(current_user, ip, vlan_id, vlan_name, required_port, descriptions):
        try:
            # Validate that descriptions match the required_port count
            if len(descriptions) < required_port:
                return jsonify({"error": "Number of descriptions provided is less than the required ports"})

            # Create a Paramiko SSH client and connect
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=username, password=password)

            # Run "show vlan" command to check if VLAN already exists
            ssh_session = ssh_client.invoke_shell()
            ssh_session.send("terminal length 0\r")
            time.sleep(1)
            ssh_session.send("show vlan\r")
            time.sleep(2)  # Allow time for the output
            vlan_output = ssh_session.recv(65535).decode()

            # Check VLAN existence directly in the output
            vlan_already_exists = False
            for line in vlan_output.split("\n"):
                if line.strip().startswith(str(vlan_id)):
                    vlan_already_exists = True
                    break

            # If VLAN does not exist, create it
            if not vlan_already_exists:
                ssh_session.send(f"conf t\r")
                ssh_session.send(f"vlan {vlan_id}\r")
                ssh_session.send(f"name {vlan_name}\r")
                ssh_session.send(f"exit\r")
                ssh_session.send(f"end\r")
                ssh_session.send(f"copy running-config startup-config\r")
                time.sleep(1)
                ssh_session.send(f"y\r")
                time.sleep(1)

            # Run "show int eth status" command and filter results
            ssh_session.send("show int eth status\r")
            time.sleep(2)
            int_status_output = ssh_session.recv(65535).decode()
            filtered_interfaces = Filters_Default.Nag_filter.filter_interface_status(int_status_output)

            if not filtered_interfaces:
                ssh_client.close()
                return jsonify({"error": "No matching interfaces found"})

            # Select the required number of ports
            selected_interfaces = filtered_interfaces[:required_port]

            # Configure each selected interface with description and VLAN
            ssh_session.send(f"conf t\r")
            for idx, interface in enumerate(selected_interfaces):
                description = descriptions[idx]  # Use the provided description for the interface
                ssh_session.send(f"interface ethernet {interface['Interface']}\r")
                ssh_session.send(f"description {description}\r")
                ssh_session.send(f"switchport access vlan {vlan_id}\r")
                ssh_session.send(f"no shutdown\r")
                ssh_session.send(f"exit\r")
            ssh_session.send(f"end\r")
            ssh_session.send(f"copy running-config startup-config\r")
            time.sleep(1)
            ssh_session.send(f"y\r")
            time.sleep(1)
            ssh_session.send(f"exit\r")
            config_output = ssh_session.recv(65535).decode()

            # Close the SSH connection
            ssh_client.close()

            return jsonify({
                "configuration_report": [{
                    "vlan_configurations": [
                        {
                            "vlan_id": vlan_id,
                            "vlan_name": vlan_name
                        }
                    ],
                    "configured_interfaces": [
                        {
                            "interface": iface["Interface"],
                            "description": descriptions[idx]
                        }
                        for idx, iface in enumerate(selected_interfaces)
                    ],
                    "success": True
                }]
            })

        except paramiko.AuthenticationException:
            return jsonify({"error": "Authentication failed. Please check your credentials."})
        except Exception as e:
            return jsonify({"error": "Unexpected error occurred: " + str(e)})
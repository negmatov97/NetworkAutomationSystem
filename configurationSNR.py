from flask import json, jsonify
from gen_token import token_required
import paramiko
import time

class show:
    @token_required
    def connect_to_ip1(current_user, ip):

        if not (current_user.role == 'admin' or current_user.role == 'user'):
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

        username = current_user.username
        password = current_user.radius_free

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
            formated_json = json.dumps(output, indent=2)
            return {"Success": formated_json}
        except Exception as e:
            return "Error: " + str(e)

    @token_required
    def sh_ver(current_user, ip_address):

        if not (current_user.role == 'admin' or current_user.role == 'user'):
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

        username = current_user.username
        password = current_user.radius_free

        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip_address, username=username, password=password)

            ssh_session = ssh_client.invoke_shell()
            ssh_session.send(f"enable\r")
            ssh_session.send(f"terminal length 0\r")
            ssh_session.send(f"show version\r")
            time.sleep(1)
            output = ssh_session.recv(65535).decode()
            ssh_client.close()  # Close the SSH connection

            # Find the start and end markers for the "show version" output
            start_marker = "show version"
            end_marker = "#"

            start_index = output.find(start_marker)
            end_index = output.find(end_marker, start_index)

            if start_index != -1 and end_index != -1:
                output = output[start_index + len(start_marker):end_index].strip()

            # Create a dictionary with the extracted output
            result_dict = {
                'ip': ip_address,
                'message': 'Connected to device successfully',
                'output': output
            }

            return result_dict
        except Exception as e:
            print(f"SSH connection error: {str(e)}")
            return {
                'ip': ip,
                'message': 'Authentication failed or SSH error',
                'output': None
            }

    def sh_run():
        device_ip = connecting.ssh_modul.device_ip
        username = connecting.ssh_modul.username
        password = connecting.ssh_modul.password

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=device_ip, username=username, password=password)

        ssh_session = ssh_client.invoke_shell()
        ssh_session.send(f"enable\r")
        ssh_session.send(f"terminal length 0\r")
        ssh_session.send(f"show run\r")
        time.sleep(1)
        output = ssh_session.recv(65535).decode()
        print(output)
        return output

    def sh_vlan():
        device_ip = connecting.ssh_modul.device_ip
        username = connecting.ssh_modul.username
        password = connecting.ssh_modul.password

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=device_ip, username=username, password=password)

        ssh_session = ssh_client.invoke_shell()
        ssh_session.send(f"enable\r")
        ssh_session.send(f"terminal length 0\r")
        ssh_session.send(f"show vlan\r")
        time.sleep(1)
        output = ssh_session.recv(65535).decode()
        print(output)
        return output

    def sh_mac_vl():
        device_ip = connecting.ssh_modul.device_ip
        username = connecting.ssh_modul.username
        password = connecting.ssh_modul.password

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=device_ip, username=username, password=password)

        ssh_session = ssh_client.invoke_shell()
        ssh_session.send(f"enable\r")
        ssh_session.send(f"terminal length 0\r")
        ssh_session.send(f"show mac-address-table vlan {vl_id}\r")
        time.sleep(1)
        output = ssh_session.recv(65535).decode()
        print(output)
        return output

    def sh_mac_interf():
        device_ip = connecting.ssh_modul.device_ip
        username = connecting.ssh_modul.username
        password = connecting.ssh_modul.password

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=device_ip, username=username, password=password)

        ssh_session = ssh_client.invoke_shell()
        ssh_session.send(f"enable\r")
        ssh_session.send(f"terminal length 0\r")
        ssh_session.send(f"show mac-address-table int eth 1/0/{inter_id}\r")
        time.sleep(1)
        output = ssh_session.recv(65535).decode()
        print(output)
        return output

    def sh_log():
        device_ip = connecting.ssh_modul.device_ip
        username = connecting.ssh_modul.username
        password = connecting.ssh_modul.password

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=device_ip, username=username, password=password)

        ssh_session = ssh_client.invoke_shell()
        ssh_session.send(f"enable\r")
        ssh_session.send(f"terminal length 0\r")
        ssh_session.send(f"show logging flash\r")
        time.sleep(1)
        output = ssh_session.recv(65535).decode()
        print(output)
        return output

    def sh_interf_stat():
        device_ip = connecting.ssh_modul.device_ip
        username = connecting.ssh_modul.username
        password = connecting.ssh_modul.password

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=device_ip, username=username, password=password)

        ssh_session = ssh_client.invoke_shell()
        ssh_session.send(f"enable\r")
        ssh_session.send(f"terminal length 0\r")
        ssh_session.send(f"show int eth status\r")
        time.sleep(1)
        output = ssh_session.recv(65535).decode()
        print(output)
        return output


class config:
    def c_vl():
        device_ip = connecting.ssh_modul.device_ip
        username = connecting.ssh_modul.username
        password = connecting.ssh_modul.password
        vl_id = str(input("VLAN ID: "))
        vl_name = str(input("VLAN name:"))

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=device_ip, username=username, password=password)

        #jarayon
        ssh_session = ssh_client.invoke_shell()
        ssh_session.send(f"enable\r")
        ssh_session.send(f"config terminal\r")
        ssh_session.send(f"vlan {vl_id}\r")
        ssh_session.send(f"name {vl_name}\r")
        ssh_session.send(f"end\r")
        time.sleep(1)
        output = ssh_session.recv(65535).decode()
        print(output)
        return output

    def d_vl():
        device_ip = connecting.ssh_modul.device_ip
        username = connecting.ssh_modul.username
        password = connecting.ssh_modul.password
        vl_id = str(input("VLAN ID: "))

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=device_ip, username=username, password=password)


        ssh_session = ssh_client.invoke_shell()
        ssh_session.send(f"enable\r")
        ssh_session.send(f"config terminal\r")
        ssh_session.send(f"no vlan {vl_id}\r")
        ssh_session.send(f"end\r")
        time.sleep(1)
        output = ssh_session.recv(65535).decode()
        print(output)
        return output

    def w_int_acc():
        device_ip = connecting.ssh_modul.device_ip
        username = connecting.ssh_modul.username
        password = connecting.ssh_modul.password
        inter_id = str(input("VLAN ID: "))

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=device_ip, username=username, password=password)

        ssh_session = ssh_client.invoke_shell()
        ssh_session.send(f"enable\r")
        ssh_session.send(f"config terminal\r")
        ssh_session.send(f"int eth 1/0/{inter_id}\r")
        ssh_session.send(f"switchport mode access\r")
        ssh_session.send(f"end\r")
        time.sleep(1)
        output = ssh_session.recv(65535).decode()
        print(output)
        return output

    def w_int_trk():
        device_ip = connecting.ssh_modul.device_ip
        username = connecting.ssh_modul.username
        password = connecting.ssh_modul.password
        inter_id = str(input("VLAN ID: "))

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=device_ip, username=username, password=password)

        ssh_session = ssh_client.invoke_shell()
        ssh_session.send(f"enable\r")
        ssh_session.send(f"config terminal\r")
        ssh_session.send(f"int eth 1/0/{inter_id}\r")
        ssh_session.send(f"switchport mode trunk\r")
        ssh_session.send(f"end\r")
        time.sleep(1)
        output = ssh_session.recv(65535).decode()
        print(output)
        return output

    def w_int_ac_vl():
        device_ip = connecting.ssh_modul.device_ip
        username = connecting.ssh_modul.username
        password = connecting.ssh_modul.password
        inter_id = str(input("VLAN ID: "))
        vl_id = str(input("VLAN ID: "))

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=device_ip, username=username, password=password)

        ssh_session = ssh_client.invoke_shell()
        ssh_session.send(f"enable\r")
        ssh_session.send(f"config terminal\r")
        ssh_session.send(f"int eth 1/0/{inter_id}\r")
        ssh_session.send(f"switchport access vlan {vl_id}\r")
        ssh_session.send(f"end\r")
        time.sleep(1)
        output = ssh_session.recv(65535).decode()
        print(output)
        return output

    def w_int_trk_vl():
        device_ip = connecting.ssh_modul.device_ip
        username = connecting.ssh_modul.username
        password = connecting.ssh_modul.password
        inter_id = str(input("VLAN ID: "))
        vl_id = str(input("VLAN ID: "))

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=device_ip, username=username, password=password)

        ssh_session = ssh_client.invoke_shell()
        ssh_session.send(f"enable\r")
        ssh_session.send(f"config terminal\r")
        ssh_session.send(f"int eth 1/0/{inter_id}\r")
        ssh_session.send(f"switchport trunk allowed vlan add {vl_id}\r")
        ssh_session.send(f"end\r")
        time.sleep(1)
        output = ssh_session.recv(65535).decode()
        print(output)
        return output

    def w_d_int_trk_vl():
        device_ip = connecting.ssh_modul.device_ip
        username = connecting.ssh_modul.username
        password = connecting.ssh_modul.password
        inter_id = str(input("VLAN ID: "))
        vl_id = str(input("VLAN ID: "))

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=device_ip, username=username, password=password)

        ssh_session = ssh_client.invoke_shell()
        ssh_session.send(f"enable\r")
        ssh_session.send(f"config terminal\r")
        ssh_session.send(f"int eth 1/0/{inter_id}\r")
        ssh_session.send(f"switchport trunk allowed vlan remove {vl_id}\r")
        ssh_session.send(f"end\r")
        time.sleep(1)
        output = ssh_session.recv(65535).decode()
        print(output)
        return output

    def w_d_int_ac_vl():
        device_ip = connecting.ssh_modul.device_ip
        username = connecting.ssh_modul.username
        password = connecting.ssh_modul.password
        inter_id = str(input("VLAN ID: "))

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=device_ip, username=username, password=password)

        ssh_session = ssh_client.invoke_shell()
        ssh_session.send(f"enable\r")
        ssh_session.send(f"config terminal\r")
        ssh_session.send(f"int eth 1/0/{inter_id}\r")
        ssh_session.send(f"switchport access vlan 1\r")
        ssh_session.send(f"no description\r")
        ssh_session.send(f"end\r")
        time.sleep(1)
        output = ssh_session.recv(65535).decode()
        print(output)
        return output
        return output
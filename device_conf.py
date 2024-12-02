from flask import jsonify, request, Flask, Blueprint
from db_config import db, UniversalTable, Vendor, Log
from gen_token import token_required
import binary_commands
import yaml
from datetime import datetime



config = Blueprint('config', __name__)


# Sample function to retrieve data
def get_one(ip):
    # Replace with your logic to retrieve data based on IP
    # For example, you can query the database using SQLAlchemy
    record = UniversalTable.query.filter_by(ip_add=ip).first()
    return record

# Load device models from device.yaml
with open('device.yaml', 'r') as file:
    device_models = yaml.safe_load(file)

vendor_models = {}
for brand, models in device_models.items():
    for model in models:
        vendor_models[model['model'].upper()] = brand

def get_vendor_name(vendor_fk):
    try:
        vendor = Vendor.query.filter_by(id=vendor_fk).first()
        if vendor:
            return vendor.name
        else:
            return None  # Return None if vendor with given ID is not found
    except Exception as e:
        # Handle exceptions if necessary
        print(str(e))
        return None  # Return None in case of any exception


@config.route('/show_version', methods=['POST'])
@token_required
def new_function(current_user):


    allowed_roles = ["S_admin", "D_admin", "RO_admin"]
    if not current_user.roles in allowed_roles:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:
        # Log the access
        log_entry = Log(
            username=current_user.username,
            last_name=current_user.familiya,
            district=current_user.dist,
            roles=current_user.roles,
            actions=f"{current_user.username} {current_user.familiya} tomonidan /show_version/ buyrug'i berildi",
            times=datetime.now(),
            dates = datetime.today().date()
        )
        db.session.add(log_entry)
        db.session.commit()

        data = request.json
        ip_addresses = data.get('ip_addresses', [])
        results = {}

        for ip in ip_addresses:
            record = get_one(ip)

            if record:
                vendor_fk = record.vendor_fk
                vendor_name = get_vendor_name(vendor_fk)

                if vendor_name:
                    brand = vendor_models.get(vendor_name.upper())
                    if brand:
                        if brand == 'snr':
                            result = binary_commands.NagDevice.show_version(ip)
                            results[ip] = result.json

                        elif brand == 'tp-link':
                            result = binary_commands.TplinkDevice.show_system_info(ip)
                            results[ip] = result.json

                        elif brand == 'dcn':
                            result = binary_commands.DCNDevice.show_version(ip)
                            results[ip] = result.json

                        else:
                            results[ip] = jsonify({"error:": f"Unsupported vendor '{vendor_name}'"})

                    else:
                        results[ip] = jsonify({"error:": f"Unsupported vendor '{vendor_name}'"})

                else:
                    results[ip] = jsonify({"error:": f"Vendor name not found for vendor_fk '{vendor_fk}'"}), 500

            else:
                results[ip] = jsonify({"error:": "IP address not found in the database"}), 500

        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@config.route('/conf_vlan_add', methods=['POST'])
@token_required
def create_vlan(current_user):

    allowed_roles = ["S_admin", "D_admin", "RO_admin"]
    if not current_user.roles in allowed_roles:
        return jsonify({'message': 'Sizning Huquqlaringiz cheklangan'}), 401

    try:

        data = request.json
        vlan_id = data['vlan_id']
        vlan_name = data['vlan_name']
        ip_addresses = data['ip_addresses']
        results = {}

        # Log for create vlan
        log_entry = Log(
            username=current_user.username,
            last_name=current_user.familiya,
            district=current_user.dist,
            roles=current_user.roles,
            actions=f"{current_user.username} {current_user.familiya} tomonidan {vlan_id} ID ga ega {vlan_name} vlani yaratildi",
            times=datetime.now(),
            dates=datetime.today().date()
        )
        db.session.add(log_entry)
        db.session.commit()

        for ip in ip_addresses:
            record = get_one(ip)

            if record:
                vendor_fk = record.vendor_fk
                vendor_name = get_vendor_name(vendor_fk)

                if vendor_name:
                    brand = vendor_models.get(vendor_name.upper())
                    if brand:
                        if brand == 'snr':
                            result = binary_commands.NagDevice.create_vlan(ip, vlan_id, vlan_name)
                            results[ip] = result.json

                        elif brand == 'tp-link':
                            result = binary_commands.TplinkDevice.create_vlan(ip, vlan_id, vlan_name)
                            results[ip] = result.json

                        elif brand == 'dcn':
                            result = binary_commands.DCNDevice.create_vlan(ip, vlan_id, vlan_name)
                            results[ip] = result.json

                        else:
                            results[ip] = jsonify({"error:": f"Unsupported vendor '{vendor_name}'"})

                    else:
                        results[ip] = jsonify({"error:": f"Unsupported vendor '{vendor_name}'"})

                else:
                    results[ip] = jsonify({"error:": f"Vendor name not found for vendor_fk '{vendor_fk}'"}), 500

            else:
                results[ip] = jsonify({"error:": "IP address not found in the database"}), 500

        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@config.route('/conf_vlan_delete', methods=['POST'])
@token_required
def conf_vlan_delete(current_user):

    allowed_roles = ["S_admin", "D_admin", "RO_admin"]
    if not current_user.roles in allowed_roles:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:
        data = request.json
        vlan_id = data['vlan_id']
        ip_addresses = data['ip_addresses']
        results = {}

        # Log for delete vlan
        log_entry = Log(
            username=current_user.username,
            last_name=current_user.familiya,
            district=current_user.dist,
            roles=current_user.roles,
            actions=f"{current_user.username} {current_user.familiya} tomonidan {vlan_id} ID vlani o'chirildi",
            times=datetime.now(),
            dates=datetime.today().date()
        )
        db.session.add(log_entry)
        db.session.commit()

        for ip in ip_addresses:
            record = get_one(ip)

            if record:
                vendor_fk = record.vendor_fk
                vendor_name = get_vendor_name(vendor_fk)

                if vendor_name:
                    brand = vendor_models.get(vendor_name.upper())
                    if brand:
                        if brand == 'snr':
                            result = binary_commands.NagDevice.delete_vlan(ip, vlan_id)
                            results[ip] = result.json

                        elif brand == 'tp-link':
                            result = binary_commands.TplinkDevice.delete_vlan(ip, vlan_id)
                            results[ip] = result.json

                        elif brand == 'dcn':
                            result = binary_commands.DCNDevice.delete_vlan(ip, vlan_id)
                            results[ip] = result.json

                        else:
                            results[ip] = jsonify({"error:": f"Unsupported vendor '{vendor_name}'"})

                    else:
                        results[ip] = jsonify({"error:": f"Error: Unsupported vendor '{vendor_name}'"}), 500

                else:
                    results[ip] = jsonify({"error:": f"Vendor name not found for vendor_fk '{vendor_fk}'"}), 500

            else:
                results[ip] = jsonify({"error:": "IP address not found in the database"}), 500

        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@config.route('/conf_logging_server', methods=['POST'])
@token_required
def conf_logging_server(current_user):

    allowed_roles = ["S_admin", "D_admin", "RO_admin"]
    if not current_user.roles in allowed_roles:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:
        data = request.json
        log_server = data['log_server']
        log_level_num = data['log_level_num']
        ip_addresses = data['ip_addresses']

        results = {}

        # Log for delete vlan
        log_entry = Log(
            username=current_user.username,
            last_name=current_user.familiya,
            district=current_user.dist,
            roles=current_user.roles,
            actions=f"{current_user.username} {current_user.familiya} tomonidan {ip_addresses} qurilmasi log funktsiyasi {log_server} serveriga "
                    f"{log_level_num} darajasida yo'naltirildi",
            times=datetime.now(),
            dates=datetime.today().date()
        )
        db.session.add(log_entry)
        db.session.commit()

        for ip in ip_addresses:
            record = get_one(ip)

            if record:
                vendor_fk = record.vendor_fk
                vendor_name = get_vendor_name(vendor_fk)

                if vendor_name:
                    brand = vendor_models.get(vendor_name.upper())
                    if brand:
                        if brand == 'snr':
                            result = binary_commands.NagDevice.logging_server(ip, log_server, log_level_num)
                            results[ip] = result.json

                        elif brand == 'tp-link':
                            result = binary_commands.TplinkDevice.logging_server(ip, log_server, log_level_num)
                            results[ip] = result.json

                        elif brand == 'dcn':
                            result = binary_commands.DCNDevice.logging_server(ip, log_server, log_level_num)
                            results[ip] = result.json

                        else:
                            results[ip] = jsonify({"error:": f"Unsupported vendor '{vendor_name}'"})

                    else:
                        results[ip] = jsonify({"error:": f"Unsupported vendor {vendor_name}"}), 500

                else:
                    results[ip] = jsonify({"error:": f"Vendor name not found for vendor_fk {vendor_fk}"}), 500

            else:
                results[ip] = jsonify({"error:": "IP address not found in the database"}), 500

        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@config.route('/conf_nacs_server', methods=['POST'])
@token_required
def conf_nacs_server(current_user):

    allowed_roles = ["S_admin", "D_admin", "RO_admin"]
    if not current_user.roles in allowed_roles:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:
        data = request.json
        nacs_server = data.get('nacs_server')
        nacs_key = data.get('nacs_key')
        ip_addresses = data.get('ip_addresses', [])
        results = {}

        # Log for delete vlan
        log_entry = Log(
            username=current_user.username,
            last_name=current_user.familiya,
            district=current_user.dist,
            roles=current_user.roles,
            actions=f"{current_user.username} {current_user.familiya} tomonidan {ip_addresses} qurilmasi qurilmasi "
                    f"xavfsizlik funktsiyalari {nacs_server} serveriga yo'naltirildi",
            times=datetime.now(),
            dates=datetime.today().date()
        )
        db.session.add(log_entry)
        db.session.commit()

        for ip in ip_addresses:
            record = get_one(ip)

            if record:
                vendor_fk = record.vendor_fk
                vendor_name = get_vendor_name(vendor_fk)

                if vendor_name:
                    brand = vendor_models.get(vendor_name.upper())
                    if brand:
                        if brand == 'snr':
                            result = binary_commands.NagDevice.nacs_server(ip, nacs_server, nacs_key)
                            results[ip] = result.json

                        elif brand == 'tp-link':
                            result = binary_commands.TplinkDevice.nacs_server(ip, nacs_server, nacs_key)
                            results[ip] = result.json

                        elif brand == 'dcn':
                            result = binary_commands.DCNDevice.nacs_server(ip, nacs_server, nacs_key)
                            results[ip] = result.json

                        else:
                            results[ip] = jsonify({"error:": f"Unsupported vendor '{vendor_name}'"})

                    else:
                        results[ip] = jsonify({"error:": f"Unsupported vendor '{vendor_name}'"}), 500

                else:
                    results[ip] = jsonify({"error:": f"Vendor name not found for vendor_fk {vendor_fk}"}), 500

            else:
                results[ip] = jsonify({"error:": "IP address not found in the database"}), 500

        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@config.route('/conf_auth_default', methods=['POST'])
@token_required
def conf_auth_default(current_user):

    allowed_roles = ["S_admin", "D_admin", "RO_admin"]
    if not current_user.roles in allowed_roles:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:
        data = request.json
        ip_addresses = data.get('ip_addresses', [])
        results = {}

        # Log for delete vlan
        log_entry = Log(
            username=current_user.username,
            last_name=current_user.familiya,
            district=current_user.dist,
            roles=current_user.roles,
            actions=f"{current_user.username} {current_user.familiya} tomonidan {ip_addresses} qurilmasi xavfsizlik "
                    f"funktsiyalari boshlag'ich holatda sozlandi",
            times=datetime.now(),
            dates=datetime.today().date()
        )
        db.session.add(log_entry)
        db.session.commit()

        for ip in ip_addresses:
            record = get_one(ip)

            if record:
                vendor_fk = record.vendor_fk
                vendor_name = get_vendor_name(vendor_fk)  # Fetch vendor_name from the vendor table based on vendor_fk

                if vendor_name:
                    brand = vendor_models.get(vendor_name.upper())  # Convert vendor name to lowercase for matching
                    if brand:
                        if brand == 'snr':
                            result = binary_commands.NagDevice.auth_default(ip)
                            results[ip] = result.json

                        elif brand == 'tp-link':
                            result = binary_commands.TplinkDevice.auth_default(ip)
                            results[ip] = result.json

                        elif brand == 'dcn':
                            result = binary_commands.DCNDevice.auth_default(ip)
                            results[ip] = result.json

                        else:
                            results[ip] = jsonify({"error:": f"Unsupported vendor '{vendor_name}'"})

                    else:
                        results[ip] = jsonify({"error:": f"Unsupported vendor '{vendor_name}'"}), 500

                else:
                    results[ip] = jsonify({"error:": f"Vendor name not found for vendor_fk {vendor_fk}"}), 500

            else:
                results[ip] = jsonify({"error:": "IP address not found in the database"}), 500

        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@config.route('/conf_add_user', methods=['POST'])
@token_required
def conf_add_user(current_user):
    allowed_roles = ["S_admin", "D_admin", "RO_admin"]
    if not current_user.roles in allowed_roles:
        return jsonify({'message': 'Sizning Huquqlaringiz cheklangan'}), 401

    try:
        data = request.json
        new_username = data['new_username']
        new_password = data['new_password']
        privilage = data['privilage']
        ip_addresses = data['ip_addresses']
        results = {}

        # Log for create user
        log_entry = Log(
            username=current_user.username,
            last_name=current_user.familiya,
            district=current_user.dist,
            roles=current_user.roles,
            actions=f"{current_user.username} {current_user.familiya} tomonidan {ip_addresses} qurilmasida {new_username} useri yaratildi"
                    f" funksiyalari boshlang'ich holatda sozlandi",
            times=datetime.now(),
            dates=datetime.today().date()
        )
        db.session.add(log_entry)
        db.session.commit()

        for ip in ip_addresses:
            record = get_one(ip)
            if record:
                vendor_fk = record.vendor_fk
                vendor_name = get_vendor_name(vendor_fk)

                if vendor_name:
                    brand = vendor_models.get(vendor_name.upper())
                    if brand:
                        if brand == 'snr':
                            response = binary_commands.NagDevice.add_user(ip, new_username, new_password, privilage)
                            results[ip] = response.json

                        elif brand == 'tp-link':
                            response = binary_commands.TplinkDevice.add_user(ip, new_username, new_password, privilage)
                            results[ip] = response.json

                        elif brand == 'dcn':
                            response = binary_commands.DCNDevice.add_user(ip, new_username, new_password, privilage)
                            results[ip] = response.json

                        else:
                            results[ip] = jsonify({"error:": f"Unsupported vendor '{vendor_name}'"}), 500

                    else:
                        results[ip] = jsonify({"error:": f"Unsupported vendor '{vendor_name}'"}), 500

                else:
                    results[ip] = jsonify({"error:": f"Vendor name not found for vendor_fk '{vendor_fk}'"}), 500

            else:
                results[ip] = jsonify({"error:": "IP address not found in the database"}), 500

        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@config.route('/conf_delete_user', methods=['POST'])
@token_required
def conf_delete_user(current_user):

    allowed_roles = ["S_admin", "D_admin", "RO_admin"]
    if not current_user.roles in allowed_roles:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:
        data = request.json
        new_username = data['new_username']
        ip_addresses = data['ip_addresses']
        results = {}

        # Log for create user

        log_entry = Log(
            username=current_user.ism,
            last_name=current_user.familiya,
            district=current_user.dist,
            roles=current_user.roles,
            actions=f"{current_user.username} {current_user.familiya} tomonidan {ip_addresses} qurilmasida {new_username} useri o'chirildi"
                    f"funktsiyalari boshlag'ich holatda sozlandi",
            times=datetime.now(),
            dates=datetime.today().date()
        )
        db.session.add(log_entry)
        db.session.commit()

        for ip in ip_addresses:
            record = get_one(ip)

            if record:
                vendor_fk = record.vendor_fk
                vendor_name = get_vendor_name(vendor_fk)

                if vendor_name:
                    brand = vendor_models.get(vendor_name.upper())
                    if brand:
                        if brand == 'snr':
                            response = binary_commands.NagDevice.delete_user(ip, new_username)
                            results[ip] = response.json

                        elif brand == 'tp-link':
                            response = binary_commands.TplinkDevice.delete_user(ip, new_username)
                            results[ip] = response.json

                        elif brand == 'dcn':
                            response = binary_commands.DCNDevice.delete_user(ip, new_username)
                            results[ip] = response.json

                        else:
                            results[ip] = jsonify({"error:": f"Unsupported vendor '{vendor_name}'"}), 500

                    else:
                        results[ip] = jsonify({"error:": f"Unsupported vendor '{vendor_name}'"}), 500

                else:
                    results[ip] = jsonify({"error:": f"Vendor name not found for vendor_fk '{vendor_fk}'"}), 500

            else:
                results[ip] = jsonify({"error": "IP address not found in the database"}), 500

        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@config.route('/conf_ntp_server', methods=['POST'])
@token_required
def conf_ntp_server(current_user):

    allowed_roles = ["S_admin", "D_admin", "RO_admin"]
    if not current_user.roles in allowed_roles:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:
        data = request.json
        ntp_server_primary = data.get('ntp_server_primary')
        ntp_server_secondary = data.get('ntp_server_secondary')
        ip_addresses = data.get('ip_addresses', [])
        results = {}

        # Log for create user
        log_entry = Log(
            username=current_user.username,
            last_name=current_user.familiya,
            district=current_user.dist,
            roles=current_user.roles,
            actions=f"{current_user.username} {current_user.familiya} tomonidan {ip_addresses} qurilmasidagi vaqt sozlamalari {ntp_server_primary} va "
                    f"{ntp_server_secondary} serverlariga yo'naltirildi ",
            times=datetime.now(),
            dates=datetime.today().date()
        )
        db.session.add(log_entry)
        db.session.commit()


        for ip in ip_addresses:
            record = get_one(ip)

            if record:
                vendor_fk = record.vendor_fk
                vendor_name = get_vendor_name(vendor_fk)

                if vendor_name:
                    brand = vendor_models.get(vendor_name.upper())
                    if brand:
                        if brand == 'snr':
                            response = binary_commands.NagDevice.ntp_config(ip, ntp_server_primary, ntp_server_secondary)
                            results[ip] = response.json

                        elif brand == 'tp-link':
                            response = binary_commands.TplinkDevice.ntp_config(ip, ntp_server_primary, ntp_server_secondary)
                            results[ip] = response.json

                        elif brand == 'dcn':
                            response = binary_commands.DCNDevice.ntp_config(ip, ntp_server_primary, ntp_server_secondary)
                            results[ip] = response.json

                        else:
                            results[ip] = jsonify({"error": f"Unsupported vendor '{vendor_name}'"}), 500

                    else:
                        results[ip] = jsonify({"error:": f"Unsupported vendor '{vendor_name}'"}), 500

                else:
                    results[ip] = jsonify({"error": f"Vendor name not found for vendor_fk '{vendor_fk}'"}), 500

            else:
                results[ip] = jsonify({"error": "IP address not found in the database"}), 500

        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@config.route('/conf_interface_auto', methods=['POST'])
@token_required
def conf_interface_auto(current_user):

    allowed_roles = ["S_admin", "D_admin", "RO_admin"]
    if not current_user.roles in allowed_roles:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:

        data = request.json
        ip_addresses = data['ip_addresses']
        vlan_id = data['vlan_id']
        vlan_name = data['vlan_name']
        required_port = data['required_port']
        descriptions = data['descriptions']
        results = {}

        for ip in ip_addresses:
            record = get_one(ip)

            if record:
                vendor_fk = record.vendor_fk
                vendor_name = get_vendor_name(vendor_fk)

                if vendor_name:
                    brand = vendor_models.get(vendor_name.upper())
                    if brand:
                        if brand == 'snr':
                            response = binary_commands.NagDevice.configure_vlan_and_ports(ip, vlan_id, vlan_name, required_port, descriptions)
                            results[ip] = response.json

                        elif brand == 'tp-link':
                            response = binary_commands.TplinkDevice.configure_vlan_and_ports_tp(ip, vlan_id, vlan_name, required_port, descriptions)
                            results[ip] = response.json

                        elif brand == 'dcn':
                            response = binary_commands.DCNDevice.configure_vlan_and_ports(ip, vlan_id, vlan_name, required_port, descriptions)
                            results[ip] = response.json

                        else:
                            results[ip] = jsonify({"error": f"Unsupported vendor '{vendor_name}'"}), 500

                    else:
                        results[ip] = jsonify({"error:": f"Unsupported vendor '{vendor_name}'"}), 500

                else:
                    results[ip] = jsonify({"error": f"Vendor name not found for vendor_fk '{vendor_fk}'"}), 500

            else:
                results[ip] = jsonify({"error": "IP address not found in the database"}), 500

        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

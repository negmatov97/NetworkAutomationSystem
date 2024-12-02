from flask import jsonify, request, Flask, Blueprint, send_from_directory, url_for, send_file
from dotenv import load_dotenv
from db_config import db, UniversalTable, Backup_list, DeviceBackup, District, Vendor, Section
import paramiko
import time
import os
from backup_auto.backup_etalons import saving_db
from gen_token import token_required
from concurrent.futures import ThreadPoolExecutor, as_completed


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

user = "Negmatov"
passw = "admin123"
backup = Blueprint('backup', __name__)

db.init_app(app)

tftp_folder = os.path.join(os.path.dirname(__file__), 'tftp-server')



# Ensure the TFTP server folder exists
if not os.path.exists(tftp_folder):
    os.makedirs(tftp_folder)

@backup.route('/copy_data', methods=['POST'])
def copy_data():
    try:
        # Get the id from the request
        data = request.get_json()
        id_to_copy = data.get('id')
        priority = data.get('priority', 1)

        # Fetch data from the source table based on the specified id
        source_data = UniversalTable.query.filter_by(id=id_to_copy).first()

        if source_data:
            # Check if ip_add already exists in the destination table
            existing_data = Backup_list.query.filter_by(ip_add=source_data.ip_add).first()

            if existing_data:
                # Update the priority of the existing record
                existing_data.priority = priority
                db.session.commit()
                return jsonify({"message": "Priority updated successfully"}), 200
            else:
                # Create an instance of the destination table and copy the data
                destination_data = Backup_list(
                    okrug=source_data.district_fk,
                    qism=source_data.section_fk,
                    hostname=source_data.hostname,
                    ip_add=source_data.ip_add,
                    vendor=source_data.vendor_fk,
                    priority=priority
                )

                # Add the instance to the session and commit changes
                db.session.add(destination_data)
                db.session.commit()
                return jsonify({"message": "Data copied successfully"}), 200
        else:
            return jsonify({"error": "Data not found for the specified id"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@backup.route('/perform_backup', methods=['POST'])
def perform_backup():
    def backup_device(device_id, ip_address_without_brackets, username, password, tftp_folder, tftp_server_ip):
        result = {"id": device_id, "ip_address": ip_address_without_brackets}
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh_client.connect(hostname=ip_address_without_brackets, username=username, password=password)

            # Send commands and get backup data
            ssh_session = ssh_client.invoke_shell()
            ssh_session.send("enable\r")
            time.sleep(5)
            ssh_session.send("terminal length 0\r")
            time.sleep(5)
            ssh_session.send("show running-config\r")
            time.sleep(5)

            # Read the output
            output = ssh_session.recv(65535).decode("utf-8")

            # Save the output to the TFTP server folder
            filename = f"{ip_address_without_brackets}.txt"
            file_path = os.path.join(tftp_folder, filename)
            with open(file_path, "w") as file:
                file.write(output)

            result["message"] = "Backup successful!"
            result["output_file"] = f"tftp://{tftp_server_ip}/{filename}"

            # Save to database
            saving_db.save_backup_to_database(ip_address_without_brackets, file_path)

        except paramiko.AuthenticationException:
            result["message"] = "Authentication failed"
        except paramiko.SSHException:
            result["message"] = "Unable to establish SSH connection"
        except Exception as e:
            result["message"] = f"Error occurred: {str(e)}"
        finally:
            ssh_client.close()

        return result

    try:
        # Fetch the IDs from the request body
        data = request.get_json()
        ids = data.get('id', [])

        if not ids:
            return jsonify({"error": "No IDs provided"}), 400

        backup_results = []

        username = user  # Replace with your SSH username or fetch from environment variables
        password = passw  # Replace with your SSH password or fetch from environment variables
        tftp_server_ip = "127.0.0.1"  # Change to your TFTP server IP

        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_device = {}
            for device_id in ids:
                # Fetch ip_add from Backup_list based on the provided id
                record = UniversalTable.query.filter_by(id=device_id).first()
                if not record or not record.ip_add:
                    backup_results.append({"id": device_id, "message": "Invalid ID or IP address not found"})
                    continue

                ip_address = record.ip_add
                ip_address_without_brackets = ip_address.replace("[", "").replace("]", "")
                future = executor.submit(backup_device, device_id, ip_address_without_brackets, username, password,
                                         tftp_folder, tftp_server_ip)
                future_to_device[future] = device_id

            for future in as_completed(future_to_device):
                try:
                    result = future.result()
                    backup_results.append(result)
                except Exception as e:
                    backup_results.append({"id": future_to_device[future], "message": f"Error occurred: {str(e)}"})

        return jsonify({"backups": backup_results}), 200

    except Exception as e:
        # Log the exception and return an error response
        return jsonify({"error": str(e)}), 500



#############################################################
################ Backup List TABLE###########################
#############################################################
@backup.route('/backup_list', methods=['GET'])
@token_required
def get_backup_list(current_user):

    if current_user.roles != "S_admin":
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401
    try:
        priority_map = {
            1: "1/1",
            2: "2/1",
            7: "7/1",
            15: "15/1",
            30: "30/1"
        }

        # Query all records from the backup_list table
        backup_list_data = (
            db.session.query(
                Backup_list.id,
                District.short.label('district_name'),
                Section.name.label('section_name'),
                Backup_list.hostname,
                Backup_list.ip_add,
                Vendor.name.label('vendor_name'),
                Backup_list.priority
            )
            .join(District, Backup_list.okrug == District.id)
            .join(Section, Backup_list.qism == Section.id)
            .join(Vendor, Backup_list.vendor == Vendor.id)
            .all()
        )

        # Convert the data to a list of dictionaries using list comprehension
        data_list = [
            {
                'id': item.id,
                'okrug': item.district_name,
                'qism': item.section_name,
                'hostname': item.hostname,
                'ip_add': item.ip_add,
                'vendor': item.vendor_name,
                'priority': priority_map.get(item.priority, f"{item.priority}/1")
            }
            for item in backup_list_data
        ]

        return jsonify(data_list), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@backup.route('/backup_list_edit', methods=['POST'])
@token_required
def edit_backup_priority(current_user):

    if current_user.roles != "S_admin":
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'})

    data = request.get_json()
    record_ids = data.get('id')
    new_priority = data.get('priority')

    if not record_ids or not new_priority:
        return jsonify({'error': "ID va yangi ustuvorlik talab qilinadi"})

    if not isinstance(record_ids, list):
        record_ids = [record_ids]

    try:
        for record_id in record_ids:
            backup_record = Backup_list.query.filter_by(id=record_id).first()
            if not backup_record:
                continue
            backup_record.priority = new_priority

        db.session.commit()
        return jsonify({'message': "Ustuvorlik muvaffaqiyatli yangilandi"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)})


@backup.route('/backup_list_delete', methods=['DELETE'])
@token_required
def delete_backup_record(current_user):

    if current_user.roles != "S_admin":
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'})

    data = request.get_json()
    record_ids = data.get('id')

    if not record_ids:
        return jsonify({'error': "ID talab qilinadi"})

    if not isinstance(record_ids, list):
        record_ids = [record_ids]

    try:
        for record_id in record_ids:
            backup_record = Backup_list.query.filter_by(id=record_id).first()
            if not backup_record:
                continue
            db.session.delete(backup_record)

        db.session.commit()
        return jsonify({'message': "Yozuvlar muvaffaqiyatli o'chirildi"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)})



#################################################################################
########################## Device Backup TABLE ##################################
#################################################################################

@backup.route('/device_backups', methods=['GET'])
@token_required
def get_device_backups(current_user):
    try:

        if current_user.roles != "S_admin":
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'})

        # Query all records from the DeviceBackup table
        backups = DeviceBackup.query.all()

        # Convert the data to a list of dictionaries
        data_list = [
            {
                'id': backup.id,
                'file_ip': backup.file_ip,
                'data_time': backup.data_time.strftime("%d-%m-%Yy %H:%Mm")
            }
            for backup in backups
        ]

        return jsonify(data_list)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@backup.route('/devbackup_downl', methods=['POST'])
def download_backup():
    try:
        data = request.get_json()
        ids = data.get('id', [])

        if not ids:
            return jsonify({"error": "No IDs provided"}), 400

        if isinstance(ids, int):  # If a single ID is provided
            ids = [ids]

        backups = DeviceBackup.query.filter(DeviceBackup.id.in_(ids)).all()

        if not backups:
            return jsonify({"error": "No backups found for the provided IDs"}), 404

        response = {
            "files": []
        }

        for backup in backups:
            file_name = f"{backup.file_ip}.txt"
            file_content = backup.files.decode('utf-8', errors='ignore')  # Decoding binary content to text
            response["files"].append({
                "file_name": file_name,
                "file_content": file_content
            })

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@backup.route('/devbackup_delete', methods=['DELETE'])
@token_required
def delete_device_backup(current_user):
    allowed_roles = {"S_admin", "D_admin", "RO_admin"}
    if current_user.roles not in allowed_roles:
        return jsonify({'message': "Sizning Huqularingiz cheklangan"}), 401

    data = request.get_json()
    record_ids = data.get('id')

    if not record_ids:
        return jsonify({'error': "ID talab qilinadi"}), 400

    if not isinstance(record_ids, list):
        record_ids = [record_ids]

    try:
        for record_id in record_ids:
            backup_record = DeviceBackup.query.filter_by(id=record_id).first()
            if not backup_record:
                continue
            db.session.delete(backup_record)

        db.session.commit()
        return jsonify({'message': "Yozuvlar muvaffaqiyatli o'chirildi"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, jsonify
from db_config import db, DeviceBackup
import paramiko
import time
from datetime import datetime
import pytz

tz = pytz.timezone('Asia/Tashkent')



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:toor@127.0.0.1/postgres"
db.init_app(app)


tftp_folder = os.path.join(os.path.dirname(__file__), 'tftp-server')

commands= ["enable", "terminal length 0", "show running-config"]


class devices_nag:
    @staticmethod
    def connect_and_execute_command(hostname, username=os.environ.get('BACKUPUSER'),
                                    password=os.environ.get('BACKUPPASS')):
        commands = ["enable", "terminal length 0", "show running-config"]

        with app.app_context():
            # Create an SSH client
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            try:
                # Connect to the network device
                ssh_client.connect(hostname, username=username, password=password, timeout=10)

                # Create an SSH shell
                ssh_shell = ssh_client.invoke_shell()

                # Wait for the shell to be ready
                time.sleep(1)

                # Send each command to the shell
                for command in commands:
                    ssh_shell.send(command + "\n")
                    # Wait for the command to be executed
                    time.sleep(2)

                # Read the output
                output = ssh_shell.recv(65535).decode('utf-8')

                # Ensure the tftp-folder exists
                tftp_folder = os.path.join(os.path.dirname(__file__), 'tftp-server')
                os.makedirs(tftp_folder, exist_ok=True)

                # Save the output to a file
                filename = f"{hostname}.txt"
                file_path = os.path.join(tftp_folder, filename)
                with open(file_path, 'w') as file:
                    file.write(output)

                # Upload backup to database
                saving_db.save_backup_to_database(hostname, file_path)

            except Exception as e:
                print(f"Error connecting to {hostname}: {str(e)}")

            finally:
                # Close the SSH connection
                ssh_client.close()

    @staticmethod
    def connect_to_multiple_devices(hostnames, max_connections=5):
        with ThreadPoolExecutor(max_workers=max_connections) as executor:
            future_to_hostname = {executor.submit(devices_nag.connect_and_execute_command, hostname): hostname for
                                  hostname in hostnames}
            for future in as_completed(future_to_hostname):
                hostname = future_to_hostname[future]
                try:
                    future.result()
                except Exception as e:
                    print(f"Error processing {hostname}: {str(e)}")


class saving_db:
    @staticmethod
    def save_backup_to_database(hostname, file_path):
        with app.app_context():
            try:
                # Read the content of the file as binary
                with open(file_path, 'rb') as file:
                    file_content = file.read()

                current_time = datetime.now(tz)

                # Check if an entry with the same file_ip exists
                existing_backup = DeviceBackup.query.filter_by(file_ip=hostname).first()

                if existing_backup:
                    # Update the existing entry
                    existing_backup.file_name = file_path
                    existing_backup.files = file_content
                    existing_backup.data_time = current_time
                    message = f"Backup updated in database for {hostname}"
                    print(f"update")
                else:
                    # Create a new entry
                    new_backup = DeviceBackup(file_ip=hostname, file_name=file_path, files=file_content)
                    db.session.add(new_backup)
                    message = f"Backup saved to database for {hostname}"

                db.session.commit()
                print({"message": message})

            except Exception as e:
                db.session.rollback()
                print({"Error": str(e)})


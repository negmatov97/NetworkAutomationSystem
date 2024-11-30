import os
from flask import Flask
import yaml
from flask import jsonify, Blueprint
from flask_cors import CORS
from dotenv import load_dotenv
from db_config import db, Backup_list, Vendor
from backup_auto.backup_etalons import devices_nag

load_dotenv()

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
backup = Blueprint('backup', __name__)
CORS(app)

db.init_app(app)

def get_one(ip):
    record = Backup_list.query.filter_by(ip_add=ip).first()
    return record

with open('device.yaml', 'r') as file:
    device_models = yaml.safe_load(file)

vendor_models = {model['model']: brand for brand, models in device_models.items() for model in models}

def get_vendor_name(vendor_fk):
    try:
        vendor = Vendor.query.filter_by(id=vendor_fk).first()
        return vendor.name if vendor else None
    except Exception as e:
        print(str(e))
        return None

def backup_function(priority):
    with app.app_context():
        ip_addresses = db.session.query(Backup_list.ip_add).filter(Backup_list.priority == priority).all()

        for ip_row in ip_addresses:
            ip = ip_row[0]
            record = get_one(ip)

            if record:
                vendor_fk = record.vendor
                vendor_name = get_vendor_name(vendor_fk)

                if vendor_name:
                    brand = vendor_models.get(vendor_name)

                    if brand in ['tp-link', 'snr', 'cisco', 'qtech', 'dcn', 'hp', 'eltex']:
                        devices_nag.connect_and_execute_command(ip)
                    else:
                        print(f"Error: Unsupported vendor '{vendor_name}'")
                else:
                    print(f"Error: Vendor name not found for vendor_fk '{vendor_fk}'")
            else:
                print(f"Error: IP address not found in the database")

        return jsonify({'message': 'success'}), 200

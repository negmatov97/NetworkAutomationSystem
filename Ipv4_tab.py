from flask import Flask, Blueprint, request, jsonify, render_template
import psycopg2.extras
from explator import DistrictHelper
from gen_token import token_required
from db_config import db, UniversalTable, District, Section, Vlan, Vendor, Log
from datetime import datetime


app = Flask (__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:toor@192.168.202.46/postgres'

frist_api = Blueprint('frist_api', __name__)

db.init_app(app)


DB_HOST = "localhost"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "toor"

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)

##############################################################################################
#                         Asosiy ma'lumotlar (Universal_table)                               #
##############################################################################################

@frist_api.route('/data', methods=['GET'])
@token_required
def get_data(current_user):
    try:
        if current_user.roles == "S_admin" and current_user.dist == 10:
            # Fetch all data
            data = UniversalTable.query.all()
        elif 1 <= current_user.dist <= 8:
            # Fetch data filtered by district_fk
            data = UniversalTable.query.filter_by(district_fk=current_user.dist).all()
        else:
            return jsonify({'message': 'Insufficient privileges'}), 401

        # Serialize data
        data_list = []
        for item in data:
            district = District.query.get(item.district_fk)
            section = Section.query.get(item.section_fk)
            vlan = Vlan.query.get(item.vlan_fk)
            vendor = Vendor.query.get(item.vendor_fk)
            row_data = {
                'id': item.id,
                'district_fk': item.district_fk,
                'district_short': district.short if district else None,
                'section_fk': item.section_fk,
                'section_name': section.name if section else None,
                'vlan_fk': item.vlan_fk,
                'vlan_name': vlan.name if vlan else None,
                'vendor_fk': item.vendor_fk,
                'vendor_name': vendor.name if vendor else None,
                'hostname': item.hostname,
                'ip_add': item.ip_add,
                'mask': item.mask,
                'mac_add': item.mac_add
            }
            data_list.append(row_data)
        return jsonify(data_list)
    except Exception as e:
        # Handle exceptions and return appropriate error response
        return jsonify({'error': str(e)}), 500


@frist_api.route('/data_mgmt', methods=['GET'])
@token_required
def get_data_mgmt(current_user):
    try:
        if current_user.roles == "S_admin" and current_user.dist == 10:
            # Fetch all data
            data = UniversalTable.query.all()
        elif 1 <= current_user.dist <= 8:
            # Fetch data filtered by district_fk
            data = UniversalTable.query.filter_by(district_fk=current_user.dist).all()
        else:
            return jsonify({'message': 'Insufficient privileges'}), 401

        # Serialize data
        data_list = []
        for item in data:
            district = District.query.get(item.district_fk)
            section = Section.query.get(item.section_fk)
            vlan = Vlan.query.get(item.vlan_fk)
            vendor = Vendor.query.get(item.vendor_fk)

            # Filter by vlan_name "MGMT_1" or "MGMT_2"
            if vlan and vlan.name in ["MGMT_1", "MGMT_2"]:
                row_data = {
                    'id': item.id,
                    'district_fk': item.district_fk,
                    'district_short': district.short if district else None,
                    'section_fk': item.section_fk,
                    'section_name': section.name if section else None,
                    'vlan_fk': item.vlan_fk,
                    'vlan_name': vlan.name if vlan else None,
                    'vendor_fk': item.vendor_fk,
                    'vendor_name': vendor.name if vendor else None,
                    'hostname': item.hostname,
                    'ip_add': item.ip_add,
                    'mask': item.mask,
                    'mac_add': item.mac_add
                }
                data_list.append(row_data)

        return jsonify(data_list)
    except Exception as e:
        # Handle exceptions and return appropriate error response
        return jsonify({'error': str(e)}), 500


@frist_api.route('/data/<int:id>', methods=['GET'])
@token_required
def get_data_one(current_user, id):
    try:
        if current_user.roles == "S_admin":
            # Fetch data by id
            data = UniversalTable.query.filter_by(id=id).first()
        elif 1 <= current_user.dist <= 8:
            # Fetch data filtered by district_fk and id
            data = UniversalTable.query.filter_by(district_fk=current_user.dist, id=id).first()
        else:
            return jsonify({'message': 'Insufficient privileges'}), 401

        if not data:
            return jsonify({'message': 'Data not found'}), 404

        # Fetch related data
        district = District.query.get(data.district_fk)
        section = Section.query.get(data.section_fk)
        vlan = Vlan.query.get(data.vlan_fk)
        vendor = Vendor.query.get(data.vendor_fk)

        # Serialize data
        row_data = {
            'id': data.id,
            'district_fk': data.district_fk,
            'district_short': district.short if district else None,
            'section_fk': data.section_fk,
            'section_name': section.name if section else None,
            'vlan_fk': data.vlan_fk,
            'vlan_name': vlan.name if vlan else None,
            'vendor_fk': data.vendor_fk,
            'vendor_name': vendor.name if vendor else None,
            'hostname': data.hostname,
            'ip_add': data.ip_add,
            'mask': data.mask,
            'mac_add': data.mac_add
        }

        return jsonify(row_data)
    except Exception as e:
        # Handle exceptions and return appropriate error response
        return jsonify({'error': str(e)}), 500

from flask import request, jsonify

@frist_api.route('/data_more', methods=['POST'])
@token_required
def get_dates(current_user):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Invalid request'}), 400

        # Extract ids from the JSON payload
        ids = data.get('id')
        if ids is None:
            return jsonify({'message': 'ID(s) required'}), 400

        if not isinstance(ids, list):
            ids = [ids]

        if current_user.roles == "S_admin":
            # Fetch data by ids
            records = UniversalTable.query.filter(UniversalTable.id.in_(ids)).all()
        elif 1 <= current_user.dist <= 8:
            # Fetch data filtered by district_fk and ids
            records = UniversalTable.query.filter(UniversalTable.district_fk == current_user.dist, UniversalTable.id.in_(ids)).all()
        else:
            return jsonify({'message': 'Insufficient privileges'}), 401

        if not records:
            return jsonify({'message': 'Data not found'}), 404

        # Fetch related data and serialize
        row_data_list = []
        for record in records:
            district = District.query.get(record.district_fk)
            section = Section.query.get(record.section_fk)
            vlan = Vlan.query.get(record.vlan_fk)
            vendor = Vendor.query.get(record.vendor_fk)

            row_data = {
                'id': record.id,
                'district_fk': record.district_fk,
                'district_short': district.short if district else None,
                'section_fk': record.section_fk,
                'section_name': section.name if section else None,
                'vlan_fk': record.vlan_fk,
                'vlan_name': vlan.name if vlan else None,
                'vendor_fk': record.vendor_fk,
                'vendor_name': vendor.name if vendor else None,
                'hostname': record.hostname,
                'ip_add': record.ip_add,
                'mask': record.mask,
                'mac_add': record.mac_add
            }
            row_data_list.append(row_data)

        return jsonify(row_data_list)
    except Exception as e:
        # Handle exceptions and return appropriate error response
        return jsonify({'error': str(e)}), 500


@frist_api.route('/data', methods=['POST'])
@token_required
def insert_data(current_user):

    if current_user.roles not in ["S_admin", "D_admin"]:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:
        data = request.get_json()

        # Conditionally set district_fk based on current_user.priv
        if current_user.roles == "S_admin":
            district_value = data['district_fk']
        else:
            district_value = current_user.dist

        # Create a new record in the universal_table
        new_data = UniversalTable(
            district_fk=district_value,
            section_fk=data['section_fk'],
            vlan_fk=data['vlan_fk'],
            vendor_fk=data['vendor_fk'],
            hostname=data['hostname'],
            ip_add=data['ip_add'],
            mask=data['mask'],
            mac_add=data['mac_add']
       )

        # Log the action
        log_entry = Log(
            username=current_user.ism,
            last_name=current_user.familiya,
            district=DistrictHelper.get_district_short(current_user.dist),
            roles=current_user.roles,
            actions=f"Ma'lumotlar bazasiga HOSTNAME={data['hostname']}, IP MANZIL={data['ip_add']}, MAC-ADDRESS={data['mac_add']} qurilma ma'lumotlari kiritildi",
            times=datetime.now(),
            dates=datetime.today().date()
        )

        db.session.add(new_data)
        db.session.add(log_entry)

        db.session.commit()

        return jsonify({"message": "Ma'lumotlar muvofaqqiyatli ro'yxatgaolindi", "success": True}), 201

    except Exception as e:
        return jsonify({"xatolik": str(e), "success": False}), 500




@frist_api.route('/data/<int:id>', methods=['DELETE'])
@token_required
def delete_row(current_user, id):
    try:
        row_to_delete = UniversalTable.query.get(id)

        if not row_to_delete:
            return jsonify({'xatolik': f"{id} Ma'lumot topilmadi!", "success": False}), 404

        # Check if the user has the required role
        if current_user.roles not in ["S_admin", "D_admin"]:
            return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

        # If the user is a "D_admin," check if they have permission to delete the row
        if current_user.roles == "D_admin" and current_user.dist != row_to_delete.district_fk:
            return jsonify({'message': "Sizda ma'lumotni o'chirish uchun huquq yo'q"}), 401

        # Log the action before deleting the row
        log_entry = Log(
            username=current_user.ism,
            last_name=current_user.familiya,
            district=DistrictHelper.get_district_short(current_user.dist),
            roles=current_user.roles,
            actions=f"Ma'lumotlar bazasidan HOSTNAME={row_to_delete.hostname}, IP ADDRESS={row_to_delete.ip_add}, MAC-ADDRESS={row_to_delete.mac_add} qurilma ma'lumotlari o'chirildi",
            times=datetime.now(),
            dates = datetime.today().date()
        )

        db.session.add(log_entry)

        db.session.delete(row_to_delete)
        db.session.commit()

        return jsonify({'message': f"{id} Ma'lumot o'chirildi!", "success": True}), 200

    except Exception as e:
        return jsonify({'xatolik': str(e), "success": False}), 500


@frist_api.route('/data/<int:id>', methods=['PUT'])
@token_required
def update_record(current_user, id):

    allowed_roles = ["S_admin", "D_admin"]

    if current_user.roles not in allowed_roles:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:
        record = UniversalTable.query.get(id)
        old_record=record.ip_add

        if not record:
            return jsonify({'message': "Ma'lumot topilmadi!"}), 404

        if current_user.roles == "D_admin" and current_user.dist != record.district_fk:
            return jsonify({'message': "Sizda ma'lumotni o'zgartirish uchun huquq yo'q"}), 401

        if 'district_fk' in request.json:
            record.district_fk = request.json['district_fk']
        if 'section_fk' in request.json:
            record.section_fk = request.json['section_fk']
        if 'vlan_fk' in request.json:
            record.vlan_fk = request.json['vlan_fk']
        if 'vendor_fk' in request.json:
            record.vendor_fk = request.json['vendor_fk']
        if 'hostname' in request.json:
            record.hostname = request.json['hostname']
        if 'ip_add' in request.json:
            record.ip_add = request.json['ip_add']
        if 'mask' in request.json:
            record.mask = request.json['mask']
        if 'mac_add' in request.json:
            record.mac_add = request.json['mac_add']

        log_entry = Log(
            username=current_user.ism,
            last_name=current_user.familiya,
            district=DistrictHelper.get_district_short(current_user.dist),
            roles=current_user.roles,
            actions=f"Ma'lumotlar bazasida  {old_record} qurilmasi ma'lumotlari o'zgartirildi",
            times=datetime.now(),
            dates = datetime.today().date()
        )

        db.session.add(log_entry)

        # Commit the changes to the database
        db.session.commit()

        return jsonify({'message': "Ma'lumot o'zgartirildi!", "success": True}), 200

    except Exception as e:
        return jsonify({'error': str(e), "success": False}), 500



@frist_api.route('/district_section_data/<int:id>', methods=['GET'])
@token_required
def district_section_data(current_user, id):

    # Define allowed roles
    allowed_roles = ["S_admin", "D_admin", "RO_admin"]

    # Check if the user's role is not in the allowed roles
    if not current_user.roles in allowed_roles:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:
        # If the user is an "S_admin," retrieve all sections where okrug_fk matches the provided District ID
        if current_user.roles == "S_admin":
            matching_sections = db.session.query(Section).filter(Section.okrug_fk == id).all()
        # If the user is a "D_admin" or "RO_admin," retrieve sections where okrug_fk matches current_user.dist
        else:
            matching_sections = db.session.query(Section).filter(Section.okrug_fk == current_user.dist).all()

        # Create a list of dictionaries to store the id and name columns from matching sections
        section_data = [{"id": section.id, "name": section.name} for section in matching_sections]

        # Return the section_data as JSON
        return jsonify(section_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


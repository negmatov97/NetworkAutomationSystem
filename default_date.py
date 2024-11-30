from flask import Flask, Blueprint, request, jsonify, render_template
import psycopg2.extras
from sqlalchemy import func
from gen_token import token_required
from db_config import db, District, Section, Vlan, Vendor, Log
from datetime import datetime


app = Flask (__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:toor@192.168.202.46/postgres'

default_api = Blueprint('default_api', __name__)

db.init_app(app)


DB_HOST = "localhost"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "toor"

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)

##############################################################################################
#                             Dastlabki ma'lumotlar (District)                               #
##############################################################################################
@default_api.route('/districts', methods=['GET'])
#@token_required
def get_districts():

    # allowed_roles = ["S_admin", "D_admin", "RO_admin"]
    # if not current_user.roles in allowed_roles:
    #     return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:
        districts = District.query.all()
        district_list = [{"id": district.id, "name": district.name, "short": district.short} for district in districts]
        return jsonify(district_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@default_api.route('/districts/<int:id>', methods=['GET'])
@token_required
def get_district_by_id(current_user, id):

    if current_user.roles != "S_admin" or current_user.dist != 10:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:
        district = District.query.get(id)
        if not district:
            return jsonify({'message': 'District not found'}), 404

        district_data = {
            "id": district.id,
            "name": district.name,
            "short": district.short
        }
        return jsonify(district_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@default_api.route('/districts', methods=['POST'])
@token_required
def insert_district(current_user):

    if current_user.roles != "S_admin" or current_user.dist != 10:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:
        data = request.get_json()
        new_district = District(name=data['name'], short=data['short'])
        db.session.add(new_district)
        db.session.commit()

        # Log the action
        log_entry = Log(
            username=current_user.username,
            last_name=current_user.familiya,
            district=current_user.dist,
            roles=current_user.roles,
            actions=f"{current_user.username} {current_user.familiya} tomonidan Boshqaruv bo'g'ini uchun {data['name']} kiritildi",
            times=datetime.now(),
            dates = datetime.today().date()
        )
        db.session.add(log_entry)
        db.session.commit()

        return jsonify({"message": "Ma'lumot muvoffaqiyatli kiritildi!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@default_api.route('/districts/<int:id>', methods=['PUT'])
@token_required
def update_district(current_user, id):

    if current_user.roles != "S_admin" or current_user.dist != 10:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:
        data = request.get_json()
        district_to_update = District.query.get(id)
        if district_to_update:
            old_district_name=district_to_update.name
            old_district_short=district_to_update.short
            district_to_update.name = data['name']
            district_to_update.short = data['short']
            db.session.commit()

            # Log the action
            log_entry = Log(
                username=current_user.username,
                last_name=current_user.familiya,
                district=current_user.dist,
                roles=current_user.roles,
                actions=f"{current_user.username} {current_user.familiya} tomonidan Boshqaruv bo'g'ini uchun "
                        f"{old_district_name} va {old_district_short} ma'lumotlari {data['name']} va {data['short']} ga"
                        f" o'zgartirildi",
                times=datetime.now(),
                dates = datetime.today().date()
            )

            return jsonify({"message": "Ma'lumot muvoffaqiyatli o'zgartirildi!"})
        else:
            return jsonify({"error": "District not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@default_api.route('/districts/<int:id>', methods=['DELETE'])
@token_required
def delete_district(current_user, id):

    if current_user.roles != "S_admin" or current_user.dist != 10:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:
        district_to_delete = District.query.get(id)
        if district_to_delete:
            district_name=district_to_delete.name
            db.session.delete(district_to_delete)
            db.session.commit()

            # Log the action
            log_entry = Log(
                username=current_user.username,
                last_name=current_user.familiya,
                district=current_user.dist,
                roles=current_user.roles,
                actions=f"{current_user.username} {current_user.familiya} tomonidan Boshqaruv bo'g'inidagi {district_name} "
                        f"ma'lmotlari o'chirildi",
                times=datetime.now(),
                dates=datetime.today().date()
            )

            return jsonify({"message": "Ma'lumot muvoffaqiyatli o'chirildi!"})
        else:
            return jsonify({"error": "District not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


##############################################################################################
#                             Dastlabki ma'lumotlar (Section)                                #
##############################################################################################

@default_api.route('/section', methods=['GET'])
@token_required
def get_section(current_user):

    if current_user.roles != "S_admin" or current_user.dist != 10:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:
        sections = Section.query.all()
        section_list = []

        for section in sections:
            # Query the corresponding District based on district_fk
            district = District.query.get(section.okrug_fk)

            if district:
                # Append the data to the section_list
                section_data = {
                    "id": section.id,
                    "name": section.name,
                    "okrug_fk": section.okrug_fk,
                    "district_name": district.short  # Include district name
                }
                section_list.append(section_data)

        return jsonify(section_list)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@default_api.route('/section', methods=['POST'])
@token_required
def insert_section(current_user):

    if current_user.roles != "S_admin" or current_user.dist != 10:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:
        data = request.get_json()
        new_section = Section(name=data['name'], okrug_fk=data['okrug_fk'])
        db.session.add(new_section)
        db.session.commit()

        # Log the action
        log_entry = Log(
            username=current_user.username,
            last_name=current_user.familiya,
            district=current_user.dist,
            roles=current_user.roles,
            actions=f"{current_user.username} {current_user.familiya} tomonidan {data['name']} harbiy qism "
                    f"ma'lumotlari kiritildi",
            times=datetime.now(),
            dates=datetime.today().date()
        )

        return jsonify({"message": "Ma'lumot muvoffaqiyatli kiritildi!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@default_api.route('/section/<int:id>', methods=['PUT'])
@token_required
def update_section(current_user, id):

    if current_user.roles != "S_admin" or current_user.dist != 10:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:
        data = request.get_json()
        section_to_update = Section.query.get(id)
        if section_to_update:
            old_section_name=section_to_update.name
            section_to_update.name = data['name']
            section_to_update.okrug_fk = data['okrug_fk']
            db.session.commit()

            # Log the action
            log_entry = Log(
                username=current_user.username,
                last_name=current_user.familiya,
                district=current_user.dist,
                roles=current_user.roles,
                actions=f"{current_user.username} {current_user.familiya} tomonidan  {old_section_name} harbiy qism"
                        f" ma'lumotlari {data['name']} ga o'zgartirildi",
                times=datetime.now(),
                dates=datetime.today().date()
            )

            return jsonify({"message": "Ma'lumot muvoffaqiyatli o'zgartirildi!"})
        else:
            return jsonify({"error": "Ma'lumot topilmadi!"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@default_api.route('/section/<int:id>', methods=['DELETE'])
@token_required
def delete_section(current_user, id):

    if current_user.roles != "S_admin" or current_user.dist != 10:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:
        section_to_delete = Section.query.get(id)
        if section_to_delete:
            section_name=section_to_delete.name
            db.session.delete(section_to_delete)
            db.session.commit()

            # Log the action
            log_entry = Log(
                username=current_user.username,
                last_name=current_user.familiya,
                district=current_user.dist,
                roles=current_user.roles,
                actions=f"{current_user.username} {current_user.familiya} tomonidan {section_name} "
                        f"ma'lmotlari o'chirildi",
                times=datetime.now(),
                dates=datetime.today().date()
            )

            return jsonify({"message": "Ma'lumot muvoffaqiyatli o'chirildi!"})
        else:
            return jsonify({"error": "Ma'lumot topilmadi!"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

##############################################################################################
#                              Dastlabki ma'lumotlar (VLAN)                                  #
##############################################################################################
@default_api.route('/vlan', methods=['GET'])
@token_required
def get_vlans(current_user):

    if current_user.roles != "S_admin" or current_user.dist != 10:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:
        vlans = Vlan.query.all()
        vlan_list = [{"id": vlan.id, "name": vlan.name, "vlan_id": vlan.vlan_id} for vlan in vlans]
        return jsonify(vlan_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@default_api.route('/vlan', methods=['POST'])
@token_required
def insert_vlan(current_user):

    if current_user.roles != "S_admin" or current_user.dist != 10:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:
        data = request.get_json()
        new_section = Vlan(name=data['name'], vlan_id=data['vlan_id'])
        db.session.add(new_section)
        db.session.commit()

        # Log the action
        log_entry = Log(
            username=current_user.username,
            last_name=current_user.familiya,
            district=current_user.dist,
            roles=current_user.roles,
            actions=f"{current_user.username} {current_user.familiya} tomonidan {data['name']}"
                    f" nomli {data['vlan_id']} ma'lumotlari kiritildi",
            times=datetime.now(),
            dates=datetime.today().date()
        )

        return jsonify({"message": "Ma'lumot muvoffaqiyatli kiritildi!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@default_api.route('/vlan/<int:id>', methods=['PUT'])
@token_required
def update_vlan(current_user, id):

    if current_user.roles != "S_admin" or current_user.dist != 10:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401
    try:
        data = request.get_json()
        vlan_to_update = Vlan.query.get(id)
        if vlan_to_update:
            old_vlan_name=vlan_to_update.name
            old_vlan_vlan_id=vlan_to_update.vlan_id
            vlan_to_update.name = data['name']
            vlan_to_update.vlan_id = data['vlan_id']
            db.session.commit()

            # Log the action
            log_entry = Log(
                username=current_user.username,
                last_name=current_user.familiya,
                district=current_user.dist,
                roles=current_user.roles,
                actions=f"{current_user.username} {current_user.familiya} tomonidan {old_vlan_name}"
                        f" nomli {old_vlan_vlan_id} ma'lumotlari {data['name']} {data['vlan_id']} ma'lumotlariga "
                        f"o'zgartirildi kiritildi",
                times=datetime.now(),
                dates=datetime.today().date()
            )

            return jsonify({"message": "Ma'lumot muvoffaqiyatli o'zgartirildi!"})
        else:
            return jsonify({"error": "Ma'lumot topilmadi!"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@default_api.route('/vlan/<int:id>', methods=['DELETE'])
@token_required
def delete_vlan(current_user, id):

    if current_user.roles != "S_admin" or current_user.dist != 10:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:
        vlan_to_delete = Vlan.query.get(id)
        if vlan_to_delete:
            vlan_name=vlan_to_delete.name
            db.session.delete(vlan_to_delete)
            db.session.commit()

            # Log the action
            log_entry = Log(
                username=current_user.username,
                last_name=current_user.familiya,
                district=current_user.dist,
                roles=current_user.roles,
                actions=f"{current_user.username} {current_user.familiya} tomonidan {vlan_name} ma'lumotli o'chirildi",
                times=datetime.now(),
                dates=datetime.today().date()
            )

            return jsonify({"message": "Ma'lumot muvoffaqiyatli o'chirildi!"})
        else:
            return jsonify({"error": "Ma'lumot topilmadi!"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

##############################################################################################
#                              Dastlabki ma'lumotlar (VENDOR)                                #
##############################################################################################

@default_api.route('/vendor', methods=['GET'])
@token_required
def get_vendors(current_user):

    if current_user.roles != "S_admin" or current_user.dist != 10:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:
        vendors = Vendor.query.all()
        vendor_list = [{"id": vendor.id, "name": vendor.name} for vendor in vendors]
        return jsonify(vendor_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@default_api.route('/vendor', methods=['POST'])
@token_required
def insert_vendor(current_user):

    if current_user.roles != "S_admin" or current_user.dist != 10:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:
        data = request.get_json()
        new_section = Vendor(name=data['name'])
        db.session.add(new_section)
        db.session.commit()

        # Log the action
        log_entry = Log(
            username=current_user.username,
            last_name=current_user.familiya,
            district=current_user.dist,
            roles=current_user.roles,
            actions=f"{current_user.username} {current_user.familiya} tomonidan {data['name']} ma'lumotlari kiritildi",
            times=datetime.now(),
            dates=datetime.today().date()
        )

        return jsonify({"message": "Ma'lumot muvoffaqiyatli kiritildi!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@default_api.route('/vendor/<int:id>', methods=['PUT'])
@token_required
def update_vendor(current_user, id):

    if current_user.roles != "S_admin" or current_user.dist != 10:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:
        data = request.get_json()
        vendor_to_update = Vendor.query.get(id)
        if vendor_to_update:
            old_vendor_name=vendor_to_update.name
            vendor_to_update.name = data['name']
            db.session.commit()

            # Log the action
            log_entry = Log(
                username=current_user.username,
                last_name=current_user.familiya,
                district=current_user.dist,
                roles=current_user.roles,
                actions=f"{current_user.username} {current_user.familiya} tomonidan {old_vendor_name} ma'lumotlari"
                        f" {data['name']} ga o'zgartirildi",
                times=datetime.now(),
                dates=datetime.today().date()
            )

            return jsonify({"message": "Ma'lumot muvoffaqiyatli o'zgartirildi!"})
        else:
            return jsonify({"error": "Ma'lumot topilmadi!"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@default_api.route('/vendor/<int:id>', methods=['DELETE'])
@token_required
def delete_vendor(current_user, id):

    if current_user.roles != "S_admin" or current_user.dist != 10:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:
        vendor_to_delete = Vendor.query.get(id)
        if vendor_to_delete:
            old_vendor_name=vendor_to_delete.name
            db.session.delete(vendor_to_delete)
            db.session.commit()

            # Log the action
            log_entry = Log(
                username=current_user.username,
                last_name=current_user.familiya,
                district=current_user.dist,
                roles=current_user.roles,
                actions=f"{current_user.username} {current_user.familiya} tomonidan {old_vendor_name} ma'lumotlari"
                        f"o'chirildi",
                times=datetime.now(),
                dates=datetime.today().date()
            )

            return jsonify({"message": "Ma'lumot muvoffaqiyatli o'chirildi!"})
        else:
            return jsonify({"error": "Ma'lumot topilmadi!"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

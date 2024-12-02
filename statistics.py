from flask import Blueprint, request, jsonify, render_template
import psycopg2.extras
from sqlalchemy import func
from gen_token import token_required
from db_config import db, UniversalTable, District, Section, Vlan, Vendor, Log



statis_api = Blueprint('statis_api', __name__)



##############################################################################################
#                         Statistik ma'lumotlar (Universal_table)                            #
##############################################################################################

@statis_api.route('/all_vendor_data', methods=['GET'])
@token_required
def all_vendor_data(current_user):
    allowed_roles = ["S_admin", "D_admin", "RO_admin"]

    if current_user.roles not in allowed_roles:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:
        vendor_data_query = db.session.query(
            UniversalTable.vendor_fk,
            Vendor.name.label('vendor_name'),
            db.func.count().label('count')
        ).join(Vendor, UniversalTable.vendor_fk == Vendor.id) \
            .group_by(UniversalTable.vendor_fk, Vendor.name)

        if current_user.roles == "S_admin" and current_user.dist == 10:
            total_count = UniversalTable.query.count()
        else:
            total_count = UniversalTable.query.filter_by(district_fk=current_user.dist).count()
            vendor_data_query = vendor_data_query.filter(UniversalTable.district_fk == current_user.dist)

        vendor_data = vendor_data_query.all()

        vendor_percentage_data = [
            {
                'vendor_id': vendor.vendor_fk,
                'vendor_name': vendor.vendor_name,
                'count': vendor.count,
                'percentage': round((vendor.count / total_count) * 100)
            }
            for vendor in vendor_data
        ]

        return jsonify(vendor_percentage_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@statis_api.route('/district_vendor_data/<int:id>', methods=['GET'])
@token_required
def district_vendor_data(current_user, id):

    allowed_roles = "S_admin"
    if not current_user.roles in allowed_roles:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    total_count = UniversalTable.query.filter_by(district_fk=id).count()

    vendor_data = db.session.query(
        UniversalTable.vendor_fk,
        Vendor.name.label('vendor_name'),
        db.func.count().label('count')
    ).join(Vendor, UniversalTable.vendor_fk == Vendor.id)\
    .filter(UniversalTable.district_fk == id)\
    .group_by(UniversalTable.vendor_fk, Vendor.name).all()

    vendor_percentage_data = []
    for vendor_id, vendor_name, count in vendor_data:
        percentage = round((count / total_count) * 100)
        vendor_percentage_data.append({
            'vendor_id': vendor_id,
            'vendor_name': vendor_name,
            'count': count,
            'percentage': percentage
        })

    return jsonify(vendor_percentage_data)


@statis_api.route('/section_vendor_data/<int:id>', methods=['GET'])
@token_required
def section_vendor_data(current_user, id):

    allowed_roles = ["S_admin", "D_admin", "RO_admin"]
    if not current_user.roles in allowed_roles:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    vendor_data = db.session.query(UniversalTable.vendor_fk, db.func.count().label('count')).filter_by(section_fk=id).group_by(UniversalTable.vendor_fk).all()


    total_count = sum(count for _, count in vendor_data)


    vendor_percentage_data = []
    for vendor, count in vendor_data:
        vendor_name = Vendor.query.filter_by(id=vendor).first().name
        if vendor_name is not None:
            percentage = round((count / total_count) * 100)
            vendor_percentage_data.append({
                'vendor_id': vendor,
                'vendor_name': vendor_name,
                'count': count,
                'percentage': percentage
            })

    return jsonify(vendor_percentage_data)


@statis_api.route('/all_vlan_data', methods=['GET'])
@token_required
def all_vlan_data(current_user):
    # Define allowed roles
    allowed_roles = ["S_admin", "D_admin", "RO_admin"]
    if not current_user.roles in allowed_roles:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:
        # If the user is an "S_admin," retrieve all district_fk IDs
        if current_user.roles == "S_admin":

            unique_vlan_count = db.session.query(
                db.func.count(db.func.distinct(UniversalTable.vlan_fk))
            ).scalar()

                 # Retrieve VLAN data for all districts
            vlan_data = db.session.query(
                UniversalTable.vlan_fk,
                Vlan.name.label('vlan_name'),
                db.func.count().label('count')
            ).join(Vlan, UniversalTable.vlan_fk == Vlan.id)\
            .group_by(UniversalTable.vlan_fk, Vlan.name).all()


            vlan_foiz = []

            for vlan_id, vlan_name, count in vlan_data:
                foiz = round(100/unique_vlan_count )
                vlan_foiz.append({
                    "vlan_id": vlan_id,
                    "vlan_name": vlan_name,
                    "count": count,
                    "percentage": foiz
                })

        # If the user is a "D_admin" or "RO_admin," retrieve district_fk IDs equal to current_user.dist
        else:
            unique_vlan_count = db.session.query(
                db.func.count(db.func.distinct(UniversalTable.vlan_fk))
            ).filter(UniversalTable.district_fk == current_user.dist).scalar()

            # Retrieve VLAN data for current_user.dist
            vlan_data = db.session.query(
                UniversalTable.vlan_fk,
                Vlan.name.label('vlan_name'),
                db.func.count().label('count')
            ).join(Vlan, UniversalTable.vlan_fk == Vlan.id)\
            .filter(UniversalTable.district_fk == current_user.dist)\
            .group_by(UniversalTable.vlan_fk, Vlan.name).all()

        # Calculate and format percentage data
        vlan_percentage_data = []
        for vlan_id, vlan_name, count in vlan_data:
            percentage = round(100/unique_vlan_count)
            vlan_percentage_data.append({
                'vlan_id': vlan_id,
                'vlan_name': vlan_name,
                'count': unique_vlan_count,
                'percentage': percentage
            })

        # If the user is an "S_admin," include all district_fk IDs in the response
        if current_user.roles == "S_admin":
            return jsonify({'vlan_percentage_data': vlan_foiz})
        else:
            return jsonify( {'vlan_percentage_data': vlan_percentage_data})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@statis_api.route('/district_vlan_data/<int:id>', methods=['GET'])
@token_required
def district_vlan_data(current_user, id):

    allowed_roles = ["S_admin", "D_admin", "RO_admin"]
    if not current_user.roles in allowed_roles:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    district = District.query.filter_by(id=id).first()
    if not district:
        return jsonify({'message': 'District topilmadi'}), 404

    total_count = db.session.query(
        db.func.count(db.distinct(UniversalTable.vlan_fk))
    ).filter_by(district_fk=id).scalar()

    district_data = {
        'district_id': district.id,
        'district_name': district.name,
        'district_short': district.short,
        'total_vlan_count': total_count,
        'vlan_data': []
    }

    if total_count > 0:
        vlan_data = db.session.query(
            UniversalTable.vlan_fk,
            db.func.count(UniversalTable.vlan_fk).label('count')
        ).filter_by(district_fk=id).group_by(UniversalTable.vlan_fk).all()

        seen_vlan_ids = set()
        for vlan_id, count in vlan_data:
            vlan_entry = Vlan.query.filter_by(id=vlan_id).first()
            if vlan_entry and vlan_entry.vlan_id not in seen_vlan_ids:
                seen_vlan_ids.add(vlan_entry.vlan_id)
                percentage = round(100/total_count)
                district_data['vlan_data'].append({
                    "vlan_id": vlan_entry.vlan_id,
                    "vlan_name": vlan_entry.name,
                    "count": count,
                    "percentage": percentage
                })

    return jsonify(district_data)


@statis_api.route('/district_vlan_dates', methods=['GET'])
@token_required
def district_vlan_data_all(current_user):

    allowed_roles = ["S_admin", "D_admin", "RO_admin"]
    if not current_user.roles in allowed_roles:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    # District jadvalidan barcha id va nomlarni olish
    districts = District.query.all()

    result = []

    for district in districts:
        # Har bir districtdagi turli sectionlar orasida noyob `vlan_fk`lar sonini olish
        total_count = db.session.query(
            db.func.count(db.distinct(UniversalTable.vlan_fk))
        ).filter_by(district_fk=district.id).scalar()

        district_data = {
            'district_id': district.id,
            'district_name': district.name,
            'total_vlan_count': total_count,  # Umumiy takrorlanmas VLANlar sonini qo'shish
            'vlan_data': []
        }

        if total_count > 0:
            # Har bir district uchun noyob `vlan_fk`lar ro'yxatini olish
            vlan_data = db.session.query(
                UniversalTable.vlan_fk,
                db.func.count(UniversalTable.vlan_fk).label('count')
            ).filter_by(district_fk=district.id).group_by(UniversalTable.vlan_fk).all()

            seen_vlan_ids = set()  # Noyob `vlan_id`larni kuzatish uchun to'plam
            for vlan_id, count in vlan_data:
                vlan_entry = Vlan.query.filter_by(id=vlan_id).first()
                if vlan_entry and vlan_entry.vlan_id not in seen_vlan_ids:
                    seen_vlan_ids.add(vlan_entry.vlan_id)
                    percentage = round(100/total_count)
                    district_data['vlan_data'].append({
                        'vlan_id': vlan_entry.vlan_id,  # Vlan jadvalidan 'vlan_id' maydonini olish
                        'vlan_name': vlan_entry.name,   # Vlan jadvalidan 'name' maydonini olish
                        'count': count,
                        'percentage': percentage
                    })

        result.append(district_data)

    return jsonify(result)


@statis_api.route('/section_vlan_data/<int:id>', methods=['GET'])
@token_required
def section_vlan_data(current_user, id):

    allowed_roles = ["S_admin", "D_admin", "RO_admin"]
    if not current_user.roles in allowed_roles:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    vlan_data = db.session.query(UniversalTable.vlan_fk, db.func.count().label('count')).filter_by(section_fk=id).group_by(UniversalTable.vlan_fk).all()


    total_count = sum(count for _, count in vlan_data)


    vlan_percentage_data = []
    for vlan, count in vlan_data:
        vlan_name = Vlan.query.filter_by(id=vlan).first().name
        if vlan_name is not None:
            percentage = round((count / total_count) * 100)
            vlan_percentage_data.append({
                'vlan_id': vlan,
                'vlan_name': vlan_name,
                'count': count,
                'percentage': percentage
            })

    return jsonify(vlan_percentage_data)



@statis_api.route('/vlan_data_filter/<int:id>', methods=['GET'])
@token_required
def vlan_data_filter_all(current_user, id):

    allowed_roles = ["S_admin", "D_admin", "RO_admin"]
    if not current_user.roles in allowed_roles:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:
        # If the user is an "S_admin," retrieve all vlan_fk and district_fk IDs
        if current_user.roles == "S_admin":

            data = db.session.query(
                UniversalTable.district_fk,
                UniversalTable.section_fk,
                db.func.count().label('count')
            ).filter_by(vlan_fk=id).group_by(
                UniversalTable.district_fk,
                UniversalTable.section_fk
            ).all()

            total_count = sum(count for _, _, count in data)

        # If the user is a "D_admin" or "RO_admin," retrieve vlan_fk IDs equal to current_user.dist
        else:
            # Retrieve total count for current_user.dist
            total_count = UniversalTable.query.filter_by(district_fk=current_user.dist, vlan_fk=id).count()

            # Retrieve data for current_user.dist and vlan_fk
            data = db.session.query(
                UniversalTable.district_fk,
                UniversalTable.section_fk,
                db.func.count().label('count')
            ).filter_by(district_fk=current_user.dist, vlan_fk=id).group_by(
                UniversalTable.district_fk,
                UniversalTable.section_fk
            ).all()

        data_types_percentage = []
        for district, section, count in data:
            district_name = District.query.filter_by(id=district).first().name
            section_name = Section.query.filter_by(id=section).first().name
            if district_name is not None and section_name is not None:
                percentage = round((count / total_count) * 100) if total_count != 0 else 0
                data_types_percentage.append({
                    'district_id': district,
                    'district_name': district_name,
                    'section_id': section,
                    'section_name': section_name,
                    'count': count,
                    'percentage': percentage
                })

        # If the user is an "S_admin," include all vlan_fk and district_fk IDs in the response
        if current_user.roles == "S_admin":
            return jsonify({'data_types_percentage': data_types_percentage})
        else:
            return jsonify(data_types_percentage)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@statis_api.route('/count_devices', methods=['GET'])
@token_required
def count_vendors(current_user):

    allowed_roles = ["S_admin", "D_admin", "RO_admin"]
    if not current_user.roles in allowed_roles:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:
        # If the user is an "S_admin," retrieve IPv4_count with all vendor_count, vendor_type_count, vlan_count, vlan_fk == 1
        if current_user.roles == "S_admin" and current_user.dist == 10:
            vlan_count = db.session.query(UniversalTable.vlan_fk).distinct().count()
            IPv4_count = db.session.query(UniversalTable.ip_add).filter(UniversalTable.vlan_fk == 1).distinct().count()
            IPv4_backup = db.session.query(UniversalTable.ip_add).filter(UniversalTable.vlan_fk == 10).distinct().count()

        # If the user is a "D_admin" or "RO_admin," retrieve IPv4_count with district_fk id equal to current_user.dist, vendor_count, vendor_type_count, vlan_count, vlan_fk == 1
        else:
            vlan_count = db.session.query(UniversalTable.vlan_fk).filter(UniversalTable.district_fk == current_user.dist).distinct().count()
            IPv4_count = db.session.query(UniversalTable.ip_add).filter(UniversalTable.district_fk == current_user.dist, UniversalTable.vlan_fk == 1).distinct().count()
            IPv4_backup = db.session.query(UniversalTable.ip_add).filter(UniversalTable.district_fk == current_user.dist,
                                                                        UniversalTable.vlan_fk == 2).distinct().count()

        # Create a JSON response
        response = {
            'IPv4_backup': IPv4_backup,
            # 'vendor_type': vendor_type_count,
            'vlan_count': vlan_count,
            'IPv4_count': IPv4_count
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@statis_api.route('/dist_vendor_app', methods=['GET'])
@token_required
def count_vendors_by_district1(current_user):

    allowed_roles = ["S_admin", "D_admin", "RO_admin"]
    if not current_user.roles in allowed_roles:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:
        if current_user.roles == "S_admin" and current_user.dist == 10:
            # Query the database to count the vendors for each district_fk with vlan_fk equal to 1
            result = db.session.query(
                UniversalTable.district_fk,
                District.short,
                func.count(UniversalTable.vendor_fk).label('vendor_count')
            ).join(District, UniversalTable.district_fk == District.id) \
            .filter(UniversalTable.vlan_fk == 1) \
            .group_by(UniversalTable.district_fk, District.short) \
            .all()
        else:
            result = db.session.query(
                UniversalTable.district_fk,
                District.short,
                func.count(UniversalTable.vendor_fk).label('vendor_count')
            ).join(District, UniversalTable.district_fk == District.id) \
                .filter(UniversalTable.vlan_fk == 1, UniversalTable.district_fk == current_user.dist) \
            .group_by(UniversalTable.district_fk, District.short) \
            .all()

        # Create a JSON response
        response = [{'d_id': row[0], 'd_name': row[1], 'd_v_count': row[2]} for row in result]
        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
from werkzeug.security import generate_password_hash
from flask import Flask, Blueprint, request, jsonify
from gen_token import token_required
from db_config import db, User, District, Roles, Log
from datetime import datetime
import os


user_api = Blueprint('user_api', __name__)






class DistrictHelper:
    @staticmethod
    def get_district_short(district_id):
        """Retrieve the short value for a given district ID."""
        district = District.query.get(district_id)
        return district.short if district else None

@user_api.route('/users', methods=['GET'])
@token_required
def get_user(current_user):
    allowed_roles = ["S_admin", "D_admin", "RO_admin"]

    if current_user.roles not in allowed_roles:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401


    district = District.query.filter_by(id=current_user.dist).first()

    user_data = {
        'username': current_user.username,
        'familiya': current_user.familiya,
        'ism': current_user.ism,
        'dist': district.short,
        'roles': current_user.roles,
    }
    return jsonify({'user_data': user_data})


@user_api.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):
    # Check if the current user has the required role
    if current_user.roles != "S_admin":
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:
        users = User.query.all()
        users_list = []

        for user in users:
            district = District.query.get(user.dist)

            if district:
                user_data = {
                    "id": user.id,
                    "familiya": user.familiya,
                    "ism": user.ism,
                    "username": user.username,
                    "password": user.password,
                    "roles": user.roles,
                    "dist": district.short,
                }
                users_list.append(user_data)

        return  jsonify(users_list)

    except Exception as e:
        return jsonify({"erroe": str(e)}), 500


@user_api.route('/user/<int:id>', methods=['GET'])
@token_required
def get_one_users(current_user, id):

    allowed_roles = ["S_admin", "D_admin"]

    if current_user.roles not in allowed_roles:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    user = User.query.filter_by(id=id).first()

    if not user:
       return jsonify({'message': 'Foydalanuvchi topilmadi'}), 404

    user_data = {}
    user_data['id'] = user.id
    user_data['familiya'] = user.familiya
    user_data['ism'] = user.ism
    user_data['username'] = user.username
    user_data['password'] = user.password
    user_data['dist'] = user.dist
    user_data['roles'] = user.roles

    return jsonify({'user': user_data}), 200

@user_api.route('/user', methods=['POST'])
@token_required
def create_user(current_user):
    # Check if the current user has the required role
    if not current_user.roles == "S_admin":
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    # Validate input data
    data = request.get_json()  # JSON ma'lumotlarini olish
    required_fields = ['familiya', 'ism', 'username', 'password', 'dist', 'roles']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Required fields are missing'}), 400

    # Hash the password
    hashed_password = generate_password_hash(data['password'])

    # Create a new user
    new_user = User(
        familiya=data['familiya'],
        ism=data['ism'],
        username=data['username'],
        password=hashed_password,
        dist=data['dist'],
        roles=data['roles']
    )

    # Add the user to the database
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            'message': 'Yangi foydalanuvchi yaratildi'
        }), 201
    except Exception as e:
        print(f"Error creating user: {e}")
        db.session.rollback()
        return jsonify({'message': 'Internal server error'}), 500




@user_api.route('/user/<int:id>', methods=['DELETE'])
@token_required
def delete_user(current_user, id):

    if not current_user.roles == "S_admin" and current_user.dist == 10:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 403  # 403 Forbidden for non-admin users

    user = User.query.filter_by(id=id).first()

    if not user:
        return jsonify({'message': 'Foydalanuvchi topilmadi'}), 404  # 404 Not Found when user not found

    try:
        db.session.delete(user)
        db.session.commit()

        # Log for create user
        log_entry = Log(
            username=current_user.username,
            last_name=current_user.familiya,
            district=current_user.dist,
            roles=current_user.roles,
            actions=f"{current_user.username} {current_user.familiya} tomonidan user o'chirildi"
                    f"funktsiyalari boshlag'ich holatda sozlandi",
            times=datetime.now(),
            dates=datetime.today().date()
        )
        db.session.add(log_entry)
        db.session.commit()

        return jsonify({'message': "Foydalanuvchi o'chirildi!"}), 200  # 200 OK for successful deletion
    except Exception as e:
        # Log the error for debugging purposes
        print(f"Error deleting user: {e}")
        db.session.rollback()  # Rollback the transaction in case of an error
        return jsonify({'message': 'Server error occurred'}), 500  # 500 Internal Server Error for other errors


@user_api.route('/user/<int:id>', methods=['PUT'])
@token_required
def update_user(current_user, id):
    if not current_user.roles == ["S_admin"] and current_user.dist == 10:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan', 'success': False}), 401

    try:
        user = User.query.get(id)

        # Log for create user
        log_entry = Log(
            username=current_user.username,
            last_name=current_user.familiya,
            district=current_user.dist,
            roles=current_user.roles,
            actions=f"{current_user.username} {current_user.familiya} tomonidan qurilmasida useri o'chirildi"
                    f"funktsiyalari boshlag'ich holatda sozlandi",
            times=datetime.now(),
            dates=datetime.today().date()
        )
        db.session.add(log_entry)
        db.session.commit()

        if user is None:
            return jsonify({'message': 'Foydalanuvchi topilmadi'}), 404

        # Update the desired columns
        user.familiya = request.json.get('familiya', user.familiya)
        user.ism = request.json.get('ism', user.ism)
        user.username = request.json.get('username', user.username)
        new_password = request.json.get('password', None)
        if new_password:
            hashed_password = generate_password_hash(new_password)
            user.password = hashed_password  # Update the password with the hashed value
        user.roles = request.json.get('roles', user.roles)
        user.dist = request.json.get('dist', user.dist)

        # Commit the changes to the database
        db.session.commit()

        return jsonify({'message': "Foydalanuvchi ma'lumotlari muvoffaqiyatli o'zgartirildi", 'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500



@user_api.route('/user_search', methods=['GET'])
@token_required
def user_search(current_user):

    if not current_user.roles == "S_admin" and current_user.dist == 10:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    search_term = request.args.get('search_user', '')
    if not search_term:
        return jsonify({'error': "Qidiruv kalitida xatolik bor"}), 400

    results = User.query.filter(
        db.or_(
            User.public_id.ilike(search_term),
            User.familiya.ilike(search_term),
            User.ism.ilike(search_term),
            User.username.ilike(search_term),
            User.roles.ilike(search_term)
        )
    ).all()

    search_results = []
    for user in results:
        search_results.append({
            'id': user.id,
            'public_id': user.public_id,
            'familiya': user.familiya,
            'ism': user.ism,
            'username': user.username,
            'roles': user.roles
        })

    return jsonify(search_results)


@user_api.route('/roles', methods=['GET'])
@token_required
def get_roles(current_user):

    if not current_user.roles == "S_admin" and current_user.dist == 10:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    try:
        roles = Roles.query.all()
        role_list = [{"id": role.id, "name": role.roles} for role in roles]
        return jsonify(role_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

from flask import jsonify, request, Flask, Blueprint
from db_config import db, Log, District
from gen_token import token_required
import binary_commands
import yaml
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'manashukeymanashukey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:toor@192.168.202.46/postgres'

logs = Blueprint('logs', __name__)

db.init_app(app)


# Ma'lumotlarni olish uchun API yo'nalishi
@logs.route('/api/logs', methods=['GET'])
@token_required
def get_logs(current_user):
    allowed_roles = ["S_admin", "D_admin"]
    if not current_user.roles in allowed_roles:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    logs = Log.query.all()  # Fetch all records
    logs_list = []

    for log in logs:
        logs_list.append({
            'id': log.id,
            'username': log.username,
            'last_name': log.last_name,
            'district': log.district,
            'roles': log.roles,
            'actions': log.actions,
            'times': log.times.strftime('%H:%M:%S'),  # Format time to remove microseconds
            'dates': log.dates.isoformat()
        })

    return jsonify(logs_list)  # Return as JSON


@logs.route('/search_logs', methods=['POST'])
def search_logs():
    data = request.get_json()

    # Qidiruv uchun barcha filterlarni olish
    username = data.get('username')
    last_name = data.get('last_name')
    district = data.get('district')
    roles = data.get('roles')
    actions = data.get('actions')
    dates = data.get('dates')

    # Filtrlarni qo'llash
    query = Log.query
    if username:
        query = query.filter_by(username=username)
    if last_name:
        query = query.filter_by(last_name=last_name)
    if district:
        query = query.filter_by(district=district)
    if roles:
        query = query.filter_by(roles=roles)
    if actions:
        query = query.filter_by(actions=actions)
    if dates:
        query = query.filter(Log.dates == dates)  # Sanalar tengligini solishtirish uchun

    # Natijalarni olish
    logs = query.all()

    # Natijalarni JSON formatiga o'tkazish
    results = [
        {
            "id": log.id,
            "username": log.username,
            "last_name": log.last_name,
            "district": log.district,
            "roles": log.roles,
            "actions": log.actions,
            "dates": log.dates.strftime('%Y-%m-%d')
        }
        for log in logs
    ]

    return jsonify(results), 200
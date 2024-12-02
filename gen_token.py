from flask import Blueprint, Flask, request, jsonify, make_response
from functools import wraps
from flask import request, jsonify
import jwt
from werkzeug.security import check_password_hash
from db_config import User
from flask_cors import CORS


app = Flask(__name__)
app.config['SECRET_KEY'] = 'manashukeymanashukey'
CORS(app)

api_bp = Blueprint('api', __name__)

blacklist = set()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
            if token.startswith('Bearer '):
                # Extract the token without 'Bearer ' prefix
                token = token[7:]
            else:
                return jsonify({'message': 'Invalid token format'}), 401

        if not token:
            return jsonify({'message': 'Token tokenda xatolik'}), 401

        # # Check if token is blacklisted
        # if token in blacklist:
        #     return jsonify({'message': 'Token has been blacklisted'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(username=data['username'],
                                                familiya=data['familiya'],
                                                ism=data['ism'],
                                                dist=data['dist'],
                                                roles=data['roles']).first()
            if not current_user:
                return jsonify({'message': 'User not found'}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@api_bp.route('/api/logout', methods=['POST'])
@token_required
def logout(current_user):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Missing Authorization header'}), 401

    # Extract the token without "Bearer " prefix
    token = token[7:] if token.startswith('Bearer ') else token

    # Token is valid, return a success message
    return jsonify({'message': 'Token valid, logout successful'}), 200

@api_bp.route('/api/login', methods=['POST'])
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required'})

    user = User.query.filter_by(username=auth.username).first()

    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required'})

    if check_password_hash(user.password, auth.password):
        # Create a new session record when the user logs in
        # new_session = UserSession(user_id=user.id, login_time=datetime.now())
        # db.session.add(new_session)
        # db.session.commit()

        # Generate a JWT token
        token = jwt.encode({
            'id': user.id,
            'username': user.username,
            'familiya': user.familiya,
            'ism': user.ism,
            'dist': user.dist,
            'roles': user.roles,
        }, app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({'token': token.decode('UTF-8')})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required'})
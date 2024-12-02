from flask import Blueprint, Flask, request, jsonify, make_response
import jwt
from werkzeug.security import check_password_hash
from db_config import db, User, UserSession
from datetime import datetime
from gen_token import token_required
from flask_cors import CORS


app = Flask(__name__)
app.config['SECRET_KEY'] = 'manashukeymanashukey'
CORS(app)

api_bp = Blueprint('api', __name__)


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
            'roles': user.roles
        }, app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({'token': token.decode('UTF-8')})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required'})


@api_bp.route('/api/logout', methods=['POST'])
@token_required
def logout1(current_user):
    allowed_roles = ["S_admin", "D_admin", "RO_admin"]

    if current_user.roles not in allowed_roles:
        return jsonify({'message': 'Sizning Huqularingiz cheklangan'}), 401

    # Get the user's token from the request headers (Bearer token)
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({'message': 'Missing Authorization header with Bearer token'}), 401

    # Extract the token from the "Bearer <token>" format
    try:
        token = token.split(" ")[1]
    except IndexError:
        return jsonify({'message': 'Invalid Authorization header format'}), 401

    try:
        # Verify the token and extract the user's ID
        user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = user_data['id']


    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.InvalidTokenError as e:
        print(f"Invalid token error: {e}")
        return jsonify({'message': 'Invalid token'}), 401
    except jwt.InvalidAudienceError:
        return jsonify({'message': 'Invalid audience in the token'}), 401
    except jwt.InvalidIssuerError:
        return jsonify({'message': 'Invalid issuer in the token'}), 401
    except Exception as e:
        print(f"Error decoding token: {e}")
        return jsonify({'message': 'Error decoding token'}), 500



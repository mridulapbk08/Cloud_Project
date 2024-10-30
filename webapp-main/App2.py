from flask import Flask, request, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import Bcrypt
from sqlalchemy import text, exc
import uuid
from flask_httpauth import HTTPBasicAuth
from datetime import datetime, timedelta
from flask_migrate import Migrate
from google.cloud import pubsub_v1
import uuid
import logging
import json
import secrets
import re
import os
from dotenv import load_dotenv
load_dotenv()

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "level": record.levelname,
            "message": record.getMessage(),
            "time": self.formatTime(record, self.datefmt),
        }
        return json.dumps(log_record)
    
# object of flask 
dbhost = os.environ.get("DB_HOST")
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")
dbname = os.environ.get("DBNAME")



App = Flask(__name__)
App.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{username}:{password}@{dbhost}/{dbname}"
App.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
App.config['SECRET_KEY'] = 'root@123'  
db = SQLAlchemy(App)
bcrypt = Bcrypt(App)
auth = HTTPBasicAuth()
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path('csye6225-assignment3','verify_email')

handler = logging.FileHandler('app_log.log')  
handler.setFormatter(JsonFormatter())
App.logger.addHandler(handler)
App.logger.setLevel(logging.INFO)



class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(36), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    token = db.Column(db.String(32), default=None, nullable=True)
    isverified = db.Column(db.Boolean, default=False, nullable=False)
    token_expiry = db.Column(db.DateTime, default=None, nullable=True)
    account_created = db.Column(db.DateTime, default=datetime.now)
    account_updated = db.Column(db.DateTime, onupdate=datetime.now, default=datetime.now)

    def hash_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
 
    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    def generate_auth_token(self):
        # When generating a new token, also set the token_expiry
        self.token = secrets.token_hex(16)
        self.token_expiry = datetime.now() + timedelta(hours=24)  # Set token to expire in 24 hours
        return self.token
    
class VerificationToken(db.Model):
    __tablename__ = 'verification_token'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    token = db.Column(db.String(255), nullable=False)
    expiry = db.Column(db.DateTime, nullable=False)    



    
@auth.verify_password
def verify_password(email, password):
    user = User.query.filter_by(email=email).first()
    if not user or not user.verify_password(password):
        App.logger.error('Authentication failed for user: %s', email)
        return False
    return user

def test_db_connection():
    try:
        with db.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        App.logger.info("Database connection successful")
        return True
    except Exception as e:
        App.logger.error(f"Database connection error: {e}")
        return False

@App.route('/healthz', methods=['GET'])
def health_check():
    if request.method != 'GET':
        App.logger.warning("405 Method Not Allowed - healthz endpoint")
        return make_response('', 405)

    if request.args or request.data or 'Content-Type' in request.headers:
        App.logger.warning("400 Bad Request - healthz endpoint")
        return make_response('', 400)

    if not test_db_connection():
        App.logger.error("503 Service Unavailable - Database connection failed")
        return make_response('', 503)

    response = make_response('', 200)
    response.headers['Cache-Control'] = 'no-cache'
    App.logger.info("200 OK - healthz endpoint successful")
    return response

# @App.route('/v1/user', methods=['POST'])
# def create_user():
#     data = request.get_json()

#     required_fields = ['email', 'password', 'first_name', 'last_name']
#     for field in required_fields:
#         if not data.get(field):
#             App.logger.warning(f"400 Bad Request - {field} cannot be null or empty")
#             return make_response(jsonify({'error': f'{field} cannot be null or empty'}), 400)

#     try:
#         hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
#         new_user = User(email=data['email'], password=hashed_password,
#                         first_name=data['first_name'], last_name=data['last_name'])
#         db.session.add(new_user)
#         db.session.commit()
#         App.logger.info(f"User created: {data['email']}")
#         user_data = {
#             'email': new_user.email,
#             'first_name': new_user.first_name,
#             'last_name': new_user.last_name
#         }
#         return jsonify(user_data), 201
#     except IntegrityError:
#         App.logger.error(f"User with this email already exists: {data['email']}")
#         return make_response(jsonify({'error': 'User with this email already exists'}), 400)

@App.route('/v1/user', methods=['POST'])
def create_user():
    data = request.get_json()

    required_fields = ['email', 'password', 'first_name', 'last_name']
    for field in required_fields:
        if not data.get(field):
            App.logger.warning(f"400 Bad Request - {field} cannot be null or empty")
            return make_response(jsonify({'error': f'{field} cannot be null or empty'}), 400)

    try:
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        new_user = User(email=data['email'], password=hashed_password,
                        first_name=data['first_name'], last_name=data['last_name'])
        db.session.add(new_user)
        db.session.commit()

        # Publish message to Pub/Sub topic
        publish_message(data)

        App.logger.info(f"User created: {data['email']}")
        user_data = {
            'email': new_user.email,
            'first_name': new_user.first_name,
            'last_name': new_user.last_name
        }
        return jsonify(user_data), 201
    except IntegrityError:
        App.logger.error(f"User with this email already exists: {data['email']}")
        return make_response(jsonify({'error': 'User with this email already exists'}), 400)

def publish_message(data):
    project_id = 'csye6225-assignment3'  # Replace with your Google Cloud project ID
    topic_name = 'verify_email'  # Replace with your Pub/Sub topic name

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)

    message = json.dumps(data).encode('utf-8')

    future = publisher.publish(topic_path, data=message)
    future.result()

    App.logger.info(f"Message published to Pub/Sub topic: {topic_name}")



@App.route('/v1/user/self', methods=['PUT'])
@auth.login_required
def update_user():
    current_user = User.query.filter_by(email=auth.current_user().email).first()
    data = request.get_json()
    allowed_fields = ['first_name', 'last_name', 'password']

    for field in allowed_fields:
        if field in data and (not data[field] or data[field].isspace()):
            App.logger.warning(f"400 Bad Request - {field} cannot be null or empty for user update")
            return make_response(jsonify({'error': f'{field} cannot be null or empty'}), 400)

    if 'password' in data:
        data['password'] = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    for key, value in data.items():
        setattr(current_user, key, value)

    try:
        db.session.commit()
        App.logger.info(f"User {current_user.email} updated successfully")
    except Exception as e:
        db.session.rollback()
        App.logger.error(f"Error updating user {current_user.email}: {e}")
        return make_response('', 500)

    return make_response('', 200)

@App.route('/v1/user/self', methods=['GET'])
@auth.login_required
def get_user():
    current_user = User.query.filter_by(email=auth.current_user().email).first()
    if not current_user:
        App.logger.error(f"User not found: {auth.current_user()}")
        return make_response('', 404)

    user_data = {
        'id': current_user.id,
        'email': current_user.email,
        'first_name': current_user.first_name,
        'last_name': current_user.last_name,
        'account_created': current_user.account_created,
        'account_updated': current_user.account_updated
    }
    App.logger.info(f"User data retrieved for: {current_user.email}")
    return jsonify(user_data)


@App.route('/v1/user/verify', methods=['GET'])
def verify_user():
    token = request.args.get('token')
    if not token:
        return jsonify({'message': 'Missing token'}), 400

    verification_token = VerificationToken.query.filter_by(token=token).first()
    if not verification_token:
        return jsonify({'message': 'Invalid token'}), 400

    user = User.query.filter_by(email=verification_token.email).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if user.isverified:
        return jsonify({'message': 'User already verified'}), 400

    if (user.token_expiry and datetime.now() > user.token_expiry):
        return jsonify({'message': 'Token expired'}), 400

    user.isverified = True
    user.token = None
    user.token_expiry = None

    try:
        db.session.commit()
        App.logger.info(f"User {user.email} verified successfully")
        return jsonify({'message': 'User verified successfully'}), 200
    except Exception as e:
        db.session.rollback()
        App.logger.error(f"Error verifying user {user.email}: {e}")
        return jsonify({'message': 'Error verifying user'}), 500


if __name__ == '__main__':
    with App.app_context():
        db.create_all()
    App.logger.info("Service started")
    App.run(host='0.0.0.0', port=5000, debug=True)

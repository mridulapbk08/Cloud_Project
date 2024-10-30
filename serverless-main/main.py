import os
import json
import base64
import requests
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import functions_framework
import uuid  
from sqlalchemy_utils import database_exists, create_database
import os
 

load_dotenv()
app = Flask(__name__)
 
 

MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN')
MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
DATABASE_URL = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
db = SQLAlchemy(app)
migrate = Migrate(app, db)
engine = create_engine(DATABASE_URL)
 
class VerificationToken(db.Model):
    __tablename__ = 'verification_tokens'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    token = db.Column(db.String(255), nullable=False)
    expiry = db.Column(db.DateTime, nullable=False)
 
if not database_exists(engine.url):
   create_database(engine.url)
with app.app_context():
    db.create_all()
 
def generate_verification_token(email):
    try:
        token = str(uuid.uuid4())
        print("Created token {}".format(token))
        expiry = datetime.now(timezone.utc) + timedelta(minutes=2)  
        new_token = VerificationToken(email=email, token=token, expiry=expiry)
        db.session.add(new_token)
        db.session.commit()
        print("Database token {}".format(token))
        return token
    except Exception as e:
        print(f"Error generating or storing the verification token: {e}")
        db.session.rollback()  
        return None
 
 
def send_verification_email(email, first_name, token):
    verification_link = f"https://mridulaprabhakar.me/v1/user/verify?token={token}"
    text_content = f"Hi {first_name},\n\nPlease click the following link to verify your email address: {verification_link}\n\nThank you for joining us!\n\nIf you did not request this, please ignore this email."
    html_content = f"""
<html>
<body>
<p>Hi {first_name},</p>
<p>Thank you for signing up. Please click the button below to verify your email address and get started:</p>
<p><a href='{verification_link}' style='display: inline-block; background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;'>Verify Email</a></p>
<p>If the button doesn't work, please copy and paste the following link into your browser:</p>
<p><a href='{verification_link}'>{verification_link}</a></p>
<p>If you did not create an account using this email address, please ignore this email.</p>
</body>
</html>
    """

    response = requests.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
        auth=("api", MAILGUN_API_KEY),
        data={
            "from": f"Your App Name <mailgun@{MAILGUN_DOMAIN}>",
            "to": email,
            "subject": "Action Required: Please Verify Your Email Address",
            "text": text_content,
            "html": html_content
        }
    )
    print(f"Mailgun response: {response.status_code}, {response.text}")
    return response

 
 
@functions_framework.cloud_event
def hello_pubsub(cloud_event):
    with app.app_context():
        message_data = base64.b64decode(cloud_event.data["message"]["data"])
        message_dict = json.loads(message_data)
 
        email = message_dict['email']
        first_name = message_dict['first_name']
        token = generate_verification_token(email)
 
        # Send verification email
        print("Beofre sending {}".format(token))
        response = send_verification_email(email, first_name, token)
        if response.status_code == 200:
            print("Email sent successfully")
        else:
            print(f"Failed to send email: {response.text}")

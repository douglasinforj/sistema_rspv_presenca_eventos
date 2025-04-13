from django.conf import settings
from django.utils.crypto import get_random_string
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime, timedelta

def generate_token(email):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    return serializer.dumps(email, salt='email-confirm')

def verify_token(token, max_age=86400):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=max_age)
        return email
    except:
        return None
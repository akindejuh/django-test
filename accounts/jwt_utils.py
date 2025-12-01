import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings


def generate_token(user):
    payload = {
        'user_id': user.id,
        'email': user.email,
        'user_type': user.user_type,
        'exp': datetime.now(timezone.utc) + timedelta(days=1),
        'iat': datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


def decode_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

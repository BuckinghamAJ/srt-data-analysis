from .login_gov_security import (OIDCSecurityManager, CustomSsoSecurityManager)
import os
import jwt
from datetime import datetime, timedelta
from authlib.common.security import generate_token
import logging
logger = logging.getLogger()


def generate_client_assertion(client_id, token_endpoint):
    private_key = os.getenv('SUPERSET_SECRET_KEY', 'YOUR_OWN_RANDOM_GENERATED_SECRET_KEY')
    private_key = bytes(private_key, 'utf-8')

    jwt_id = generate_token(32)
    now = datetime.utcnow()
    exp = now + timedelta(minutes=5)

    claims = {
        'iss': client_id,
        'sub': client_id,
        'aud': token_endpoint,
        'jti': jwt_id,
        'exp': int(exp.timestamp())
    }

    print("Claims: {0}".format(claims))

    cl_assert = None
    try:
        cl_assert = jwt.encode(claims, private_key, algorithm='RS256')
    except Exception as e:
        logger.error("Exception: {0}".format(e))
    
    return cl_assert

from .login_gov_security import (OIDCSecurityManager)
import os
import jwt
from datetime import datetime, timedelta, timezone
from authlib.common.security import generate_token
import logging
logger = logging.getLogger()



from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

def generate_client_assertion(client_id, token_endpoint):
    cert_path = os.path.join(os.path.dirname(__file__), '../../../certs/')
    
    private_key = None

    with open(os.path.join(cert_path, 'private.pem'), 'rb') as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend()
        )

    jwt_id = generate_token(32)
    now = datetime.now(timezone.utc)
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

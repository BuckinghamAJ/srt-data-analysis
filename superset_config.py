import os
from flask_appbuilder.security.manager import AUTH_OAUTH, AUTH_OID
from dotenv import load_dotenv
from srt_superset.security import OIDCSecurityManager, generate_client_assertion
from apscheduler.schedulers.gevent import GeventScheduler

background_scheduler = GeventScheduler()
load_dotenv()  # take environment variables from .env.



# Superset specific config
# Set superset vnv to path of this file
# export SUPERSET_CONFIG_PATH=/path/to/superset_config.py

ROW_LIMIT = 5000

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CERT_DIR = os.path.join(BASE_DIR, 'certs')
CONF_DIR = os.path.join(BASE_DIR, 'conf')

# Flask App Builder configuration
# Your App secret key will be used for securely signing the session cookie
# and encrypting sensitive information on the database
# Make sure you are changing this key for your deployment with a strong key.
# Alternatively you can set it with `SUPERSET_SECRET_KEY` environment variable.
# You MUST set this for production environments or the server will not refuse
# to start and you will see an error in the logs accordingly.
SECRET_KEY = os.getenv('SUPERSET_SECRET_KEY', 'YOUR_OWN_RANDOM_GENERATED_SECRET_KEY')


# COOKIES
debug = True if os.getenv('DEBUG') == 'True' else False

if debug:
      SESSION_COOKIE_SAMESITE = None
      SESSION_COOKIE_SECURE = False 
      SESSION_COOKIE_HTTPONLY = False


# The SQLAlchemy connection string to your database backend
# This connection defines the path to the database that stores your
# superset metadata (slices, connections, tables, dashboards, ...).
# Note that the connection information to connect to the datasources
# you want to explore are managed directly in the web UI
db_string = None
if os.getenv('VCAP_SERVICES'):
      db_string = os.getenv('DATABASE_URL')
      # SQLAlchemy 1.4 removed the deprecated postgres dialect name, the name postgresql must be used instead now.
      if db_string and db_string.startswith("postgres://"):
            db_string = db_string.replace("postgres://", "postgresql://", 1)
elif os.getenv('SUPERSET_META_DB'):
      db_string = os.getenv('SUPERSET_META_DB')

if db_string:
      SQLALCHEMY_DATABASE_URI = db_string 

# Flask-WTF flag for CSRF
WTF_CSRF_ENABLED = True if not debug else False
# Add endpoints that need to be exempt from CSRF protection
WTF_CSRF_EXEMPT_LIST = []
# A CSRF token that expires in 1 year
WTF_CSRF_TIME_LIMIT = 60 * 60 * 24 * 365

# Set this API key to enable Mapbox visualizations
MAPBOX_API_KEY = ''

# Start application with gunicorn in prod:
"""
gunicorn -w 10 \
      -k gevent \
      --worker-connections 1000 \
      --timeout 120 \
      -b  0.0.0.0:8080 \
      --limit-request-line 0 \
      --limit-request-field_size 0 \
      "superset.app:create_app()"
"""

# MAX.GOV User Authentication
# Set the authentication type to OAuth
AUTH_TYPE = AUTH_OAUTH

SUPERSET_CLIENT_ID= os.getenv('SUPERSET_CLIENT_ID')
NONCE_SECRET = os.getenv('NONCE_SECRET')

REDIRECT_URL = os.getenv('REDIRECT_URL')

OAUTH_PROVIDERS = [
    {   'name':'login_gov',
        'token_key':'access_token', # Name of the token in the response of access_token_url
        'icon':'fa-address-card',   # Icon for the provider
        'remote_app': {
          'client_id':SUPERSET_CLIENT_ID,  # Client Id (Identify Superset application)
          #'client_secret':'MySecret', # Secret for this Client Id (Identify Superset application)
          'api_base_url': 'https://idp.int.identitysandbox.gov/api/',
          'server_metadata_url': 'https://idp.int.identitysandbox.gov/.well-known/openid-configuration',
          "jwks_uri": 'https://idp.int.identitysandbox.gov/api/openid_connect/certs',
          'access_token_url':'https://idp.int.identitysandbox.gov/api/openid_connect/token',
          'access_token_params':{
                'client_assertion': generate_client_assertion(SUPERSET_CLIENT_ID, 'https://idp.int.identitysandbox.gov/api/openid_connect/token'),
                'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
                'grant_type': 'authorization_code'
          },
          'authorize_params':{
                'acr_values':'http://idmanagement.gov/ns/assurance/ial/1',
                'scope': 'openid email profile',               # Scope for the Authorization
                'nonce': NONCE_SECRET,
                'redirect_uri': REDIRECT_URL
            },
      }        
    }
]

def update_client_assertion():
      client_assertion = generate_client_assertion(SUPERSET_CLIENT_ID, 'https://idp.int.identitysandbox.gov/api/openid_connect/token')
      OAUTH_PROVIDERS[0]['remote_app']['access_token_params']['client_assertion'] = client_assertion

background_scheduler.add_job(update_client_assertion, 'interval', minutes=4)
background_scheduler.start()

# Will allow user self registration, allowing to create Flask users from Authorized User
AUTH_USER_REGISTRATION = True

# The default user self registration role
AUTH_USER_REGISTRATION_ROLE = "Public"


CUSTOM_SECURITY_MANAGER = OIDCSecurityManager

OIDC_INTROSPECTION_AUTH_METHOD='bearer'
OIDC_TOKEN_TYPE_HINT = 'access_token'
OIDC_CLIENT_SECRETS= os.path.join(CONF_DIR, 'client_secrets.json')
OIDC_SERVER_METADATA_URL='https://idp.int.identitysandbox.gov/.well-known/openid-configuration'

"""
# OpenID Connect Setting

OIDC_SCOPES=['openid', 'email']

"""
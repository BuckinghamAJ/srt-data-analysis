from flask import redirect, request
from flask_appbuilder.security.manager import AUTH_OID, AUTH_OAUTH
from superset.security import SupersetSecurityManager
from flask_oidc import OpenIDConnect
from flask_appbuilder.security.views import AuthOIDView, AuthOAuthView
from flask_login import login_user
from urllib.parse import quote
from flask_appbuilder.views import ModelView, SimpleFormView, expose
import logging

logger = logging.getLogger()

class OIDCSecurityManager(SupersetSecurityManager):

    def __init__(self, appbuilder):
        super(OIDCSecurityManager, self).__init__(appbuilder)
        if self.auth_type == AUTH_OID:
            self.oid = OpenIDConnect(self.appbuilder.get_app)
        self.authoidview = AuthOIDCView
        #self.authoauthview = AuthOIDCView

    
    def oauth_user_info(self, provider, response=None):
        logger.info("Oauth2 provider: {0}.".format(provider))
        if provider == 'login_gov':

            me = self.appbuilder.sm.oauth_remotes[provider].get('openid_connect/userinfo')
            data = me.json()
            logger.info("user logging in through login.gov: {0}".format(data['email']))
            return { 'email' : data['email'], 'id' : data['sub'], 'username' : data['email'], 'first_name':'', 'last_name':''} 


class AuthOIDCView(AuthOAuthView):

    @expose('/login/', methods=['GET', 'POST'])
    def login(self, flag=True):
        logger.info('Logging In!')
        sm = self.appbuilder.sm
        oidc = sm.oid
        superset_roles = ["Admin", "Alpha", "Gamma", "Public", "granter", "sql_lab"]
        default_role = "Public"
        
        @self.appbuilder.sm.oid.require_login
        def handle_login():
            logger.info(f"User: {oidc.user_getfield('email')}")
            user = sm.auth_user_oid(oidc.user_getfield('email'))
            logger.info(f"User: {user}")
            if user is None:
                info = oidc.user_getinfo(['sub', 'given_name', 'family_name', 'email', 'roles'])
                logger.info(f"OIDC Info: {vars(info)}")
                roles = [role for role in superset_roles if role in info.get('roles', [])]
                roles += [default_role, ] if not roles else []
                user = sm.add_user(info.get('sub'), info.get('given_name'), info.get('family_name'),
                                   info.get('email'), [sm.find_role(role) for role in roles])

            login_user(user, remember=False)
            return redirect(self.appbuilder.get_url_for_index)

        return handle_login()

    @expose('/logout/', methods=['GET', 'POST'])
    def logout(self):
        oidc = self.appbuilder.sm.oid

        oidc.logout()
        super(AuthOIDCView, self).logout()
        redirect_url = request.url_root.strip('/') + self.appbuilder.get_url_for_login

        return redirect(oidc.client_secrets.get('issuer') + '/protocol/openid-connect/logout?redirect_uri=' + quote(redirect_url))
    


class OAuth_ODICView(AuthOAuthView):
    # TODO: Update the callback with the proper data returned in the callback.
    @expose('/oidc_callback/')
    def oidc_callback(self):
        pass
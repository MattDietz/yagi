import json

import httplib2

import yagi.config
import yagi.log


LOG = yagi.log.logger


class Auth(object):
    #Messy, but cache the token in the class
    token = None

    @staticmethod
    def no_auth(*args, **kwargs):
        pass

    @staticmethod
    def http_basic_auth(conn, headers, force=False):
        user = yagi.config.get("handler_auth", "user")
        key = yagi.config.get("handler_auth", "key")
        if user and key:
            conn.add_credentials(user, key)

    @staticmethod
    def rax_auth(conn, headers, force=False):
        if Auth.token:
            return Auth.token
        user = yagi.config.get("handler_auth", "user")
        key = yagi.config.get("handler_auth", "key")
        tenant = yagi.config.get("handler_auth", "tenant")
        auth_server = yagi.config.get("handler_auth", "auth_server")
        req = httplib2.Http()
        body = {"auth": {
                    "RAX-KSKEY:apiKeyCredentials": {
                        "username": user,
                        "apiKey": key,
                        "tenantName": tenant}}}
        auth_headers = {}
        auth_headers["User-Agent"] = "Yagi"
        auth_headers["Accept"] = "application/json"
        auth_headers["Content-Type"] = "application/json"
        req.follow_all_redirects = True
        LOG.info("Contacting RAX auth server %s" % auth_server)
        res, body = req.request(auth_server, "POST", body=json.dumps(body),
                                headers=auth_headers)
        # Why 200? it's creating something :-/
        if res.status != 200:
            raise Exception("Authentication failed")
        LOG.info("Token received")
        Auth.token = json.loads(body)["access"]["token"]["id"]
        headers["X-Auth-Token"] = Auth.token


def get_auth_method(method=None):
    if not method:
        method = yagi.config.get("handler_auth", "method")
    if hasattr(Auth, method):
        return getattr(Auth, method)
    return None

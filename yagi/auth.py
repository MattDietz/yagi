import json

import httplib2

import yagi.config
import yagi.log


LOG = yagi.log.logger


token = None


def no_auth(*args, **kwargs):
    pass


def http_basic_auth(conn, headers, force=False):
    user = yagi.config.get("handler_auth", "user")
    key = yagi.config.get("handler_auth", "key")
    if user and key:
        conn.add_credentials(user, key)


def rax_auth(conn, headers, force=False):
    global token
    if token:
        return token
    user = yagi.config.get("handler_auth", "user")
    key = yagi.config.get("handler_auth", "key")
    ssl_check = not (yagi.config.get("handler_auth", "validate_ssl",
                         default=False) == "True")
    auth_server = yagi.config.get("handler_auth", "auth_server")
    req = httplib2.Http(disable_ssl_certificate_validation=ssl_check)
    body = {"auth": {
                "passwordCredentials": {
                    "username": user,
                    "password": key,
                    }}}
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
        raise Exception("Authentication failed with HTTP Status %d" %
                                res.status)
    LOG.info("Token received")
    token = json.loads(body)["access"]["token"]["id"]
    headers["X-Auth-Token"] = token


def get_auth_method(method=None):
    if not method:
        method = yagi.config.get("handler_auth", "method")
    if method in globals():
        return globals()[method]
    return None

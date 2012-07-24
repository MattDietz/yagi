
import errno
import httplib
import httplib2
import socket


class ResponseTooLargeError(httplib2.HttpLib2ErrorWithResponse):
    pass


class LimitingBodyHttp(httplib2.Http):

    """ This is a patched form of httplib2's Http class that is designed to
    reject reading response bodies that are too large to handle.

    By default httplib2 simply reads the whole body of the response into
    memory. This will read at most a certain size.
    """

    def __init__(self, max_body_size=1024 * 40, **kw):
        self.max_body_size = max_body_size
        self.follow_all_redirects = True
        super(LimitingBodyHttp, self).__init__(**kw)

    def _conn_request(self, conn, request_uri, method, body, headers):
        for i in range(2):
            try:
                if conn.sock is None:
                    conn.connect()
                conn.request(method, request_uri, body, headers)
            except socket.timeout:
                raise
            except socket.gaierror:
                conn.close()
                raise httplib2.ServerNotFoundError("Unable to find the server "
                                                   "at %s" % conn.host)
            except httplib2.ssl_SSLError:
                conn.close()
                raise
            except socket.error, e:
                err = 0
                if hasattr(e, 'args'):
                    err = getattr(e, 'args')[0]
                else:
                    err = e.errno
                if err == errno.ECONNREFUSED:  # Connection refused
                    raise
            except httplib.HTTPException:
                # Just because the server closed the connection doesn't
                # apparently mean that the server didn't send a response.
                if conn.sock is None:
                    if i == 0:
                        conn.close()
                        conn.connect()
                        continue
                    else:
                        conn.close()
                        raise
                if i == 0:
                    conn.close()
                    conn.connect()
                    continue
            try:
                response = conn.getresponse()
            except (socket.error, httplib.HTTPException):
                if i == 0:
                    conn.close()
                    conn.connect()
                    continue
                else:
                    raise
            else:
                content = ""
                if method == "HEAD":
                    response.close()
                else:
                    content = response.read(self.max_body_size + 1)
                    if len(content) > self.max_body_size:
                        #Too large. Drop the connection on the floor.
                        response.close()
                        conn.close()
                        raise ResponseTooLargeError(
                              "The response was larger than the maximum"
                              " size (%s) allowed" % self.max_body_size,
                              response,
                              content)
                response = httplib2.Response(response)
                if method != "HEAD":
                    content = httplib2._decompressContent(response, content)
            break
        return (response, content)

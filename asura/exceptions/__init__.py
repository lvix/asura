from werkzeug.wrappers import Response 

content_type = 'text/html; charset=UTF-8'

ERROR_MAP = {
    '2': Response('<h1>E2 File not found</h1>', content_type=content_type, status=500), 
    '13': Response('<h1>E13 No read permission</h1>', content_type=content_type, status=500), 
    '401': Response('<h1>401 Unknown or Unsupport Method</h1>', content_type=content_type, status=401), 
    '404': Response('<h1>404 Source Not Found </h1>', content_type=content_type, status=404), 
    '503': Response('<h1>503 Unknown Function Type </h1>', content_type=content_type, status=503), 
}


class AsuraException(Exception):

    def __init__(self, code='', message='Error'):
        self.code = code 
        self.message = message 

    def __str__(self):
        return self.message 


class EndpointExistsError(AsuraException):
    def __init__(self, message='Endpoint exists'):
        super(EndpointExistsError, self).__init__(message)

class URLExistsError(AsuraException):
    def __init__(self, message='URL exists'):
        super(URLExistsError, self).__init__(message)

class FileNotExistsError(AsuraException):
    def __init__(self, code='2', message='File not found'):
        super(FileNotExistsError, self).__init__(code, message) 

class RequireReadPermissionError(AsuraException):
    def __init__(self, code='13', message='Require read permission'):
        super(RequireReadPermissionError, self).__init__(code, message) 

class InvalidRequestMethodError(AsuraException):
    def __init__(self, code='401', message='Unknown or unsupported request method'):
        super(InvalidRequestMethodError, self).__init__(code, message)

class PageNotFoundError(AsuraException):
    def __init__(self, code='404', message='Source not found'):
        super(PageNotFoundError, self).__init__(code, message)

class UnknownFuncError(AsuraException):
    def __init__(self, code='503', message='Unknown function type'):
        super(UnknownFuncError, self).__init__(code, message)

def capture(f):

    def decorator(*args, **options):

        try:
            rep = f(*args, **options)
        except AsuraException as e:
            if e.code in ERROR_MAP and ERROR_MAP[e.code]:
                rep = ERROR_MAP[e.code]

                status = int(e.code) if int(e.code) >= 100 else 500

                return rep if isinstance(rep, Response) or rep is None else Response(rep(), 
                                                                                    content_type=content_type, 
                                                                                    status=status)
            else:
                raise e 
        return rep 
    return decorator 

def reload(code):
    def decorator(f):
        ERROR_MAP[str(code)] = f 
    return decorator 
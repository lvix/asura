from werkzeug.serving import run_simple
from werkzeug.wrappers import Response
from asura.wsgi_adapter import wsgi_app 

import asura.exceptions as exceptions 
from asura.helper import parse_static_key 
from asura.route import Route   
from asura.template_engine import replace_template 
from asura.session import create_session_id, session

import os, json

class ExecFunc(object):
    def __init__(self, func, func_type, **options):
        self.func = func 
        self.options = options 
        self.func_type = func_type 

# file type 
TYPE_MAP = {
    'css': 'text/css',  
    'js': 'text/js', 
    'png': 'image/png', 
    'jpg': 'image/jpg', 
    'jpeg': 'image/jpeg',
}

class Asura(object):

    template_folder = None 

    def __init__(self, static_folder='static', template_folder='template', session_path='.session'):
        self.host = '127.0.0.1' # ????
        self.port = 8086 # ????
        # 
        self.url_map = {}
        self.satic_map = {} 
        self.function_map = {}
        self.static_folder = static_folder 

        self.template_folder = template_folder

        self.route = Route(self) # the route decorator 

        Asura.template_folder = self.template_folder

        self.session_path = session_path
    # ??
    # def dispatch_request(self, request):
    #     status = 200 # HTTP ???? 200???????

    #     headers = {
    #         'Server': 'Asura Framework'
    #     }

    #     # ???? WSGI ??????? WSGI ??
    #     return Response('<h1>Asura Framework</h1>', 
    #                     content_type='text/html',
    #                     headers=headers, 
    #                     status=status
    #                     )
    @exceptions.capture
    def dispatch_static(self, static_path):
        if os.path.exists(static_path):
            # get filename suffix
            key = parse_static_key(static_path)

            # get file type 
            doc_type = TYPE_MAP.get(key, 'text/plain')

            # get file content
            with open(static_path, 'rb') as f:
                rep = f.read()

            # wrap and return a Response 

            return Response(rep, content_type=doc_type)
        else:
            raise exceptions.PageNotFoundError
            # return ERROR_MAP['404']

    @exceptions.capture
    def dispatch_request(self, request):

        # get rid of the domain part from the URL 
        # extract 'path/file' from http://aaa.com/path/file?xx=xx 
        # url will be  '/path/file'
        url = '/' + '/'.join(request.url.split('/')[3:]).split('?')[0]

        if url.find(self.static_folder) == 1 and url.index(self.satic_folder) == 1:
            endpoint = 'static'
            url = url[1:]
        else:
            endpoint = self.url_map.get(url, None)

        # define response headers 
        # usually "Server" would be IIS, Apache, Nginx and so on 
        
        cookies = request.cookies
        
        headers = {'Server': 'Asura'}

        if 'session_id' not in cookies:
            headers = {
                'Set-Cookie': 'session_id={}'.format(create_session_id()), 
                'Server': 'Asura', 
            }

        if endpoint is None:
            raise exceptions.PageNotFoundError
            # return ERROR_MAP['404']

        # get the execution function from function_map 
        exec_function = self.function_map[endpoint]

        # judging exec func type 
        if exec_function.func_type == 'route':
            ''' solving route request '''
            if request.method in exec_function.options.get('methods'):

                # whether the route exec function need to run with Request
                argcount = exec_function.func.__code__.co_argcount 

                if argcount > 0:
                    rep = exec_function.func(request)
                else:
                    rep = exec_function.func()
            else:
                ''' Unknown Request Methods'''
                raise exceptions.InvalidRequestMethodError
                # return ERROR_MAP[401]
        elif exec_function.func_type == 'view':
            ''' solving view '''
            # definitely needs Request 
            rep = exec_function.func(request)
        elif exec_function.func_type == 'static':
            
            # satic exec_function is dispatch_staic 
            return exec_function.func(url)
        else:
            ''' Unknown '''
            raise exceptions.UnknownFuncError
            # return ERROR_MAP['503']

        # status 200 means request succeeded 
        status = 200 
        content_type = 'text/html'

        if isinstance(rep, Response):
            return rep 
        # return a Response 
        return Response(rep, 
                        content_type='{}; charset=UTF-8'.format(content_type),
                        headers=headers, 
                        status=status,
                        )
    # ???? 
    def run(self, host=None, port=None, **options):
        """
           ???????????????????
        """

        
        # ?????????????
        for key, value in options.items():
            if value is not None:
                self.__setattr__(key, value)
        # map static exec function "dispatch_static"
        # to the endpoint "static"
        self.function_map['static'] = ExecFunc(func=self.dispatch_static, func_type='static')

        if host:
            self.host = host 
        
        if port:
            self.port = port 

        if not os.path.exists(self.session_path):
            os.mkdir(self.session_path)
        
        session.set_storage_path(self.session_path)

        session.load_local_session()
        # ??????????????
        # werkzeug ? run_simple 
        run_simple(hostname=self.host, port=self.port, application=self, **options)
    
    # ??? WSGI ???????
    def __call__(self, environ, start_response):
        return wsgi_app(self, environ, start_response)

    @exceptions.capture
    def add_url_rule(self, url, func, func_type, endpoint=None, **options):
        """
        add route rule 
        """
        if endpoint is None:
            endpoint = func.__name__ 

        if url in self.url_map:
            raise exceptions.URLExistsError     
    
        if endpoint in self.function_map and func_type != 'static':
            raise exceptions.EndpointExistsError 

        self.url_map[url] = endpoint 

        self.function_map[endpoint] = ExecFunc(func, func_type, **options)
    
    def bind_view(self, url, view_class, endpoint):
        self.add_url_rule(url, func=view_class.get_func(endpoint), func_type='view')
        
    def load_controller(self, controller):

        name = controller.__name__()

        for rule in controller.url_map:
            self.bind_view(rule['url'], rule['view'], name + '.' + rule['endpoint'])

def simple_template(path, **options):
    return replace_template(Asura, path, **options)

class ExecFunc:
    def __init__(self, func, func_type, **options):
        # execution function 
        self.func = func 
        # options 
        self.options = options 
        # function type 
        self.func_type = func_type 

def redirect(url, status_code=302):

    response = Response('', status=status_code)

    response.headers['location'] = url 

    return response 

def render_json(data):

    content_type = 'text/plain'

    if isinstance(data, dict) or isinstance(data, list):
        data = json.dumps(data)
        content_type = 'application/json'

    return Response(data, content_type='{}; charset=UTF-8'.format(content_type), status=200)


@exceptions.capture
def render_file(file_path, file_name=None):

    if os.path.exists(file_path):

        # added exception
        if not os.access(file_path, os.R_OK):
            raise exceptions.RequireReadPermissionError

        with open(file_path, 'rb') as f:
            content = f.read()

        if file_name is None:
            file_name = file_path.split('/')[-1]

        headers = {
            'Content-Disposition': 'attachment; filename="{}"'.format(file_name)
        }

        return Response(content, headers=headers, status=200)
    # return ERROR_MAP['404']
    raise exceptions.FileNotExitsError
from asura import Asura, simple_template, redirect, render_json, render_file
from asura.view import Controller
from asura.session import AuthSession, session 
from core.base_view import BaseView, SessionView
from core.database import dbconn

class Login(BaseView):
    def get(self, request):

        state = request.args.get('state', '1')
        return simple_template('layout.html', title='Register', 
                        message='Username:' if state ==1 else 'Username doesn\'t exist, try again')

    def post(self, request):

        ret = dbconn.execute('''SELECT * FROM user WHERE f_name = %(user)s''', request.form)
        if ret.rows ==1 :
            user = ret.get_first()['f_name']

            session.push(request, 'user', user)

            return redirect('/')
        return redirect('/login?state=0')

        # user = request.form['user']

        # session.push(request, 'user', user)

        # # return 'Login successfully, <a href=\'/\'>Go back</a>'
        # return redirect('/')

class Logout(SessionView):
    def get(self, request):
        session.pop(request, 'user')
        # return 'Logout successfully, <a href=\'/\'>Go back</a>'
        return redirect('/')

class Index(SessionView):
    def get(self, request):
        user = session.get(request, 'user')
        return simple_template('index.html', user=user, message='Welcome, ')

class Test(Index):
    def post(self, request):
        return 'This is a post request'

class API(BaseView):

    def get(self, request):
        data = {
            'name': 'Asura', 
            'lang': 'python', 
            'base': 'werkzeug', 
        }

        return render_json(data)

class Download(BaseView):

    def get(self, request):
        return  render_file('main.py')

class Register(BaseView):
    """docstring for Register"""
    def get(self, request):
        return simple_template('layout.html', title='Register', message='Input your username:')
    def post(self, request):

        ret = dbconn.insert('INSERT INTO user(f_name) VALUES(%(user)s)', request.form)

        if ret.suc:
            return redirect('/login')
        else:
            return render_json(ret.to_dict())
        

asura_url_map = [
    {
        'url': '/', 
        'view': Index,
        'endpoint': 'index',
    },
    {
        'url': '/test', 
        'view': Test, 
        'endpoint': 'test', 
    },
    {
        'url': '/login', 
        'view': Login,  
        'endpoint': 'login',
    },
    {
        'url': '/logout', 
        'view': Logout, 
        'endpoint': 'logout',
    },
    {
        'url': '/api', 
        'view': API, 
        'endpoint': 'api',
    },
    {
        'url': '/download', 
        'view': Download, 
        'endpoint': 'download',
    },
    {
        'url': '/register', 
        'view': Register, 
        'endpoint': 'register',
    },

]

app = Asura()
index_controller = Controller('index', asura_url_map)
app.load_controller(index_controller)

# @app.route('/index', methods=['GET'])
# def index():
#     return 'This is a route testing page'

# @app.route('/test/js')
# def test_js():
#     return '<script scr="/static/test.js"></script>'

app.run()

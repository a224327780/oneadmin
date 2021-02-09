import json
import logging
import os
from importlib import import_module

from bottle import request, static_file, default_app, abort, response, auth_basic

from src.common import fail
from src.oneadmin import OneAdmin
from src.onedrive import OneDrive, OneDriveException

DEFAULT_FORMATTER = '%(asctime)s[%(filename)s:%(lineno)d][%(levelname)s]:%(message)s'
logging.basicConfig(format=DEFAULT_FORMATTER, level=logging.INFO)

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception as e:
    logging.debug(e)

app = default_app()


def authenticated(user, password):
    auth_user = os.environ.get('AUTH_USERNAME', 'root')
    auth_pwd = os.environ.get('AUTH_PASSWORD')
    if user != auth_user or password != auth_pwd:
        return False
    return True


@app.route('/favicon.ico')
def favicon():
    return ''


@app.route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root='static')


@app.route('/', method='GET')
@auth_basic(authenticated)
def index():
    return OneAdmin.render('index')


@app.route('/:controller', method=['GET', 'POST'])
@app.route('/:controller/:action', method=['GET', 'POST'])
@auth_basic(authenticated)
def route_index(controller, action=None):
    try:
        m = import_module(f'src.api.{controller}')
        if not action:
            action = 'index'

        if m:
            one_drive = OneDrive()
            if controller != 'install':
                OneAdmin.before_request(one_drive)

            _action = f'{controller}_{action}'
            if hasattr(m, _action):
                return getattr(m, f'{controller}_{action}')(one_drive)
    except ModuleNotFoundError as e2:
        logging.debug(e2)
    return '<html><head><title>404 Not Found</title></head><body><center><h1>404 Not Found</h1></center><hr><center>' \
           'nginx</center></body></html>'


@app.error(500)
def error500(e1):
    if isinstance(e1.exception, OneDriveException):
        data = json.loads(e1.exception.message)
        error = data.get('error')
        response.content_type = 'application/json'
        return json.dumps(fail(error.get('message'), data=data))
    if e1.traceback:
        return app.default_error_handler(e1)
    return e1.body


if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=os.environ.get('DEBUG', False))

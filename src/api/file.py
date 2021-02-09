import logging
from datetime import datetime

from bottle import request, redirect

from src.common import format_size
from src.oneadmin import OneAdmin
from src.onedrive import OneDrive


def file_list(one_drive: OneDrive):
    params = dict(request.query)
    items = []
    page_url = None
    folder = params.get('folder', '')
    try:
        data = one_drive.file_list(**params)
        type_id = 'site_id' if params.get('site_id') else 'user_id'
        for item in data['value']:
            item['lastModifiedDateTime'] = datetime.strptime(item['lastModifiedDateTime'], '%Y-%m-%dT%H:%M:%SZ')
            item['size'] = format_size(item['size'])
            _folder = f"{folder.strip('/')}/{item.get('name')}"
            if item.get('folder'):
                item['url'] = f"/file/list?id={params['id']}&{type_id}={params.get(type_id)}&folder={_folder}"
                item['size'] = item.get('folder').get('childCount')
            else:
                item['url'] = f"/file/detail?id={params['id']}&{type_id}={params.get(type_id)}&file_id={_folder}"
            items.append(item)
        page_url = data.get('@odata.nextLink')
    except Exception as e:
        logging.error(e)
        items = False
    return OneAdmin.render('file/list', items=items, page_url=page_url)


def file_detail(one_drive: OneDrive):
    params = dict(request.query)
    data = one_drive.get_file(**params)
    download_url = data.get('@microsoft.graph.downloadUrl')
    return redirect(download_url)

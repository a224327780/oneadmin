import json
import math
from datetime import datetime, timezone, timedelta


def success(data=None, message=''):
    return {'status': 0, 'msg': message, 'data': data}


def fail(message='', status=1, data=None):
    return {'status': status, 'msg': message, 'data': data}


def print_json(json_data):
    return json.dumps(json_data, indent=4)


def format_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    return f'{round(size_bytes / p, 2)}{size_name[i]}'


def get_time():
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    return utc_dt.astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')

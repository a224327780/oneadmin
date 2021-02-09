import os
import time
from importlib import import_module

from bottle import template, Bottle, request, redirect, abort
from pymongo import MongoClient

from src.common import get_time
from src.onedrive import OneDrive


class OneAdmin:
    app = None
    mongo_db = None

    @classmethod
    def get_app(cls):
        if not cls.app:
            cls.app = Bottle(autojson=False)
            cls.init_route()
        return cls.app

    @classmethod
    def get_mongo(cls):
        if not cls.mongo_db:
            mongo_uri = os.environ.get('MONGO_URI')
            client = MongoClient(mongo_uri, connectTimeoutMS=5000, socketTimeoutMS=5000)
            db = client.get_database('one_drive')
            cls.mongo_db = db['one_admin']
        return cls.mongo_db

    @classmethod
    def init_route(cls):
        import_module('src.api.install')

    @classmethod
    def get_drives(cls):
        groups = {}
        mongodb = cls.get_mongo()
        for item in mongodb.find({}, {'_id': 1, 'one_type': 1}).sort('one_type', 1).sort('_id', 1):
            one_type = item.get('one_type')
            if not groups.get(one_type):
                groups[one_type] = []
            groups[one_type].append(item)
        return groups

    @classmethod
    def save_token(cls, name: str, data: dict):
        mongodb = cls.get_mongo()
        params = {
            'access_token': data.get('access_token'),
            'expires_time': int(time.time()) + 3500,
            'update_date': get_time()
        }
        return mongodb.update_one({'_id': name}, {'$set': params}).modified_count

    @classmethod
    def install(cls, params: dict):
        return OneAdmin.get_mongo().update_one({'_id': params.get('name')}, {'$set': params}, True)

    @classmethod
    def get_drive(cls, _id):
        mongodb = cls.get_mongo()
        return mongodb.find_one({'_id': _id})

    @classmethod
    def render(cls, tpl_name, layout=True, **kwargs):
        _id = request.query.get('id')
        kwargs.setdefault('_id', _id)
        kwargs.setdefault('request', request)
        content = template(f'{tpl_name}.html', **kwargs)
        if not layout:
            return content
        drives = cls.get_drives()
        return template('layout.html', content=content, drives=drives, **kwargs)

    @classmethod
    def before_request(cls, one_drive: OneDrive):
        _id = request.query.get('id')
        data = cls.get_drive(_id)
        if not data:
            redirect('/')

        not_time = int(time.time())
        expires_time = int(data.get('expires_time'))
        if expires_time <= not_time:
            _data = one_drive.get_ms_token(**data)

            access_token = _data.get('access_token')
            if not access_token:
                abort(text=f"[{_id}]: refresh token fail.")

            OneAdmin.save_token(_id, _data)
            data['access_token'] = access_token

        one_drive.access_token = data['access_token']


if __name__ == '__main__':
    one = OneDrive()

    # mongo.update_many({'one_type': 'A1'}, {"$unset": {"oauth_type": ""}})

    # drive = OneAdmin.get_drive('MNEW')
    # access = one.get_ms_token(**drive)
    # one.access_token = access['access_token']
    #
    # # OneAdmin.print_json(one.assign_license('0004@atcaoyufei.onmicrosoft.com', '94763226-9b3c-4e75-a931-5c89701abe66'))
    # #
    # # OneAdmin.print_json(one.file_list(user_id='b88a6c34-0abe-446b-b53b-e410024cdf64'))
    # # OneAdmin.print_json(one.get_drives('1a46e535-bbaa-46e6-b32b-2122ee656d4c'))
    # OneAdmin.print_json(one.user_list())

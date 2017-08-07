# -*- coding: utf-8 -*-

from pymongo import MongoClient
import logging
from haounits.cfgOptionTools import get_items_in_cfg, get_uri_relative_parent_package
from haounits.loggerDefTools import get_defTestLogger as getlog
import haomongodb as parent

__author__ = 'hao'

log = getlog(level=logging.DEBUG)
class gxmongo(object):
    __client = None
    __db = None

    class config():
        mongo_host = None
        mongo_db = None

    def __init__(self):
        self.__settings_file_path = get_uri_relative_parent_package(parent, 'mongodb.properties')
        connection_strings = get_items_in_cfg('mongodb', 'connection_strings', self.__settings_file_path)
        self.__client = MongoClient(connection_strings)

    @staticmethod
    def get_client(self):
        return gxmongo.__client

    def get_odbs(self):
        db_name = get_items_in_cfg('mongodb', 'odbs_name', self.__settings_file_path)
        return self.__client[db_name]

    def get_dstore(self):
        db_name = get_items_in_cfg('mongodb', 'dstore_name', self.__settings_file_path)
        return self.__client[db_name]

    def get_zhoastore(self):
        db_name = get_items_in_cfg('mongodb', 'zhoa_name', self.__settings_file_path)
        return self.__client[db_name]

    def get_repeatstore(self):
        db_name = get_items_in_cfg('mongodb', 'repeat_name', self.__settings_file_path)
        return self.__client[db_name]
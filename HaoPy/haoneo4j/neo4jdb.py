# -*- coding: utf-8 -*-

from py2neo import Graph
from haounits.cfgOptionTools import get_items_in_cfg, get_uri_relative_parent_package
import haoneo4j as parent

__author__ = 'hao'


class gxneo4j(object):
    __client = None

    def __init__(self):
        self.__settings_file_path = get_uri_relative_parent_package(parent, 'neo4j.properties')
        neo_path = get_items_in_cfg('neo4j', 'path', self.__settings_file_path)
        neo_usr = get_items_in_cfg('neo4j', 'user', self.__settings_file_path)
        neo_passwd = get_items_in_cfg('neo4j', 'password', self.__settings_file_path)
        host = get_items_in_cfg('neo4j', 'host', self.__settings_file_path)
        http_port = get_items_in_cfg('neo4j', 'http_port', self.__settings_file_path)
        bolt_port = get_items_in_cfg('neo4j', 'bolt_port', self.__settings_file_path)
        self.__client = Graph( bolt=True,user = neo_usr, password = neo_passwd, host = host, bolt_port= int(bolt_port), http_port = int(http_port))

    def get_conn(self):
        return self.__client




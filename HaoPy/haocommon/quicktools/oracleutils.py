# -*- coding: utf-8 -*-

import cx_Oracle
import traceback
import os
from haounits.cfgOptionTools import get_items_in_cfg, get_uri_relative_parent_package
import haocommon as parent
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

__author__ = 'hao'

class oracleutils():
    def __init__(self):
        self.__settings_file_path = get_uri_relative_parent_package(parent, 'settings.properties')
        connent_string = get_items_in_cfg('oracle', 'connent_string', self.__settings_file_path)
        ORACLE_HOME = get_items_in_cfg('oracle', 'ORACLE_HOME', self.__settings_file_path)
        os.environ.update({'ORACLE_HOME':ORACLE_HOME})
        self.db = cx_Oracle.connect(connent_string)

    def execute(self,sql):
        cursor = self.db.cursor()
        datacursor = cursor.execute(sql)
        for row in datacursor:
                yield  row

    def destory(self):
        self.db.close()

if __name__ == '__main__':
    o = oracleutils()
    c = o.execute("select * from user_tables")
    for r in c:
        print r
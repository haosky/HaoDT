# -*- coding: utf-8 -*-
from haounits.loggerDefTools import get_defTestLogger as getlog
from haocommon.quicktools.oracleutils import oracleutils
import logging
__author__ = 'hao'

log = getlog(level=logging.DEBUG)


class oracle_entry_extract:
    def __init__(self):
        self.ou = oracleutils()

    def extract_enterprise(self):
        entry_file=open('enterprise.data','w')
        sql = ''''''
        genf = self.ou.execute(sql)
        for r in genf:
            id = r[0]
            enterprise=r[1]

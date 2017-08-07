# -*- coding: utf-8 -*-

from haohbase.hbase_dao import hbase_dao
from haohbase.hbase.ttypes import TScan,TColumn
from haounits.cfgOptionTools import get_items_in_cfg, get_uri_relative_parent_package
import haostorm.check_repeat as mainparent
import haohbase as parent
import sys
import json
reload(sys)
sys.setdefaultencoding('utf8')

__author__ = 'hao'


class sim_sets():

    def __init__(self):
        self.__settings_file_path = get_uri_relative_parent_package(parent, 'hbase.properties')
        self.simlen = int(get_items_in_cfg('hbase', 'simlen', self.__settings_file_path))
        self.__sim_config_file_path = get_uri_relative_parent_package(mainparent, 'sim_settings.properties')
        table_config = 'hbase_table'
        self.caizheng_table = get_items_in_cfg(table_config, 'caizheng_table',
                                               self.__sim_config_file_path)
        self.splen = 12
        self.ks = ["project", "finical_unit", "finical_name", "date", "doc", "content", "unit", "finical"]

    def scan_data_rowprex(self,row,table,hase_self=False,len = 8,ks = None):
        # fs = " ColumnPaginationFilter(%d, %d) AND PrefixFilter('%s')" % ( 100,0,rowprex)
        rowprex = row[0:len] # 0
        columns = []
        if ks is None :
            ks = self.ks
        for k in ks:
            columns.append(TColumn(family='a', qualifier=k))
        fs = "PrefixFilter('%s')" %  rowprex
        scan = TScan(filterString=fs,
                     columns=columns)
        return self.scan_data_list(row if not hase_self else "",scan,table,len,ks)

    def scan_data(self):
        columns = []
        for k in self.ks:
            columns.append(TColumn(family='a', qualifier=k))
        scan = TScan(  # filterString=fs,
            columns=columns)
        return self.scan_data_main(scan)

    def scan_data_list(self,self_row,scan,table,len,ks = None):
        hd = hbase_dao()
        groups = []
        scanner = hd.open_scan(table, scan)
        r = hd.client.getScannerRows(scanner, 30)
        i = 0
        maxrow = 10
        while r:
            try:
                i += 1
                if i>= maxrow:
                    break
                for c in r:
                    row = c.row
                    if self_row == row:
                        continue
                    pk = row[0:len]  # simlen - 12
                    rowdata = {}
                    for cv in c.columnValues:
                        cm = cv.qualifier.strip()
                        if cm in ks:
                            rowdata.update({cm: cv.value})
                    groups.append({row: rowdata})
                r = hd.client.getScannerRows(scanner, 30)
            except:
                pass
        return groups

    def scan_data_main(self,scan):
        hd = hbase_dao()
        groups = {}
        scanner = hd.open_scan(self.caizheng_table, scan)
        r = hd.client.getScannerRows(scanner, 30)
        i = 0
        arts = 20
        while r:
            if i>=arts:
                break
            try:
                i += 1
                for c in r:
                    row = c.row
                    pk = row[0:self.simlen - self.splen]  # simlen - 12
                    filename = ''
                    title = ''
                    for cv in c.columnValues:
                        cm = cv.qualifier.strip()
                        if cm == 'filename':
                            filename=cv.value
                        if cm == 'content':
                            title = cv.value
                    if pk not in groups.keys():
                        groups.update({pk:[]})
                    groups[pk].append({filename:title})
                r = hd.client.getScannerRows(scanner, 30)
            except:
                pass

        result_grout = []
        for g,v in groups.items():
            if len(v) >= 2 :
                result_grout.append(v)
        return json.dumps(result_grout, ensure_ascii=False, indent=2)



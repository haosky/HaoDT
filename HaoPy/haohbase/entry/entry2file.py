# -*- coding: utf-8 -*-

from haohbase.hbase_dao import hbase_dao
from haohbase.hbase.ttypes import TScan,TColumn
import traceback
import sys
import json
reload(sys)
sys.setdefaultencoding('utf8')

__author__ = 'hao'


class entry2file():

    def scan_table_col(self,table,clos):
        hd = hbase_dao()
        groups = []
        scan = TScan(columns=[TColumn(family='a', qualifier=clos)])
        scanner = hd.open_scan(table, scan)
        r = hd.client.getScannerRows(scanner, 30)
        while r:
            try:
                for c in r:
                    groups.extend(c.row.split('、 '))
                r = hd.client.getScannerRows(scanner, 30)
            except:
                print traceback.format_exc()
        return groups

    def scan_content_type(self,writefile):
        hd = hbase_dao()
        scan = TScan(columns=[TColumn(family='a', qualifier='content'),TColumn(family='a', qualifier='bbdw'),TColumn(family='a', qualifier='fl_type')])
        scanner = hd.open_scan('CaiZhengMoNiSim', scan)
        r = hd.client.getScannerRows(scanner, 30)
        wf = open(writefile,'w')
        while r:
            try:
                for c in r:
                    rowdata = {}
                    for cv in c.columnValues:
                        cm = cv.qualifier.strip()
                        rowdata.update({cm: cv.value})
                        wf.write(json.dumps(rowdata,ensure_ascii=False).replace('\n',' ')+'\n')
                r = hd.client.getScannerRows(scanner, 30)
            except:
                print traceback.format_exc()
        wf.close()

    def write_file(self,wfile,sub_str,group):
        wo = open(wfile,'w')
        for line in group:
            wo.write('%s %s\n' % (line,sub_str))
        wo.close()

if __name__ == '__main__':
    e2f = entry2file()
    # gp = e2f.scan_table_col('Raw_Type','fl_type') # fl_type finical_name #Raw_Organial
    # e2f.write_file('rType','nz',gp)
    # gp1 = e2f.scan_table_col('Raw_Organial', 'bbdw')  # fl_type bbdw finical_name #Raw_Organial
    # e2f.write_file('rOrg', 'nz',gp1)

    e2f.scan_content_type('hrows3')
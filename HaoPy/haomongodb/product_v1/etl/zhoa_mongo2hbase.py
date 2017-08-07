# -*- coding: utf-8 -*-

from haomongodb.mongodbmaster import gxmongo
from haohbase.hbase_dao import hbase_dao
import traceback
from haohbase.hbase.ttypes import TColumnValue
import sys
reload(sys)
sys.setdefaultencoding('utf8')

__author__ = 'hao'

class zhoa_mongo2hbase():
    HBASE_TABLE = 'zhoa'

    def __init__(self):
        self.oaclient = gxmongo().get_zhoastore()

    def insert_hbase(self):
        '''智慧OA mongo插入hbase'''
        self.hd = hbase_dao()
        for sam_detail in self.oaclient['doc'].find():
            # "project","finical_unit","finical_name","date","doc","content", "unit","finical","fl_type","uuid","submiter"
            project = TColumnValue(family='a', qualifier='project',
                                          value=str(sam_detail['title']).encode('utf8'))

            finical_unit = TColumnValue(family='a', qualifier='finical_unit',
                                   value=str(""))

            finical_name = TColumnValue(family='a', qualifier='finical_name',
                                   value=str(""))

            date = TColumnValue(family='a', qualifier='date',
                                        value=str(sam_detail['datestr']))

            doc = TColumnValue(family='a', qualifier='doc',
                                value=str(sam_detail['docnum']))

            content = TColumnValue(family='a', qualifier='content',
                               value=str(sam_detail['content']))

            unit = TColumnValue(family='a', qualifier='unit',
                                   value=str(""))

            finical = TColumnValue(family='a', qualifier='finical',
                                value=str(sam_detail['level']))

            fl_type = TColumnValue(family='a', qualifier='fl_type',
                                   value=str(sam_detail['status']))

            uuid = TColumnValue(family='a', qualifier='uuid',
                                   value=str(sam_detail['_id']))

            submiter = TColumnValue(family='a', qualifier='submiter',
                                value=str(sam_detail['uploader']))

            rowkey =  sam_detail['_id']
            columnValues = [project,
                            finical_unit,
                            finical_name,
                            date,
                            doc,
                            content,
                            unit,
                            finical,
                            fl_type,
                            uuid,
                            submiter]

            print rowkey
            self.hd.put(zhoa_mongo2hbase.HBASE_TABLE, rowkey, columnValues)
        self.hd.close()

    def make_entry(self):
        import sources as source
        import json
        from haounits.cfgOptionTools import get_items_in_cfg, get_uri_relative_parent_package
        zhoa_keywrod_entry_relationship = get_uri_relative_parent_package(source, 'zhoa_keywrod_entry_relationship')
        fi = open(zhoa_keywrod_entry_relationship,"w")
        for sam_detail in self.oaclient['doc'].find():
            fi.write("%s|%s\n" % (sam_detail['title'],json.dumps(sam_detail['keywords'],ensure_ascii=False)))
        fi.close()

    def data_rebuild(self):
        '''更新数据操作'''
        from haocommon.quicktools.esutils import ElasitcUtil
        self.es = ElasitcUtil()
        res = self.es.scan_source(index='gdspecial_v2', doc_type='zhoa',query={})
        i = 0
        for row in res:
            idz = row['_id']
            source = row['_source']
            submiter = self.oaclient['doc'].find_one({'_id':idz})['uploader']
            source.update({"submiter": submiter})
            self.es.index(index='gdspecial_v2', doc_type='zhoa', id=idz, body=source)


if __name__ == '__main__':
    zhoa_mongo2hbase().data_rebuild()
# -*- coding: utf-8 -*-

import json
import logging

from haoneo4j import neo4junit
from haomongodb.product_v1.modles.mongodb_modles import TableCols
from haomongodb.mongodbmaster import gxmongo
from haocommon.product_v1.base_cyqoperator import  base_cyqoperator
from haounits.loggerDefTools import  get_defTestLogger as glog
from haoneo4j.neo4junit import neo4junit
__author__ = 'hao'

'''
关系插入neo4j
'''
class cyqoperator(base_cyqoperator):
    logLEVEL = logging.DEBUG

    def __init__(self,neo=None,mongodb=None ,logLEVEL=logging.INFO):
        base_cyqoperator.__init__(self, neo=neo,mongodb=mongodb, logLEVEL=logLEVEL)

    def operator(self):
         log = glog(level=cyqoperator.logLEVEL,clazz=cyqoperator)
         find_return =self.mongodb['TableCols'].find()
         for rep in find_return:
             rep.pop("_id")
             log.info(json.dumps(rep,ensure_ascii=False))
             keywords = self.keywords_int_cols(rep,'TABLE_COMMENTS')

             # 设置表的实体值
             labeldata = {
              'label': 'TableCols',
              'name': '%s__%s' % (rep['TABLE_NAME'],rep['COLUMN_NAME']),
              'properties': rep
             }
             labeldata['properties'].update({'_KEY':'%s__%s' % (rep['TABLE_NAME'],rep['COLUMN_NAME'])})
             self.entries.append(labeldata)

            # 设置关键字实体值
             for keyw in keywords :
                 self.entries.append({
                     'name': keyw,
                     'label':'keyword',
                     'properties': {'_KEY': '%s' % keyw}
                 })

             self.insert_entry()

             for keyw in keywords:
                # 设置关键字 for 表的关系
                 self.entry__relationship = base_cyqoperator.entry__relationship()
                 self.entry__relationship.relationship_name = 'KeyWordInTableCols'
                 self.entry__relationship.properties =  {'table': 'TableCols'}

                 # from 是关键字
                 self.entry__relationship.label_from =   {
                            '_KEY':keyw,
                             'label':'keyword',
                            'properties':{'_KEY': '%s' % keyw}
                    }

                 # to 是表实体
                 self.entry__relationship.label_to = {
                     '_KEY':  '%s__%s' % (rep['TABLE_NAME'],rep['COLUMN_NAME']),
                     'label': 'TableCols',
                     'properties': {'_KEY':'%s__%s' % (rep['TABLE_NAME'],rep['COLUMN_NAME'])}
                 }
                 self.insert_relationship()

         self.neo.finish()



if __name__ == '__main__':
    n = neo4junit(autocommit=True)
    cyqoperator(n,gxmongo().get_odbs()).operator()





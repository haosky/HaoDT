# -*- coding: utf-8 -*-

import jieba
import re
import sys
import traceback
reload(sys)
sys.setdefaultencoding('utf-8')

from haomongodb.mongodbmaster import gxmongo
from haounits.loggerDefTools import  get_defTestLogger as glog
# from haomongodb.product_v1.modles.mongodb_modles import *
from haomongodb.product_v1.modles import mongodb_modles
'''
数据混存mongodb
'''
log = glog()
def make_rule(mongomodle, odbs):
    cols = mongomodle.__dict__
    print(mongomodle)
    tablename = unicode(mongomodle).split('.')[-1]
    fobjset = odbs[tablename].find(no_cursor_timeout=True)

    rowset = []
    for key in cols.keys():
        if key.startswith('__') or key == '_id':
            continue
        rowset.append(key)

    prefixrow = tablename+u':'+(u':'.join(rowset))
    print(prefixrow)
    for fobj in fobjset:
        primary_key = None
        odbs_TableCols = odbs['TableCols']
        dataset = []
        table_name_keywords = None
        for key in fobj.keys():
            if key.startswith('__') or key == '_id':
                continue
            findtableobj = odbs_TableCols.find_one({"TABLE_NAME":tablename,"COLUMN_NAME":key})
            if findtableobj is  None:
                log.warn('TABLE_NAME %s COLUMN_NAME %s  null ' %(tablename, key))
                continue

            primary_key = fobj['_id']
            if primary_key is None:
                log.warn('primary_key null ')
                continue

            row = prefixrow+u'::'+unicode(primary_key)
            # log.info(row)

            # 1、获取值得关键字
            try:
                keywords = get_keywords(fobj[key])
            except:
                log.error(traceback.format_exc().replace('\n',' '))

            # 2、获取表关键字
            if table_name_keywords is None:
                table_name_keywords = get_keywords(findtableobj['TABLE_COMMENTS'])
                keywords.extend(table_name_keywords)

            # @TODO
#             # 3、获取字段关键字
#             table_clos_keywords = get_keywords(findtableobj['COLUMN_COMMENTS'])
#             keywords.extend(table_clos_keywords)

            update_obj = {
                '_ROWKEY':row,
                 'TABLE_COMMENTS':findtableobj['TABLE_COMMENTS']
                , 'COLUMN_COMMENTS':findtableobj['COLUMN_COMMENTS']
                , 'COLUMN_NAME': key
                , 'COLUMN_VALUE': fobj[key]
                ,'KEYWORDS':list(set(keywords))
                          }
            dataset.append(update_obj)

        yield dataset


def get_keywords(col):
    # 获取值关键字
    keywords = []
    jieba_keywords = []
    try:
        if isinstance(col, (str, unicode)):
            jieba_keywords = jieba.cut(unicode(col))
        for kw in jieba_keywords:
            kclear = re.sub(re.compile(u'[\d,A-Z,a-z]+'), '', kw).strip()
            if len(kclear) >= 2:
                keywords.append(kclear)
    except:
        log.error(traceback.format_exc().replace('\n', ' '))
    return keywords

if __name__ == '__main__':

    # client = gxmongo()
    # odbs = client.get_odbs()
    # dstore = client.get_dstore()
    # for outdatasets in make_rule(GL_VOUCHER_DETAIL,odbs):
    #     try:
    #         for data in outdatasets:
    #             dstore['ALLTABLE'].insert(data)
    #     except:
    #         log.eror(traceback.format_exc().replace('\n',' '))

    client = gxmongo()
    odbs = client.get_odbs()
    dstore = client.get_dstore()
    table_list = odbs.collection_names(include_system_collections=False)
    strs = []
    for table in table_list:
        if 'A'<= table[0] <= 'Z' and table !='TableCols' and table !='Tables':
            try:
                m = getattr(mongodb_modles,table)
                log.info('start %s -------------- ' % table)
                for outdatasets in make_rule(m,odbs):
                    try:
                        for data in outdatasets:
                            dstore['ALLTABLE'].insert(data)
                    except:
                        log.eror(traceback.format_exc().replace('\n',' '))
            except:
                log.error(traceback.format_exc().replace('\n',' '))




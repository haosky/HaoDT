# -*- coding: utf-8 -*-

from haothrift.simhandler import sim_query
from haothrift.simhandler import sim_develop
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.server import TServer
from thrift.protocol import TBinaryProtocol
from haounits.loggerDefTools import get_defTestLogger as getlog
import logging
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

__author__ = 'hao'

log = getlog(level=logging.DEBUG)


class searcher():

    def search_other(self,_uuid,**kwargs):
        socket = TSocket.TSocket('127.0.0.1', 9993)
        framed = False
        if framed:
            self.transport = TTransport.TFramedTransport(socket)
        else:
            self.transport = TTransport.TBufferedTransport(socket)
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.client = sim_query.Client(self.protocol)
        self.transport.open()
        res = self.client.common_query_api(_uuid)
        self.transport.close()
        return res

if __name__ == '__main__':
    print(".....starting....")
    ## 关联关系
    #print searcher().search_other('{"params":{"_uuid":"435f392b908a44442c9125ee2c542af0","num":10},"model":"applications.relation.MainServer","action":"get_entry_relative"}')
    # 关联关系列表
    #print searcher().search_other(
    #    '{"params":{"entry":"申报文档"},"model":"applications.relation.MainServer","action":"get_relative_list"}')

    # # 命名实体词提取
    # print searcher().search_other(
    #    '{"params":{"_uuid":"435f392b908a44442c9125ee2c542af0"},"model":"applications.multisearch.MainServer","action":"entry_word_query"}')

    # # 关键字提取
    # print searcher().search_other(
    #     '{"params":{"_uuid":"435f392b908a44442c9125ee2c542af0"},"model":"applications.multisearch.MainServer","action":"keyword_query"}')

    # 文章查重
    print searcher().search_other(
        '{"params":{"_uuid":"435f392b908a44442c9125ee2c542af0"},"model":"applications.repeat.MainServer","action":"get_doc_same_all"}')

    # 聚类分析
    # print searcher().search_other(
    #     '{"params":{"_uuid":"435f392b908a44442c9125ee2c542af0"},"model":"applications.multisearch.MainServer","action":"topic_query"}')

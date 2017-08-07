# -*- coding: utf-8 -*-
__author__ = 'hao'

from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.transport import THttpClient
from thrift.protocol import TBinaryProtocol
from haohbase.hbase import THBaseService
from haohbase.hbase.ttypes import *
from haounits.cfgOptionTools import get_items_in_cfg, get_uri_relative_parent_package
import haohbase as parent
import traceback

class hbase_dao():
    def __init__(self):
        self.__settings_file_path = get_uri_relative_parent_package(parent, 'hbase.properties')
        self.host = get_items_in_cfg('hbase', 'host', self.__settings_file_path)
        self.port = get_items_in_cfg('hbase', 'port', self.__settings_file_path)
        socket = TSocket.TSocket(self.host, self.port)
        framed = False
        if framed:
            self.transport = TTransport.TFramedTransport(socket)
        else:
            self.transport = TTransport.TBufferedTransport(socket)
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.client = THBaseService.Client(self.protocol)
        self.transport.open()

    def open(self):
        if not self.transport.isOpen() :
            self.close()
            socket = TSocket.TSocket(self.host, self.port)
            framed = False
            if framed:
                self.transport = TTransport.TFramedTransport(socket)
            else:
                self.transport = TTransport.TBufferedTransport(socket)
            self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
            self.client = THBaseService.Client(self.protocol)
            self.transport.open()

    def close(self):
        '''
        退出后关闭客户端链接并清理
        :return:
        '''
        try:
            if self.transport.isOpen():
                self.transport.close()
        except:
            traceback.print_exc()


    def get(self, table, rowkey):
        '''
        获取
        :param table: 表名
        :param rowkey: 行键
        :return:
        '''
        self.open()
        print rowkey
        tg = TGet(row=rowkey)
        res = self.client.get(table=table,tget =tg)
        self.close()
        return res

    def exists(self, table, rowkey):
        '''
        判断纪律是否存在, 存在返回True  不存在返回False
        :param table: 表名
        :param rowkey: 行键
        :return:
        '''
        self.open()
        tg = TGet(row=rowkey)
        res = self.client.exists(table=table,tget =tg)
        self.close()
        return res


    def put(self,table,rowkey,cvs):
        '''
        新增
        :param table: 表名
        :param rowkey: 行键
        :param cvs: 新增字段列表
        :return:
        '''
        self.open()
        tp = TPut(row=rowkey, columnValues=cvs)
        self.client.put(table,tp)
        self.close()

    def incr(self,table,rowkey,cvs):
        '''
        增长量
        :param table:  表名称
        :param rowkey:  行键
        :param cvs: 增长字段 [TColumnIncrement(family="cf1",qualifier=cn,amount=-1)]
        :return:
        '''
        self.open()
        socket = TSocket.TSocket(self.host, self.port)
        framed = False
        if framed:
            self.transport = TTransport.TFramedTransport(socket)
        else:
            self.transport = TTransport.TBufferedTransport(socket)
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.client = THBaseService.Client(self.protocol)
        self.transport.open()
        incr = TIncrement(row=rowkey,columns=cvs)
        self.client.increment(table,incr)
        self.close()

    def open_scan(self,table,tscan):
        '''
        读取
        :param table: 表名称
        :param tscan: 条件
        :return:
        '''
        self.open()
        return self.client.openScanner(table,tscan)

    def close_scan(self,scan_id):
        try:
            self.client.closeScanner(scan_id)
        except:
            traceback.print_exc()
        self.close()

    def delete(self,table,rk):
        self.open()
        socket = TSocket.TSocket(self.host, self.port)
        framed = False
        if framed:
            self.transport = TTransport.TFramedTransport(socket)
        else:
            self.transport = TTransport.TBufferedTransport(socket)
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.client = THBaseService.Client(self.protocol)
        self.transport.open()
        td = TDelete(row=rk)
        self.client.deleteSingle(table, td)
        self.close()

if __name__ == '__main__':
   d= hbase_dao()
   d.open()
   d.get('CaiZhengMoNiSim', '10000168435409605390b9cc421262135ff2d31338739f6b940f')
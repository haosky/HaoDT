# -*- coding: utf-8 -*-

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

    def sim_project_query(self,user_name):
        socket = TSocket.TSocket('192.168.100.14', 9993)
        framed = False
        if framed:
            self.transport = TTransport.TFramedTransport(socket)
        else:
            self.transport = TTransport.TBufferedTransport(socket)
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.client = sim_develop.Client(self.protocol)
        self.transport.open()
        res = self.client.get_doc_same_all(user_name,'abc')
        self.transport.close()
        return res

if __name__ == '__main__':
    print(".....starting....")
    print searcher().sim_project_query('97004')

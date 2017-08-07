# -*- coding: utf-8 -*-

from haothrift.simhandler import sim_query
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

    def sim_unit_query(self,company_name):
        socket = TSocket.TSocket('127.0.0.1', 9993)
        framed = False
        if framed:
            self.transport = TTransport.TFramedTransport(socket)
        else:
            self.transport = TTransport.TBufferedTransport(socket)
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.client = sim_query.Client(self.protocol)
        self.transport.open()
        res = self.client.sim_unit_query(company_name)
        self.transport.close()
        return res

if __name__ == '__main__':
    print(".....starting....")
    print searcher().sim_unit_query('广州')

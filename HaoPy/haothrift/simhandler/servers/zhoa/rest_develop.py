# -*- coding: utf-8 -*-

import traceback
from thrift.transport import TTransport
from thrift.transport import TSocket
import json
from thrift.server import TServer
from thrift.protocol import TBinaryProtocol
from haothrift.simhandler import rest_develop
from haoml.art_relative_api import art_relative_api
from haoml.articles_simhash_v2 import artcles_simhash
__author__ = 'hao'

class restsim():
    # 服务端ip
    SERVER_HOST = '192.168.100.140'
    # 服务端端口
    SERVER_PORT = 9996

    def __init__(self):
        self.api = art_relative_api()
        self.ast = artcles_simhash()

    def get_entry_relative(self, suuid, num):
        # c = self.ast.get_hbase_con_one(suuid)['project']
        data = self.api.query_relative(suuid,num)
        return data

    def get_relative_list(self,search_str):
        search_body = {"from" : 0, "size" :50,"query":{"bool":{"must":
                                            [{"query_string":{"fields":["project"],"query" :search_str}},
                                            {"exists":{"field":"isre"}}]}}}
        searchsets = self.ast.search_es_sets_dsl(search_body)
        result = []
        for row in searchsets:
            source = row['_score']
            con = row['_source']
            try:
                result.append({source: {
                    "project": con["project"],
                    "finical_unit": con["finical_unit"],
                    "finical_name": con["finical_name"],
                    "date": con["date"],
                    "doc": con["fl_type"],
                    "unit": con["unit"],
                    "finical": con["finical"],
                    "source": str(int(source)) + '%',
                    "uuid": con["_uuid"],
                    "docid": con["uuid"]
                }})
            except:
                print traceback.format_exc()
        if len(result) > 0:
            result = {'project':"", 'uuid': "", 'data': result}
            data = json.dumps(result, ensure_ascii=False)
            print data
            return data
        return None

if __name__ == '__main__':
    print(".....starting....")
    handler = restsim()
    print(".....finish....")
    proc = rest_develop.Processor(handler)
    trans_ep = TSocket.TServerSocket(host=restsim.SERVER_HOST, port=restsim.SERVER_PORT)
    trans_fac = TTransport.TBufferedTransportFactory()
    proto_fac = TBinaryProtocol.TBinaryProtocolFactory()
    server = TServer.TThreadPoolServer(proc, trans_ep, trans_fac, proto_fac)
    server.setNumThreads(20)
    server.serve()

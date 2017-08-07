# -*- coding: utf-8 -*-

from haoml.articlesimhash import get_content_simvalue, main_calc ,get_sim_distance
from haoml.articles_simhash_v2 import  artcles_simhash
from haoml.articles_simhash_v4 import  artcles_simhash as artcles_simhash_v
from haohbase.simart.get_for_scan import sim_sets
from haounits.loggerDefTools import get_defTestLogger as getlog
from haoml.rowexis import rows as existsrows
import logging
import json
import traceback
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.server import TServer
from thrift.protocol import TBinaryProtocol
from haothrift.simhandler import sim_develop
__author__ = 'hao'

log = getlog(level=logging.INFO)


class developer():
    # 服务端ip
    SERVER_HOST = '192.168.100.140'
    # 服务端端口
    SERVER_PORT = 9994
    # 相似距离
    KDISTINCT = 9
    # 句子的文本最短长度
    PHASE_LEN = 9

    def __init__(self):
        self.sim_len = 8
        self.hm_distinct = 10
        self.asm = artcles_simhash()
        self.asm3 = artcles_simhash_v()

    def get_art_sim(self, art_content):
        return str(get_content_simvalue(art_content))

    def get_difference2arts(self,art_src,art_dst):
        left = self.asm3.get_es_docid_by_uuid(art_src)
        right = self.asm3.get_es_docid_by_uuid(art_dst)
        if left and right:
            return main_calc(left, right, 10)
        return None

    def get_differencelist(self):
        return sim_sets().scan_data()

    def get_differencelist_for_art(self,content):
        sim_value = str(get_content_simvalue(content))
        groups = sim_sets().scan_data_rowprex(sim_value[0:self.sim_len],self.caizheng_table)

        differencelist = []
        sim_dist_keys = set()
        for group in groups:
            fname, docprop = group.items()[0] # simvalue,filename,content
            simvalue = docprop[0]
            sim_content_info = main_calc(docprop[2],content,self.hm_distinct)
            calc_weghit_groups = {}
            for output_phase_id,input_phase_idset in sim_content_info['similar'].items():

                for iid in input_phase_idset:
                    sim_distinct = get_sim_distance(sim_content_info["index"][int(iid)],
                                                    sim_content_info["search"][int(output_phase_id)] )

                    # 输入内容断落id :匹配内容断落id -- 距离
                    calc_weghit_groups.update({"%s:%s" % (iid, output_phase_id): 1 - sim_distinct * 0.04})

                sim_content_info.update({'weight':calc_weghit_groups})

            dist_absvalue = abs(int(sim_value) - int(simvalue))
            sim_dist_keys.add(dist_absvalue)
            differencelist.append({dist_absvalue:sim_content_info})
        return differencelist


    def get_differenceinfo(self, docid):
        result = self.asm.get_same_info(docid,kdistince=developer.KDISTINCT,phase_len=developer.PHASE_LEN)
        data = json.dumps(result, ensure_ascii=False)
        print data
        return data

    def get_differenceparse(self, docid):
        result = self.asm.get_same_phase(docid, kdistince=developer.KDISTINCT, phase_len=developer.PHASE_LEN)
        data = json.dumps(result, ensure_ascii=False)
        print data
        return data

    def get_differencecomment(self,docids_str):
        '''判断一组id本库是否存在该文章'''
        docids = docids_str.split('\n')
        doc_res = []
        for docid in docids :
            docid = docid.strip()
            if docid not in existsrows:
                doc_res.append(docid)
                print 'doc not exists ' + docid
        return json.dumps(doc_res)

    def get_same_list(self, inputdata):
        data = self.asm.get_search_list(inputdata)
        if len(data) > 0:
            d1 = data[0].values()[0]
            data.pop(0)
            result = {'project': d1['project'], 'uuid': d1['uuid'], 'data': data}
            data = json.dumps(result, ensure_ascii=False)
            print data
            return data
        return None

    def get_different_2_docid(self, left_id, right_id):
        # left_id = self.asm3.get_es_docid_by_uuid(left_id)
        # right_id = self.asm3.get_es_docid_by_uuid(right_id)
        if left_id is None or right_id is None :
            return None
        result = self.asm.get_different_2_docid(left_id, right_id)
        data = json.dumps(result, ensure_ascii=False)
        print data
        return data

    def get_doc_same_all(self,docid_in, suuid):
        # 综合评价、相似详情、相似片段
        try:
            # docid = self.asm3.get_es_docid_by_uuid(docid_in)
            # if docid:
                print 'exists '+docid_in
                result = self.asm3.main_calc(docid_in, suuid)
                stresult = json.dumps(result,ensure_ascii=False)
                print stresult
                return stresult
            # print 'None Id ' +  docid_in
        except:
            print traceback.format_exc()
            return None
#
if __name__ == '__main__':
    print(".....starting....")
    handler = developer()
    print(".....finish....")
    proc = sim_develop.Processor(handler)
    # trans_ep = TSocket.TServerSocket(host="192.168.18.236",port=9994)
    trans_ep = TSocket.TServerSocket(host=developer.SERVER_HOST, port=developer.SERVER_PORT)
    trans_fac = TTransport.TBufferedTransportFactory()
    proto_fac = TBinaryProtocol.TBinaryProtocolFactory()
    server = TServer.TThreadPoolServer(proc, trans_ep, trans_fac, proto_fac)
    server.setNumThreads(20)
    server.serve()

if __name__ == '__main__2':
     developer().get_same_list("资金")
    # print developer().get_doc_same_all('0065581842625040113','127.0.0.1')
    #  developer().get_different_2_docid('77926','d773162d8bf34d18b99081ccb25f730d')
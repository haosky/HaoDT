# -*- coding: utf-8 -*-

from haothrift.simhandler.ttypes import *
from haothrift.simhandler import sim_query
from haounits.loggerDefTools import get_defTestLogger as getlog
from haoml.zhoa_kw_entry_KMeans import kw_entry_KMeans
from haounits.bunchUtils import readbunchobj
import traceback
from haoml.articles_simhash_v4 import  artcles_simhash as artcles_simhash_v
# from haoml.keyword_extract import keyword_extract,process_hanlp_entry_cut,process_hanlp_cut
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.server import TServer
from thrift.protocol import TBinaryProtocol
from haoml.art_relative_api import art_relative_api
from haounits.fSTools import get_dir_sons
from haounits.cfgOptionTools import get_package_parent_local
import logging
import json
import importlib
import haothrift.applications as appparent

from jpype import *

__author__ = 'hao'
log = getlog(level=logging.DEBUG)

class searcher():

    def __init__(self):
        # ml_rule = self.__build_model_rule('applications.multisearch.MainServer')
        for fl in get_dir_sons(get_package_parent_local(appparent)):
            try:
                if fl.endswith('.py') or fl.endswith('.pyc'):
                    continue
                model_prex = fl.replace('\\','.').replace('/','.')
                model = 'applications.%s.MainServer' % model_prex
                self.__set_lib_method(model,{})
            except:
                log.error(traceback.format_exc())

    # @FIXME  REFACTOR
    def sim_unit_query(self,_uuid):
        return None

    #　@FIXME  REFACTOR
    def sim_user_query(self,_uuid):
        return None

    def sim_project_query(self,project_name):
        return None

    # @FIXME  REFACTOR
    def keyword_query(self,_uuid,num):
        return None

    # @FIXME  REFACTOR
    def topic_query(self,_uuid):
        return None

    # @FIXME  REFACTOR
    def entry_word_query(self,content):
        return None

    def new_word_query(self,content):
        return None

    # @FIXME  REFACTOR
    def relation_query(self,_uuid):
        return None

    def common_query_api(self,json_params):
        '''
        通用方法
        :param json_params:
        :return:
        '''
        params = json.loads(json_params)
        model = params['model']
        init_param = params.get('init',{})
        self_atr = self.__set_lib_method(model,init_param)
        return getattr(getattr(self,self_atr),'main_exec')(params)

    def __build_model_rule(self,model):
        mob = 'haothrift.%s' % model
        self_atr = 'f_%s' % hash(mob)
        return self_atr,mob

    def __set_lib_method(self,model,init_param):
        self_atr,relative_model = self.__build_model_rule(model)
        if getattr(self, self_atr, None) is None:
            log.info(relative_model)
            uh = importlib.import_module(relative_model)
            ha = uh.Server(**init_param)
            setattr(self, self_atr, ha)
        return self_atr

if __name__ == '__main__':
    print(".....starting....")
    handler = searcher()
    print(".....finish....")
    proc = sim_query.Processor(handler)
    trans_ep = TSocket.TServerSocket(host="192.168.100.140",port=9993)
    trans_fac = TTransport.TBufferedTransportFactory()
    proto_fac = TBinaryProtocol.TBinaryProtocolFactory()
    server = TServer.TThreadPoolServer(proc, trans_ep, trans_fac, proto_fac)
    server.setNumThreads(20)
    server.serve()
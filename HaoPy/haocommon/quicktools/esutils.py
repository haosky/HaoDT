# -*- coding: utf-8 -*-


from elasticsearch import Elasticsearch
from haounits.cfgOptionTools import get_items_in_cfg, get_uri_relative_parent_package
import haocommon as parent
import elasticsearch.helpers as eshelpers
import requests
import traceback
import jieba

__author__ = 'hao'

class ElasitcUtil(Elasticsearch):
    def __init__(self):
        self.__settings_file_path = get_uri_relative_parent_package(parent, 'settings.properties')
        hosts = get_items_in_cfg('elastcsearch', 'hosts', self.__settings_file_path)
        Elasticsearch.__init__(self, hosts = hosts)

    def scan_source(self,index,doc_type,query):
        scanResp = eshelpers.scan(self,
             query=query,
             index=index,
             doc_type=doc_type
             )
        return scanResp
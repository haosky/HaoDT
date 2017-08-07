# -*- coding: utf-8 -*-
from haothrift.applications.BaseServerController import BaseServerController
from haoml.articles_simhash_v2 import  artcles_simhash as artcles_simhash_v
from haoml.art_relative_api import art_relative_api
import traceback
import json

__author__ = 'hao'


class Server(BaseServerController):

     def __init__(self,**kwargs):
         BaseServerController.__init__(self,**kwargs)
         self.api = art_relative_api()
         self.ast = artcles_simhash_v()

     def get_entry_relative(self, _uuid=None, num=0):
         '''
         查询关联关系
         :param _uuid:文章uuid
         :param num: 返回条数
         :return:
         '''
         data = self.api.query_relative(_uuid, num)
         return data

     def get_project_from_entry(self, entry=None, num=0):
         data = self.api.query_project2entry_relative(entry, num)
         return data

     def get_project_from_entries(self, entrices=None, num=0):
         '''
         :param entrices: ['a','b']
         :param num:
         :return:
         '''
         data = self.api.query_project2entry_relative(entrices, num)
         return data

     def get_relative_from_entries(self,_uuid, entrices=None, num=0):
         '''
         :param entrices: ['a','b']
         :param num:
         :return:
         '''
         data = self.api.query_relative_entrices(_uuid,entrices, num)
         return data

     def get_entry_from_project(self, _uuid=None, num=0):
         data = self.api.query_entry2project_relative(_uuid, num)
         return data

     def get_relative_list(self, entry=None):
         '''
         查询带有关联关系的搜索列表
         :param entry: 搜索内容
         :return:
         '''
         search_body = {"from": 0, "size": 50, "query": {"bool": {"must":
                                                                      [{"query_string": {"fields": ["project"],
                                                                                         "query": entry}},
                                                                       {"exists": {"field": "isre"}}]}}}
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
                     "uuid": con["uuid"]
                 }})
             except:
                 self.LOG.error( traceback.format_exc())
         if len(result) > 0:
             result = {'project': "", 'uuid': "", 'data': result}
             data = json.dumps(result, ensure_ascii=False)
             self.LOG.info(data)
             return data
         return None



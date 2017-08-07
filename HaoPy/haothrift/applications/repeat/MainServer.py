# -*- coding: utf-8 -*-

import json
import traceback
from haoml.articles_simhash_v2 import  artcles_simhash
from haoml.articles_simhash_v4 import  artcles_simhash as artcles_simhash_v
from haothrift.applications.BaseServerController import BaseServerController

__author__ = 'hao'


class Server(BaseServerController):

     def __init__(self,**kwargs):
         BaseServerController.__init__(self,**kwargs)
         self.sim_len = 8
         self.hm_distinct = 10
         self.asm = artcles_simhash()
         self.asm3 = artcles_simhash_v()

     def get_same_list(self, entry=None):
         '''
         查询列表
         :param entry:搜索的内容
         :return:
         '''
         data = self.asm.get_search_list(entry)
         if len(data) > 0:
             d1 = data[0].values()[0]
             data.pop(0)
             result = {'project': d1['project'], 'uuid': d1['uuid'], 'data': data}
             data = json.dumps(result, ensure_ascii=False)
             self.LOG.info(data)
             return data
         return None

     def get_doc_same_all(self, _uuid, user_feature=None):
         '''
         综合评价、相似详情、相似片段
         :param 查询的文章id
         :param entry:使用者唯一识别标识，可以是ip等字符串
         :return:
         '''
         try:
             result = self.asm3.main_calc(_uuid, user_feature)
             stresult = json.dumps(result, ensure_ascii=False)
             self.LOG.info(stresult)
             return stresult
         except:
             self.LOG.error(traceback.format_exc())
             return None
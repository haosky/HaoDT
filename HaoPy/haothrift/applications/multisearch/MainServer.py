# -*- coding: utf-8 -*-
from haothrift.applications.BaseServerController import BaseServerController
from haoml.kw_entry_KMeans import kw_entry_KMeans
from haounits.bunchUtils import readbunchobj
import traceback
from haoml.articles_simhash_v4 import  artcles_simhash as artcles_simhash_v
from haoml.keyword_extract import keyword_extract,process_hanlp_entry_cut,process_hanlp_cut
from haounits.cfgOptionTools import get_items_in_cfg, get_uri_relative_parent_package
import haoml.data as source
from haoml.art_relative_api import art_relative_api
import json

__author__ = 'hao'

class Server(BaseServerController):

     def __init__(self,**kwargs):
         BaseServerController.__init__(self,**kwargs)
         self.asm = artcles_simhash_v()
         # kw_entry_KMeans_p = get_uri_relative_parent_package(source, 'kw_entry_KMeans.bin')
         kw_entry_KMeans_p = get_uri_relative_parent_package(source, 'zhoa_kw_entry_KMeans.bin')
         self.kmean = readbunchobj(kw_entry_KMeans_p)
         self.rp = art_relative_api()
         self.ke = keyword_extract()

     def sim_unit_query(self, _uuid=None):
         '''
         机构名实体
         :param 文章uuid:
         :return:
         '''
         try:
             input_doc = self.asm.get_con_one(_uuid)
             kls = process_hanlp_entry_cut(input_doc['content'])
             rws = list(set([word[0] for word in kls if word[1] == 'nt']))
             return json.dumps(rws, ensure_ascii=False)
         except:
             print traceback.format_exc()
             self.LOG.error(traceback.format_exc())
         return None

     def sim_user_query(self, _uuid=None):
         '''
         人名实体
         :param 文章uuid:
         :return:
         '''
         try:
             input_doc = self.asm.get_con_one(_uuid)
             kls = process_hanlp_entry_cut(input_doc['content'])
             print json.dumps(kls, ensure_ascii=False)
             rws = list(set([word[0] for word in kls if word[1] == 'nr']))
             return json.dumps(rws, ensure_ascii=False)
         except:
             self.LOG.error(traceback.format_exc())
         return None

     def sim_project_query(self, _uuid=None):
         '''
          项目实体
          :param 文章uuid:
          :return:
          '''
         # return json.dumps(self.ptools.search(project_name), ensure_ascii=False)
         return None

     def keyword_query(self, _uuid=None, num=0):
         '''
        关键字提取
        :param 文章uuid:
        :return:
         '''
         input_doc = self.asm.get_con_one(_uuid)
         if input_doc:
             return json.dumps(keyword_extract().extract_keywords(input_doc['content'], num), ensure_ascii=False)
         return None

     def topic_query(self, _uuid=None):
         '''
         主题/项目分类
         :param 文章uuid:
         :return:
          '''
         try:
             input_doc = self.asm.get_con_one(_uuid)
             kls = process_hanlp_entry_cut(input_doc['content'])
             rws = [word[0] for word in kls]
             self.LOG.info(json.dumps(rws, ensure_ascii=False))
             testset = self.kmean.map2vocab(rws)
             return json.dumps(self.kmean.predict(testset), ensure_ascii=False)
         except:
             self.LOG.error(traceback.format_exc())
         return None

     def entry_word_query(self, _uuid=None):
         '''
          命名实体词提取
          :param 文章uuid:
          :return:
           '''
         return None

     def new_word_query(self, _uuid=None):
         '''
        发现新词
        :param 文章uuid:
        :return:
         '''
         return None

     def relation_query(self, _uuid=None):
         '''
         关联关系查询
         :param 文章uuid:
         :return:
         '''
         try:
             pv = self.rp.query_relative(_uuid, 5)
             return json.dumps(pv, ensure_ascii=False)
         except:
             self.LOG.error(traceback.format_exc())
         return None

     def get_sentences_auto(self,**kwargs):
         '''
          :param kwargs {'put':搜索内容,'num':返回条数}:
          :return:
          '''
         put = kwargs['put']
         num = kwargs.get('num', 5)
         re_list = self.asm.search_auto_puts(sentence=put,num=num)
         return re_list

     def get_art_same(self,**kwargs):
        '''相似文档：基于标题和内容的搜索'''
        re_list = self.asm.search_same_esart(projet=kwargs['project'],content=kwargs['content'])
        return re_list

     def get_art_column(self,**kwargs):
         '''相似文档：基于标题和内容的搜索 column=['KwEntry','OrgEntry','PleceEntry','YyEntry','ChineseEntry':]'''
         re_list = self.asm.search_for_column(column=kwargs['column'],entry=kwargs['entry'],num=kwargs.get('num',10))
         return re_list

     def get_art_entry(self,**kwargs):
         '''
         :param kwargs {'entry':实体,'num':返回条数}:
         :return:
         '''
         entry = kwargs['entry']
         num = kwargs.get('num',5)
         re_list = self.rp.query_projectuuid2entry(entry,num)
         result = []
         for rs in re_list:
             row = self.asm.get_es_id(rs)
             con = row['_source']
             try:
                 ent = []
                 ent.extend(list(set(json.loads(con["PleceEntry"])))[0:5])
                 ent.extend(list(set(json.loads(con["KwEntry"])))[0:5])
                 ent.extend(list(set(json.loads(con["OrgEntry"])))[0:5])
                 ent.extend(list(set(json.loads(con["ChineseEntry"])))[0:5])
                 ent.extend(list(set(json.loads(con["StmtSentence"])))[0:5])
                 ent.extend(list(set(json.loads(con["YyEntry"])))[0:5])
                 ent = list(set(ent))
                 for e in ent:
                     con["content"] = con["content"].replace(e, '<span class="kw" entry="%s">%s</span>' % (e,e)).replace('\n', '<br>')
                 res = {
                     "project": con["project"],
                     "finical_unit": con["finical_unit"],
                     "finical_name": con["finical_name"],
                     "content": con["content"],
                     "date": con["date"],
                     "doc": con["fl_type"],
                     "unit": con["unit"],
                     "finical": con["finical"],
                     "source":  '100%',
                     "uuid": con["uuid"],
                     "upload_at": con["upload_at"],
                 }
                 result.append(res)
             except:
                 self.LOG.error(traceback.format_exc())

         return json.dumps(result,ensure_ascii=False)

     def search_art_keyword(self,**kwargs):
         '''
          融合搜索
          :param entry:输入的搜索内容
          :return:
         '''
         entry = kwargs['entry']
         filter = kwargs.get('filter','')
         search_body = {"from": 0, "size": 50, "query": {"bool": {"must":
                                                                      [{"query_string": {"fields": ["project"],
                                                                                         "query": entry}},
                                                                       # {"exists": {"field": "isre"}},
                                                                      ]
                                                      }}}

         searchsets = self.asm.search_es_sets_dsl(search_body)
         result = []
         for row in searchsets:
             source = row['_score']
             con = row['_source']
             try:
                 ent = []
                 ent.extend(list(set(json.loads(con["PleceEntry"])))[0:5])
                 ent.extend(list(set(json.loads(con["KwEntry"])))[0:5])
                 ent.extend(list(set(json.loads(con["OrgEntry"])))[0:5])
                 ent.extend(list(set(json.loads(con["ChineseEntry"])))[0:5])
                 ent.extend(list(set(json.loads(con["StmtSentence"])))[0:5])
                 ent.extend(list(set(json.loads(con["YyEntry"])))[0:5])
                 ent = list(set(ent))
                 for e in ent:
                     con["content"]=con["content"].replace(e,'<span class="kw"  entry="%s">%s</span>' % (e,e)).replace('\n','<br>' )
                 res = {
                     "project": con["project"],
                     "finical_unit": con["finical_unit"],
                     "finical_name": con["finical_name"],
                     "content": con["content"],
                     "date": con["date"],
                     "doc": con["fl_type"],
                     "unit": con["unit"],
                     "finical": con["finical"],
                     "source": str(int(source)) + '%',
                     "uuid": con["uuid"],
                     "upload_at": con["upload_at"],
                 }
                 result.append(res)
             except:
                 self.LOG.error(traceback.format_exc())
         if len(result) > 0:
             result = {'project': "", 'uuid': "", 'data': result}
             data = json.dumps(result, ensure_ascii=False)
             self.LOG.info(data)
             return data
         return None

     def get_body_compx_info(self,_uuid=None):
         '''
         展示详细情况
         :return:
         '''
         row = self.asm.get_es_id(_uuid)
         try:
             con = row['_source']
             kls = process_hanlp_entry_cut(con['content'])
             rws = [word[0] for word in kls]
             self.LOG.info(json.dumps(rws, ensure_ascii=False))
             testset = self.kmean.map2vocab(rws)
             topic = self.kmean.predict(testset)
             result = {
                 "project": con["project"],
                 "finical_unit": con["finical_unit"],
                 "finical_name": con["finical_name"],
                 "date": con["date"],
                 "doc": con["fl_type"],
                 "unit": con["unit"],
                 "content": con["content"].replace('\n','<br>'),
                 "finical": con["finical"],
                 "uuid": con["uuid"],
                 "upload_at": con["upload_at"],
                 "place_entry":list(set(json.loads(con["PleceEntry"])))[0:5],
                 "kw_entry": list(set(json.loads(con["KwEntry"])))[0:5],
                 "org_entry": list(set(json.loads(con["OrgEntry"])))[0:5],
                 "chinese_entry": list(set(json.loads(con["ChineseEntry"])))[0:5],
                 "stmt_sentence": list(set(json.loads(con["StmtSentence"]))),
                 "yy_entry": list(set(json.loads(con["YyEntry"])))[0:5],
                 "topic_cluster":topic[0:8]
             }
             return json.dumps(result,ensure_ascii=False)
         except:
            self.LOG.error(traceback.format_exc())
         return None

if __name__ == '__main__':
    print json.dumps(Server().search_art_keyword(entry='广东省环境保护厅'),ensure_ascii=False)
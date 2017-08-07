# -*- coding: utf-8 -*-
import os
import re
import sys
import traceback
import argparse
from datetime import datetime
from simhash import Simhash, SimhashIndex
from haohbase.hbase_dao import hbase_dao
from haohbase.simart.get_for_scan import sim_sets
from haounits.cfgOptionTools import get_items_in_cfg, get_uri_relative_parent_package
from haoml.articlesimhash import art_get_phase,get_features,get_sim_distance,calc_distince,mark_same_content,get_different_2_doc
import jieba
from haounits.loggerDefTools import get_defTestLogger
from jieba import analyse
import json
import sys
import copy
from time import time
from haocommon.quicktools.esutils import ElasitcUtil
import haostorm.check_repeat as mainparent
import haostorm.check_repeat.qdsl as parent
log = get_defTestLogger()
reload(sys)
sys.setdefaultencoding('utf8')

class artcles_simhash():

     
    QSDL_TYPE = 'caizheng'
    caizheng_t1 = 'MoNi__v2'
    caizheng_row_t1 = 'MoNi__v2_row'

    def __init__(self):
        self.es = ElasitcUtil()
        self.__qdsl_file_path = get_uri_relative_parent_package(parent, 'search.qdsl')
        self.query_table_data_dsl = get_items_in_cfg(artcles_simhash.QSDL_TYPE, artcles_simhash.caizheng_t1,
                                                     self.__qdsl_file_path)

        self.query_table_data_dsl_row = get_items_in_cfg(artcles_simhash.QSDL_TYPE, artcles_simhash.caizheng_row_t1,
                                                     self.__qdsl_file_path)

       
        self.INDEX_DATA_CENTER = get_items_in_cfg('index_type', 'CZ_INDEX_DATA_CENTER',
                                                  self.__qdsl_file_path)
        self.DOC_TYPE_TABLE = get_items_in_cfg('index_type', 'CZ_DOC_TYPE_TABLE',
                                               self.__qdsl_file_path)

        self.__sim_config_file_path = get_uri_relative_parent_package(mainparent, 'sim_settings.properties')
        table_config = 'hbase_table'
        self.caizheng_table = get_items_in_cfg(table_config, 'caizheng_table',
                                               self.__sim_config_file_path)
        self.hscan = sim_sets()
        self.ks = ["project", "finical_unit", "finical_name", "date", "doc", "content", "unit", "finical","fl_type"]
        self.art_phase_sim_parse = None

    def search_es_sets(self, article_src):
        search_body_str = self.query_table_data_dsl % (article_src)
        search_body = json.loads(search_body_str)
        return self.search_es_sets_dsl(search_body)


    def search_es_sets_dsl(self,search_body):
        response_hits = self.es.search(index=self.INDEX_DATA_CENTER, doc_type=self.DOC_TYPE_TABLE,
                                       body=search_body)
        rows = response_hits.get('hits', {}).get('hits', [])
        return rows

    def get_es_row_with_count(self,article_src,num):
        # sb = ' '.join(list(jieba.cut(article_src)))
        # search_body_str = self.query_table_data_dsl_row % (num,sb)
        search_body_str = self.query_table_data_dsl_row % (num, article_src.strip().replace('\t','').replace('\r',''))
        search_body = json.loads(search_body_str)
        response_hits = self.es.search(index=self.INDEX_DATA_CENTER,
                                       doc_type=self.DOC_TYPE_TABLE,
                                       body=search_body)
        rows = response_hits.get('hits', {}).get('hits', [])
        return rows

    def get_con_one(self,docid):
        response_hits = self.es.get(index=self.INDEX_DATA_CENTER,
                                       doc_type=self.DOC_TYPE_TABLE,
                                    id=docid)
        try:
            rows = response_hits.get('_source', {})
            return rows
        except:
            print traceback.format_exc()
        return None

    def get_search_list(self, inputdata):
        # 文档查重-汇总列表
        result = []
        searchsets = self.search_es_sets(inputdata)
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
                    "content":unicode(con["content"][0:200]) ,
                    # "content":"",
                    "unit": con["unit"],
                    "finical": con["finical"],
                    "source": str(int(source))+'%',
                    "uuid": con["uuid"]
                }})
            except:
                pass
        return result

    def get_same_content_list(self,docid,kdistince=10,phase_len=8):
        try:
            doc = self.get_con_one(docid)
            content = doc['content']
            doc_phases = art_get_phase(content)
            doc_same_src = {}
            pharseid = -1
            ds = {}
            maxline = 100
            for doc_phase in doc_phases :
                try:
                    if maxline <= 0:
                        break
                    maxline -= 1
                    pharseid += 1
                    if(len(doc_phase.replace(' ',''))) < phase_len:
                        continue
                    src_set = {}
                    search_es_list = []
                    try:
                        search_es_list = self.get_es_row_with_count(doc_phase,4)
                    except:
                        log.error( traceback.format_exc())
                    src_docs_sim = []
                    for src_doc in search_es_list:
                        try:
                            src_doc_id = src_doc['_id']
                            if src_doc_id == docid:
                                continue
                            doc_body = src_doc['_source']
                            if 'content' not in doc_body:
                                continue
                            if doc_body['project'] == doc['project']:
                                continue

                            dcon = unicode(doc_body['content'])
                            dlen = len(dcon)
                            src_doc_phases = art_get_phase(dcon)
                            i = -1
                            sim_doc_data = {
                                "project": doc_body["project"],
                                "finical_unit": doc_body["finical_unit"],
                                "finical_name": doc_body["finical_name"],
                                "date": doc_body["date"],
                                "doc": doc_body["doc"],
                                "unit": doc_body["unit"],
                                "finical": doc_body["finical"],
                                "fl_type": doc_body["fl_type"],
                                "uuid": doc_body["_uuid"],
                                 "docid": doc_body["uuid"],
                                "content_len" : len(dcon)
                            }
                            for src_phase in src_doc_phases:
                                i += 1
                                if (len(src_phase.replace(' ', ''))) < phase_len:
                                    continue
                                src_docs_sim.append(['%s:%s' % (src_doc_id,i), Simhash(get_features(src_phase))])
                                src_set.update({'%s:%s' % (src_doc_id,i):[src_phase,sim_doc_data,len(src_doc_phases),dlen]})
                        except:
                            log.error(traceback.format_exc())
                except:
                    log.error(traceback.format_exc())

                index = SimhashIndex(src_docs_sim, k=kdistince)
                s1 = Simhash(get_features(doc_phase))
                sim_sames = index.get_near_dups(s1)
                if len(sim_sames) == 0 :
                    continue
                doc_same_src.update({pharseid:[]})
                for same_id in sim_sames:
                    doc_same_src[pharseid].append({same_id:src_set[same_id]})
                ds.update({pharseid:doc_phase})

            return {'phases':ds,'sim_map':doc_same_src},doc,doc_phases
        except:
            log.error(traceback.format_exc())
            return None

    def get_same_comment(self,docid,kdistince=10,phase_len=8):
        try:
            same_content_list,docbody,split_doc_phases = self.get_same_content_list(docid,kdistince=kdistince,phase_len=phase_len)
            search_phases = same_content_list['phases']
            sim_map = same_content_list['sim_map']
            art_same_list = {}
            sim_word_count_list = {}
            for k, same in sim_map.items():
                sim_word_count_list.update({k:[]})
                #  相似的每一句
                for same_unit in same:
                    samedocid = same_unit.keys()[0].split(':')[0]
                    # 内容部分
                    same_property  = same_unit.values()[0]
                    index_content = same_property[0]
                    if samedocid not in art_same_list.keys():
                        art_same_list.update({samedocid:{'phases':[],'body':same_property[1],'phasecount':same_property[2]}})
                    rightcontent = search_phases[k].strip()
                    leftcontent = index_content.strip()
                    right, sim_word_count_c = mark_same_content(copy.deepcopy(leftcontent), copy.deepcopy(rightcontent), "")
                    art_same_list[samedocid]['phases'].append([search_phases[k],index_content,sim_word_count_c]) #原内容,相似内容,相似字数
                    # sim_word_count_list[k].append({sim_word_count_c:len(leftcontent)})
                    sim_source = float(sim_word_count_c) / float(len(leftcontent))
                    sim_word_count_list[k].append({sim_source: {sim_word_count_c: len(leftcontent)}})

            # 求相似列表
            doc_same_list = []
            source_doc = {}
            # 循环每篇文章
            for samedocid,content_2_simbody in art_same_list.items():
                doccheckcount = 0
                docsimcount = 0
                phases = content_2_simbody['phases']
                phasecount = content_2_simbody['phasecount']
                sum_souce = 0.0
                for phase in phases :
                        #相似文章里面相似的每一句
                        rightcontent = phase[1].strip()
                        leftcontent = phase[0].strip()
                        sim_count = phase[2]
                        docsimcount = docsimcount + sim_count
                        doccheckcount = doccheckcount + len(leftcontent)
                        sum_souce = sum_souce +  float(sim_count)   / float(len(leftcontent))

                # isource = 0 if doccheckcount == 0 else min(float(docsimcount) / float(doccheckcount) * 100, 100)
                isource = sum_souce * 100  / float(len(split_doc_phases))
                if isource > 0:
                    source_doc.update({samedocid:{"checkcount":doccheckcount,"simcount":docsimcount}})
                    docname = content_2_simbody['body']['project']
                    doc_same_list.append({isource: {"come_from": content_2_simbody['body']['fl_type'], "upload_at": "广州", "upload_for": "某某",
                                                     "doc_name": docname, "source": str(int(isource)) + str(isource - int(isource))[1:3] + "%", "info_url": "",
                                                     "uuid": samedocid}})

            doc_same_list.sort(reverse=True)

            # 求总体相似
            sim_count_c = 0
            length_conut_c = 0
            distribution = []
            plen = len(split_doc_phases)
            source_gb = 0
            for k,soure2len in sim_word_count_list.items():
                soure2len.sort(reverse=True)
                # 获取 分数:{相似字数:句子数}
                content_ss = soure2len[0]

                source = content_ss.keys()[0]
                content_max_same = content_ss.values()[0]
                source_gb = source_gb + source
                sim_count = content_max_same.keys()[0]
                length_conut = content_max_same.values()[0]
                sim_count_c =sim_count_c + sim_count
                length_conut_c = length_conut_c + length_conut

                classname = 0
                if 0.4 >= source < 0.7:
                    classname = 1
                elif source >= 0.7:
                    classname = 2
                distribution.append({'local': int(float(k) * 100 / float(plen)), 'type': classname})

            art_sim_source = float(source_gb) * 100 / float(len(split_doc_phases))
            dcc = docbody['content']
            word_count = len(list(jieba.cut(dcc)))
            parse_count =  dcc.count('\n')
            mark_set = u''',.?'!<>，。？《》！[]()（）【】;；:： '''
            for mark in mark_set:
                dcc=dcc.replace(mark,'')
            single_word_count = len(dcc)

            distribution.sort(reverse=False)

            smsource = str(int(art_sim_source)) + str(art_sim_source - int(art_sim_source))[1:6]
            data = {"sim_source": smsource +"%", "title":docbody['project'], "same_list": doc_same_list,
             "check_count": length_conut_c, "sim_count": sim_count_c, "word_count": word_count, "parse_count": parse_count,
             "single_word_count": single_word_count, "distribution": distribution,'sentence_count':len(split_doc_phases),'sim_original':str(100.0 - float(smsource))+'%'}

            result = {'project': docbody['project'], 'uuid':docid, 'data': data}

            return result

        except:
            log.error(traceback.format_exc())
            return None

    def get_same_info(self,docid,kdistince=10,phase_len=8):
        try:
            same_content_list, docbody, split_doc_phases = self.get_same_content_list(docid, kdistince=kdistince,
                                                                                      phase_len=phase_len)
            plen = len(split_doc_phases)
            search_phases = same_content_list['phases']
            sim_map = same_content_list['sim_map']
            art_same_list = {}
            sim_word_count_list = {}
            sim_doc_map = {}

            content = docbody['content']

            has_key = []
            for k, same in sim_map.items():
                sim_word_count_list.update({k: []})
                #  相似的每一句
                for same_unit in same:
                    pk = same_unit.keys()[0]
                    samedocid = pk.split(':')[0]
                    # if samedocid in has_key:
                    #     continue
                    # has_key.append(samedocid)
                    # 内容部分
                    same_property = same_unit.values()[0]
                    index_content = same_property[0]

                    body_con = same_property[1]
                    if samedocid not in art_same_list.keys():
                        art_same_list.update({k: {'phases': [], 'body': body_con,
                                                          'phasecount': same_property[2],   }})
                    rightcontent = search_phases[k].strip()
                    leftcontent = index_content.strip()

                    right, sim_word_count_c = mark_same_content(copy.deepcopy(leftcontent), copy.deepcopy(rightcontent), "sim gray")
                    left, left_sim_word_count = mark_same_content(copy.deepcopy(rightcontent), copy.deepcopy(leftcontent), "lsim gray")
                    isource = float(left_sim_word_count) * 100 / float(len(leftcontent))
                    sdetail = {
                        "uuid": samedocid,
                        "title": body_con["project"],
                        "index_parse": left,
                        "sim_parse_doc": "",
                        "sim_parse": right,
                        "submiter": "某某",
                        "upload_at": body_con["date"],
                        "wordcount": body_con["content_len"],
                        "sim_rate" :str(int(isource)) + str(isource - int(isource))[1:3] + "%"
                    }
                    mapsets = sim_doc_map.get(k, [])

                    mapsets.append(sdetail)
                    sim_doc_map.update({k: mapsets})
                    localvalue = float(k) * 100 / float(plen)

                    classname = 'warn'
                    if isource >= 0.7:
                        classname = 'serious'
                    link_txt = u'''<a onclick="simInfo(this);" href="javascript:void(0);" source="%s" class="%s" id="%s" local="%s" >%s</a>''' % (
                        # k,
                        str(int(isource)) + str(isource - int(isource))[1:3] + "%", classname, k,
                        str(int(localvalue) ), leftcontent)
                    content = content.replace(split_doc_phases[k], link_txt)

            data = {"content": content.replace('\n', '<br>'), "right": sim_doc_map}
            result = {'project': docbody['project'], 'uuid': docbody['uuid'], 'data': data}
            return result
        except:
            log.error(traceback.format_exc())
            return None

    def get_same_phase(self,docid,kdistince=10,phase_len=8):
        try:
            same_content_list, docbody, split_doc_phases = self.get_same_content_list(docid, kdistince=kdistince,
                                                                                      phase_len=phase_len)
            plen = len(split_doc_phases)
            search_phases = same_content_list['phases']
            sim_map = same_content_list['sim_map']
            art_same_list = {}
            sim_word_count_list = {}
            sim_doc_map = {}

            has_key = []
            content_parse = []
            dkset = []
            for k, same in sim_map.items():
                sim_word_count_list.update({k: []})
                #  相似的每一句
                for same_unit in same:
                    pk = same_unit.keys()[0]
                    samedocid = pk.split(':')[0]

                    # 内容部分
                    same_property = same_unit.values()[0]
                    index_content = same_property[0]

                    body_con = same_property[1]
                    if samedocid not in art_same_list.keys():
                        art_same_list.update({k: {'phases': [], 'body': body_con,
                                                          'phasecount': same_property[2],   }})

                    rightcontent = search_phases[k].strip()
                    leftcontent= index_content.strip()

                    right, sim_word_count_c = mark_same_content(leftcontent, copy.deepcopy(rightcontent), "sim gray")
                    left, left_sim_word_count = mark_same_content(rightcontent, copy.deepcopy(leftcontent), "lsim gray")
                    isource = float(left_sim_word_count) * 100 / float(len(leftcontent))
                    sdetail = {isource:{
                        "uuid": samedocid,
                        "title": body_con["project"],
                        "index_parse": left,
                        "sim_parse_doc": "",
                        "sim_parse": right,
                        "submiter": "某某",
                        "upload_at": body_con["date"],
                        "wordcount": body_con["content_len"],
                        "sim_rate" :str(int(isource)) + str(isource - int(isource))[1:3] + "%"
                    }}
                    mapsets = sim_doc_map.get(k, [])

                    mapsets.append(sdetail)
                    sim_doc_map.update({k: mapsets})

                    if k in dkset:
                        continue
                    dkset.append(k)
                    localvalue = float(k) * 100 / float(plen)

                    link_txt = u'''<a href="javascript:parseSimInfo('%s')" class="%s" id="%s" local="%s">%s</a>''' % (
                        k, "black", k, str(localvalue), leftcontent)

                    if samedocid in has_key:
                        continue
                    has_key.append(samedocid)
                    content_parse.append({k:[link_txt,str(int(localvalue))]})

            for doc, maps in sim_doc_map.items():
                sim_doc_map[doc].sort(reverse=True)

            content_parse.sort()
            data_parse = []
            for d in content_parse:
                vd = d.values()[0]
                data_parse.append({'id':d.keys()[0],'name':vd[0],'local':vd[1]})
            data = {"content": data_parse, "right": sim_doc_map}
            result = {'project': docbody['project'], 'uuid': docbody['uuid'], 'data': data}
            return result
        except:
            log.error(traceback.format_exc())
            return None

    def get_different_2_docid(self, left_id, right_id):
        try:
            left =  self.get_con_one(left_id)
            art_left =left['content']
            right = self.get_con_one(right_id)
            art_right = right['content']
            max_distince = 10
            djson = get_different_2_doc(art_left, art_right, max_distince=max_distince)
            djson.update({'left_title':left['project'],'right_title':right['project']})
            return djson
        except:
            log.error(traceback.format_exc())
            return None
#
# import haothrift.eshandler.qdsl as qsdlparent
# if __name__ == '__main__':
#     asm = artcles_simhash()
#     # 搜索
#     datasets = asm.get_search_list('北京市预算监督条例')
#     print(json.dumps(datasets,ensure_ascii=False,indent=2))
#
#     # 综合评价
#
#     # content_same_list = asm.get_same_phase('11053111324763869998a87e538a7893327f9e00037facd140a2',kdistince=9,phase_len=6)
#     # print json.dumps(content_same_list,ensure_ascii=False,indent=1)
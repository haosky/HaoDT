# -*- coding: utf-8 -*-
import traceback
import multiprocessing
import jieba
from haounits.cfgOptionTools import get_items_in_cfg, get_uri_relative_parent_package
from haoml.articlesimhash import mark_same_content
import json
import re
import sys
import copy
from haocommon.quicktools.esutils import ElasitcUtil
from haoml.articlesimhash import art_get_phase,get_features
import haostorm.check_repeat as mainparent
from simhash import Simhash, SimhashIndex
import haostorm.check_repeat.qdsl as parent
from haounits.loggerDefTools import get_defTestLogger as getlog
import time
import logging
reload(sys)
sys.setdefaultencoding('utf8')

log = multiprocessing.get_logger()
log.setLevel(logging.INFO)

class artcles_simhash():
    '''在线多进程处理'''
    PROCESSNUM = 3
    QSDL_TYPE = 'caizheng'
    caizheng_t1 = 'MoNi__v2'
    caizheng_row_t1 = 'MoNi__v2_row'
    #最大句子数
    MAX_SENTENCE_NUM = 1000

    PHASE_TO_DOC_LEN = 3
    # 匹配相似的字数
    PHASE_RAW_LEN = 4

    def __init__(self):
        self.es = ElasitcUtil()
        self.__sim_config_file_path = get_uri_relative_parent_package(mainparent, 'sim_settings.properties')
        table_config = 'hbase_table'
        self.caizheng_table = get_items_in_cfg(table_config, 'caizheng_table',
                                                     self.__sim_config_file_path)

        self.exists_table = get_items_in_cfg(table_config, 'exists_table',
                                                     self.__sim_config_file_path)

        self.phase_table =  get_items_in_cfg(table_config, 'phase_table',
                                                     self.__sim_config_file_path)
        self.__qdsl_file_path = get_uri_relative_parent_package(parent, 'search.qdsl')
        self.query_table_data_dsl_row = get_items_in_cfg(artcles_simhash.QSDL_TYPE, artcles_simhash.caizheng_row_t1,
                                                         self.__qdsl_file_path)
        self.INDEX_DATA_CENTER = get_items_in_cfg('index_type', 'CZ_INDEX_DATA_CENTER',
                                                  self.__qdsl_file_path)
        self.DOC_TYPE_TABLE = get_items_in_cfg('index_type', 'CZ_DOC_TYPE_TABLE',
                                               self.__qdsl_file_path)
        self.REPEAT_TYPE_TABLE = self.DOC_TYPE_TABLE+'_rep'

        self.ks = ["project", "finical_unit", "finical_name", "date", "doc", "content", "unit", "finical","fl_type"]

        self.__settings_file = get_uri_relative_parent_package(mainparent, 'sim_settings.properties')
        self.pdistinct = int(get_items_in_cfg("simhash", "doc2phase_distinct",
                                              self.__settings_file))
        self.art_phase_sim_parse = None

        # #mongo 配置
        # self.__mongo_config_file_path = get_uri_relative_parent_package(mongosource, 'mongodb.properties')
        # self.mongo_doc_repeat = int(get_items_in_cfg("collections", "doc_repeat",
        #                                       self.__settings_file))
        # self.doc_repeat_exists = int(get_items_in_cfg("collections", "doc_repeat_exists",
        #                                              self.__settings_file))
        # self.mongo = gxmongo()
        # self.repeat_mongo_db = self.mongo.get_repeatstore()
        # self.repeat_collections = self.repeat_mongo_db[self.mongo_doc_repeat]

    def get_es_docid_by_uuid(self,_uuid):
        # 通过项目id 获取，本库记录id
        search_body = {"from" : 0, "size" : 1, "query": {"term": { "uuid": _uuid}}}
        response_hits = self.es.search(index=self.INDEX_DATA_CENTER,
                                       doc_type=self.DOC_TYPE_TABLE,
                                       body=search_body)
        rows = response_hits.get('hits', {}).get('hits', [])
        try:
            return rows[0]['_id']
        except:
            log.error(traceback.format_exc())
        return None

    def get_es_row_with_count(self,article_src,num):
        # sb = ' '.join(list(jieba.cut(article_src)))
        # search_body_str = self.query_table_data_dsl_row % (num,sb)
        rows = []
        try:
            sc = re.sub(u'\t|\r|[0-9]|[一二三四五六七八九十百千\（\）万元、：]', '', article_src).strip()
            search_body_str = self.query_table_data_dsl_row % (num,sc )
            log.debug( search_body_str)
            search_body = json.loads(search_body_str)
            response_hits = self.es.search(index=self.INDEX_DATA_CENTER,
                                           doc_type=self.DOC_TYPE_TABLE,
                                           body=search_body)
            rows = response_hits.get('hits', {}).get('hits', [])
        except:
            log.error(traceback.format_exc())
        return rows

    def search_auto_puts(self,sentence,num=10):
        search_body = { "query": {"bool":{"should":[{"match_phrase_prefix": {"content" : {
            "query": sentence,
            "max_expansions":  50
        }}},{"match_phrase_prefix": {"project" : {
            "query": sentence,
            "max_expansions":  50
        }}}]}}}
        response_hits = self.es.search(index=self.INDEX_DATA_CENTER,
                                       doc_type=self.DOC_TYPE_TABLE,
                                       body=search_body)
        rows = response_hits.get('hits', {}).get('hits', [])
        sents = set()
        for rv in rows:
            rz=rv['_source']
            con = unicode(rz['content'].strip().replace('\r','。').replace('\n','。'))
            sens = re.split(re.compile(u'''\r\n|\n|。|!|？|！|\?|；|，|、|》|《|\s|：''',re.S),con)
            if len(sents) >=num:
                break
            for sen in sens:
                if len(sents) >=num:
                    break
                if unicode(sentence) in sen:
                    zv = sen.strip()
                    sents.add(zv)

            if unicode(sentence) in  unicode(rz['project']):
                if len(sents) >=num:
                    break
                zv = rz['project'].strip()
                sents.add(zv)

        return json.dumps(list(sents),ensure_ascii=False)


    def search_for_column(self,column,entry,num=10):
        search_body = {"from" : 0, "size" : num, "query": {"match_phrase": { column: entry  }}}
        response_hits = self.es.search(index=self.INDEX_DATA_CENTER,
                                       doc_type=self.DOC_TYPE_TABLE,
                                       body=search_body)
        rows = response_hits.get('hits', {}).get('hits', [])
        return rows

    def search_same_esart(self,projet,content,num=10):
        search_body =  {"size":num, "query": {"bool":{"should":[{"match": {"content" :
                    content.replace('\n',' ').replace('\t','').replace('"',''),
                }},{"match": {"projet" :
                    projet
            }}]}}}
        response_hits = self.es.search(index=self.INDEX_DATA_CENTER,
                                       doc_type=self.DOC_TYPE_TABLE,
                                       body=search_body)
        rows = response_hits.get('hits', {}).get('hits', [])
        return rows

    # def get_hbase_con_one(self, docid):
    #     hd = hbase_dao()
    #     rec = hd.get(self.caizheng_table, docid)
    #     result = {"uuid":docid}
    #     for col in rec.columnValues:
    #         result.update({col.qualifier : col.value} )
    #     return result

    def get_con_one(self,docid):
        response_hits = self.es.get(index=self.INDEX_DATA_CENTER,
                                       doc_type=self.DOC_TYPE_TABLE,
                                    id=docid)
        try:
            rows = response_hits.get('_source',None)
            return rows
        except:
            log.error( traceback.format_exc())
        return None

    def search_es_sets_dsl(self,search_body):
        response_hits = self.es.search(index=self.INDEX_DATA_CENTER, doc_type=self.DOC_TYPE_TABLE,
                                       body=search_body)
        rows = response_hits.get('hits', {}).get('hits', [])
        return rows

    def get_es_id(self,_uuid):
        rep = self.es.get(index=self.INDEX_DATA_CENTER, doc_type=self.DOC_TYPE_TABLE,
                                       id=_uuid)
        return rep

    def search_es_sim(self,sen_id,project,doc_phase,sentences_count):
        id_split = sen_id.split(':')
        # 文章uuid
        docid = id_split[0]
        es_start_time = time.time()
        search_es_list = self.get_es_row_with_count(doc_phase, artcles_simhash.PHASE_TO_DOC_LEN)
        es_end_time = time.time()
        log.info( 'es end time ' + str(es_end_time - es_start_time))
        src_docs_sim = []
        src_set = {}

        for src_doc in search_es_list:
            try:
                src_doc_id = src_doc['_id']
                log.debug(src_doc_id)
                if src_doc_id == docid:
                    log.info('src_doc_id same ' + src_doc_id)
                    continue
                doc_body = src_doc['_source']
                if 'content' not in doc_body:
                    log.info('no content '+ src_doc_id)
                    continue
                dcon = unicode(doc_body['content'])
                src_doc_phases = art_get_phase(dcon)
                i = -1
                sim_doc_data = {
                    "project": doc_body["project"],
                    "finical_unit": doc_body["finical_unit"],
                    "finical_name": doc_body["finical_name"],
                    "date": doc_body["date"],
                    "submiter": doc_body.get("submiter", ""),
                    "doc": doc_body["doc"],
                    "unit": doc_body["unit"],
                    "finical": doc_body["finical"],
                    "fl_type": doc_body["fl_type"],
                    "uuid": doc_body["uuid"],
                    "docid": doc_body["uuid"],
                    "sentences_count": sentences_count
                }
                for src_phase in src_doc_phases:
                    i += 1
                    src_phase = unicode(src_phase.strip())
                    if (len(src_phase.replace(u' ', u''))) < artcles_simhash.PHASE_RAW_LEN:
                        continue
                    src_docs_sim.append(['%s:%s' % (src_doc_id, i), Simhash(get_features(src_phase))])
                    src_set.update(
                        # 相似句子内容，相似文档句子数, 其他字段信息
                        {'%s:%s' % (src_doc_id, i): [src_phase, len(src_doc_phases), sim_doc_data]})
            except:
                log.error(traceback.format_exc().replace('\n', ' '))

            sim_index_start = time.time()
            index = SimhashIndex(src_docs_sim, k=self.pdistinct)
            s1 = Simhash(get_features(doc_phase))
            sim_sames = index.get_near_dups(s1)
            sim_index_end = time.time()
            log.info('sim_index_time ' + str(sim_index_end - sim_index_start))
            if len(sim_sames) == 0:
                continue

            # doc_same_src.update({phase_id: []})
            for same_id in sim_sames:
                # doc_same_src[phase_id].append({same_id: src_set[same_id]})
                # 原文句子id,原文句子内容,相似句子相关字段信息
                emit_data = (sen_id, [project, doc_phase, src_set[same_id], same_id])
                yield  emit_data

    def phase_to_phase(self,data):
        # log.info(data)
        sen_id = data[0]
        id_split = sen_id.split(':')
        gets = data[1]
        # 原文章标题
        project = gets[0]
        # 原文章句子内容
        doc_phase = gets[1]
        # 相似句子相关字段信息
        sam_doc_prop = gets[2][2]
        log.debug('data detail ' + json.dumps(sam_doc_prop, ensure_ascii=False))
        # 相似片段内容
        sam_phase = gets[2][0]
        # 　相似片段ｉｄ == '%s:%s' % (src_doc_id, i)
        same_id = gets[3]
        # 计算相似片段差异 leftcontent : rightcontent
        right_doc_phase, right_doc_phase_word_count = mark_same_content(copy.deepcopy(sam_phase.strip()),
                                                                        copy.deepcopy(doc_phase.strip()), "sim gray")

        left_sam_phase, left_sam_phase_word_count = mark_same_content(copy.deepcopy(doc_phase.strip()),
                                                                      copy.deepcopy(sam_phase.strip()), "lsim gray")
        phase_sam_score = float(right_doc_phase_word_count * 100) / float(len(unicode(doc_phase.strip())))
        sim_rate_value = round(phase_sam_score, 3)

        '''
        sam_doc_prop ::
         {
                    "project": doc_body["project"],
                    "finical_unit": doc_body["finical_unit"],
                    "finical_name": doc_body["finical_name"],
                    "date": doc_body["date"],
                    "doc": doc_body["doc"],
                    "unit": doc_body["unit"],
                    "finical": doc_body["finical"],
                    "fl_type": doc_body["fl_type"],
                    "uuid": doc_body["uuid"],
                    "doc_content_len": len(doc_phase),
                    "sam_content_len": dlen,
                    "sentences_count""sentences_count
                }
        '''

        sam_detail = {
            "same_doc_title": sam_doc_prop['project'],
            "find_sam_sentence": left_sam_phase,
            "sam_in_phase": "",
            "doc_sentence": right_doc_phase,
            "submiter": sam_doc_prop['submiter'],
            "upload_at": sam_doc_prop['date'],
            "wordcount": len(doc_phase.strip()),
            "sim_rate_value": sim_rate_value,
            "sim_rate": unicode(sim_rate_value) + u'%',
            "doc_sentence_word_count": right_doc_phase_word_count,
            "sam_sentence_word_count": left_sam_phase_word_count,
            "doc_sentence_id": id_split[1],
            "sam_sentence_id": same_id,
            "sentences_count": sam_doc_prop['sentences_count'],
            "sentence": doc_phase,
            "find_sentence": sam_phase,
            "doc_title":project,
            "doc_sentence_uuid":sen_id,
        }
        ssentence_id = sam_detail['sam_sentence_id']
        ssentence_id_split = ssentence_id.split(':')
        # 原文uuid+':'+相似文章uuid+':'+原文句子id+':'+相似句子id
        id_split = sen_id.split(':')
        doc_uuid = id_split[0]
        rowkey = doc_uuid + ':' + ssentence_id_split[0] + ':' + id_split[1] + ':' + ssentence_id_split[1]
        result = sam_detail
        log.debug(json.dumps(sam_detail, ensure_ascii=False))
        return result

    def build_queue_spout_unit(self,sentences,docid,project):
        # result = []
        sentence_id = 0
        sentences_count = len(sentences)
        i = 0
        for content in sentences:
            if len(content.strip()) > 5:
                i+=1
                # result.append({u'sentence_id': u'%s:%s' % (docid, sentence_id), u'project': unicode(project),
                #                u'content': unicode(content), u'sentences_count': unicode(sentences_count)})
                yield {u'sentence_id': u'%s:%s' % (docid, sentence_id), u'project': unicode(project),
                               u'content': unicode(content), u'sentences_count': unicode(sentences_count)}
            sentence_id += 1
            if i >= artcles_simhash.MAX_SENTENCE_NUM:
                break
        # return result

    def is_exists_repeat_row(self,search_uuid):
        try:
            source = self.es.get_source(index=self.INDEX_DATA_CENTER, doc_type=self.REPEAT_TYPE_TABLE,id=search_uuid)
            strdata = source['data']
            meta =json.loads(strdata)
            return meta
        except:
            # log.error(traceback.format_exc())
            pass
        return  None

    def make_es_source(self,search_uuid,score):
        source = self.es.get_source(index=self.INDEX_DATA_CENTER, doc_type=self.DOC_TYPE_TABLE,id=search_uuid)
        source.update({"repeat_score":score})
        self.es.index(index=self.INDEX_DATA_CENTER, doc_type=self.DOC_TYPE_TABLE,id=search_uuid,body=source)

    def put_result(self,search_uuid,data):
        body = json.dumps(data,ensure_ascii=False)
        self.es.index(index=self.INDEX_DATA_CENTER, doc_type=self.REPEAT_TYPE_TABLE,id=search_uuid,body={'data':body})

    def main_calc(self,search_uuid,suuid = None):
        '''
        计算综合评价、相似详情、相似片段
        :param search_uuid: 匹配相似的文档 id
        :param suuid: 消费者组表述，最好是单个用户全局特征，例如ip地址
        :return:
        '''
        start = time.time()
        input_doc = self.get_con_one(search_uuid)
        input_content = input_doc['content']
        # 拆分断落
        split_doc_phases = art_get_phase(input_content)
        found = self.is_exists_repeat_row(search_uuid)
        if found is not None:
            return found
        doc_data = []
        rlist= []
        multiprocessingstarttime = time.time()
        pool = multiprocessing.Pool(processes=artcles_simhash.PROCESSNUM)
        for sen_item in  self.build_queue_spout_unit(split_doc_phases,search_uuid,input_doc['project']):
            try:
               dre = pool.apply_async(phase_detail, args = (sen_item,))
               rlist.append(dre)
            except:
                log.error(traceback.format_exc())
        for rq in rlist:
            try:
                doc_data.extend(rq.get())
            except:
                log.error(traceback.format_exc())
        pool.close()
        pool.join()
        mark_set = u''',.?'!<>，。？《》！[]()（）【】;；:： '''
        dcc = ''
        multiprocessingendtime = time.time()
        for mark in mark_set:
            dcc = input_content.replace(mark, '')

        word_count = len(list(jieba.cut(dcc)))
        single_word_count = len(unicode(dcc))
        parse_count = dcc.count('\n')
        sentence_set = {}
        content_diff_map = {}
        log.info(json.dumps(doc_data,ensure_ascii=False))

        calc_time_start = time.time()
        for sentence_detail in doc_data:
            sentence_detail['doc_sentence_id'] = int(sentence_detail['doc_sentence_id'])
            #doc_sent_id -> list sam_doc_sent_id
            sam_id = sentence_detail['doc_sentence_uuid']
            # 去从并按分值排序
            if sam_id not in sentence_set.keys():
                sentence_set.update({sam_id: []})
            sentence_set[sam_id].append({sentence_detail['sim_rate_value']: sentence_detail})

            # 文本差异映射列表
            sam_sentence_id = sentence_detail['sam_sentence_id']
            sam_sentence_id_split = sam_sentence_id.split(':')
            same_doc_id = sam_sentence_id_split[0]
            doc_sentence_id = sentence_detail['doc_sentence_id']

            diff_list = content_diff_map.get(same_doc_id, [])
            sdetail = {sentence_detail['sim_rate_value']:{
                'doc_sentence': sentence_detail['doc_sentence'],
                'find_sam_sentence': sentence_detail['find_sam_sentence'],
                'wordcount': len(unicode(sentence_detail['find_sentence'].strip())),
                'sentence': sentence_detail['sentence'],
                'score': sentence_detail['sim_rate'],
                'doc_sentence_id':doc_sentence_id,
                'sam_sentence_id': sam_sentence_id
            }}
            diff_list.append(sdetail)
            content_diff_map.update({same_doc_id: diff_list})

        sam_sent_unique = []
        sam_doc_score = {}
        max_score_set = []
        distribution = []
        # 获取最大分数
        check_count = 0
        sam_count = 0
        source_count = 0
        isFirst = True
        docDetail = {}
        isHad = False
        doc_same_list = []
        same_info_content = copy.deepcopy(input_content)
        sim_doc_map = {}
        # 逐句的相似
        # gobal_sam_senc_count = 0
        for doc_sentence_uuid, sam_sentence in sentence_set.items():
            sam_sentence.sort(reverse=True)
            sam_detail = sam_sentence[0].values()[0]

            score = sam_detail['sim_rate_value']
            max_score_set.append(score)
            classname = 0
            str_classname = 'warn'
            local = int(float(sam_detail['doc_sentence_id']) * 100 / float(sam_detail['sentences_count']))
            if 40 >= score < 70:
                classname = 1
            elif score >= 70:
                classname = 2
                str_classname = 'serious'
            distribution.append({'local': local, 'type': classname})

            # same_info 内容替换 start:
            orig_sent = sam_detail['sentence'].strip()
            doc_sent_id = int(sam_detail['doc_sentence_id'])
            link_txt = u'''<a onclick="simInfo(this);" href="javascript:void(0);" source="%s" class="%s" id="%s" local="%s" >%s</a>''' % (
                sam_detail['sim_rate'], str_classname, doc_sent_id,
                local, orig_sent)
            same_info_content = same_info_content.replace(orig_sent, link_txt)
            # same_info 内容替换 end:

            # 分数累加
            check_count = check_count + int(sam_detail['wordcount'])
            sam_count = sam_count + int(sam_detail['doc_sentence_word_count'])
            # gobal_sam_senc_count += 1
            source_count = source_count + float(score) * float(sam_detail['wordcount'])

            if isFirst:
                docDetail = sam_detail
                isFirst = False
                isHad = True

            # 相似列表

            sam_sentence_id = sam_detail['sam_sentence_id']
            sam_sent_id_split = sam_detail['sam_sentence_id'].split(':')
            sam_id = sam_sent_id_split[0]
            eq = '%s:%s' % (sam_sentence_id , doc_sent_id)

            # 取最高分的逐句
            if eq not in sam_sent_unique:
                sam_sent_unique.append(eq)
                if sam_id not in sam_doc_score.keys():
                    sam_doc_score.update({sam_id: [0.0, {'come_from': ''
                        , 'upload_at': sam_detail['upload_at']
                        , 'upload_for': sam_detail['submiter']
                        , 'doc_name': sam_detail['same_doc_title']
                        , 'info_url': ''
                        , 'uuid': sam_id
                        }]})

                sam_doc_score[sam_id][0] = sam_doc_score[sam_id][0] + float(sam_detail['sim_rate_value']) * float(sam_detail['wordcount'])

        if isFirst:
            # 没有数据，跳出
            return None

        sam_phase_content = []
        dcontent_ids = []


        for sam_doc_id, detail in sam_doc_score.items():
            data_detail = detail[1]
            iscore = detail[0]
            # 文章列表分数
            doc_score = min(round(iscore / float(single_word_count), 3),97)
            if doc_score >= 0.05:
                data_detail.update({"source": str(doc_score) + '%'})
                doc_same_list.append({iscore: data_detail})

            # sam_info 组装右边数据结构 start :
        same_map_unique = []
        for sam_doc_id,diff_cons in content_diff_map.items():
            diff_cons.sort(reverse=True)
            for dutil in diff_cons:
                diff_con = dutil.values()[0]
                sen_id = diff_con['doc_sentence_id']
                unique_m_id = str(sen_id) +':'+ diff_con['sam_sentence_id']
                if unique_m_id in same_map_unique:
                    continue
                same_map_unique.append(unique_m_id)
                if sen_id not in dcontent_ids:
                    dcontent_ids.append(sen_id)
                    localvalue = int(float(sen_id) * 100 / float(docDetail['sentences_count']))
                    link_txt = u'''<a href="javascript:parseSimInfo('%s')" class="%s" id="%s" local="%s">%s</a>''' % (
                        sen_id, "black", sen_id, str(localvalue), diff_con['sentence'])
                    sam_phase_content.append({sen_id: [link_txt, localvalue]})

                mapsets = sim_doc_map.get(sen_id, [])
                sdetail = {
                    "uuid": sam_doc_id,
                    "title": docDetail['doc_title'],
                    "index_parse": diff_con['doc_sentence'],
                    "sim_parse_doc": "",
                    "sim_parse": diff_con['find_sam_sentence'],
                    "submiter": data_detail['upload_for'],
                    "upload_at": data_detail['upload_at'],
                    "wordcount": diff_con["wordcount"],
                    "sim_rate": diff_con['score']
                }
                mapsets.append(sdetail)
                sim_doc_map.update({sen_id: mapsets})

                # sam_info 组装右边数据结果 end:

        doc_same_list.sort(reverse=True)
        # sam_info

        data = {"content": same_info_content.replace('\n', '<br>'), "right": sim_doc_map}
        info_result = {'project': docDetail['doc_title'], 'uuid': docDetail['doc_sentence_uuid'].split(':')[0],
                       'data': data}
        # sam_phase
        sam_phase_content.sort()
        data_parse_result_content = []
        for d in sam_phase_content:
            vd = d.values()[0]
            data_parse_result_content.append({'id': d.keys()[0], 'name': vd[0], 'local': vd[1]})

        phase_main_data = {"content": data_parse_result_content, "right": sim_doc_map}
        phase_result = {'project': docDetail['doc_title'], 'uuid': docDetail['doc_sentence_uuid'].split(':')[0],
                        'data': phase_main_data}

        # sam_comment 整体平均分
        gobal_score = min(round(float(source_count) / float(single_word_count), 3),97)

        data = {}
        if isHad:
            data = {"sim_source": str(gobal_score) + "%", "title": docDetail['doc_title'], "same_list": doc_same_list,
                    "check_count": check_count, "sim_count": sam_count, "word_count": word_count,
                    "parse_count": parse_count,
                    "single_word_count": single_word_count,
                    "distribution": distribution,
                    'sentence_count': docDetail['sentences_count'],
                    'sim_original': str(100.0 - gobal_score) + '%'}

        result = {'project': docDetail['doc_title'], 'uuid': docDetail['doc_sentence_uuid'].split(':')[0], 'data': data}
        end = time.time()
        log.info(start)
        log.info('multprocess start time %s' % multiprocessingstarttime)
        log.info('multprocess end time %s' % multiprocessingendtime)
        log.info('calc start time %s' % calc_time_start)
        log.info(end)
        # 插入结果
        calc_result = {'sam_comment':result,'sam_info':info_result,'sam_phase':phase_result}
        try:
            self.put_result(search_uuid, calc_result)
        except:
            log.error(traceback.format_exc())
        # es分值
        try:
            # 插入的是百分数
            self.make_es_source(search_uuid,gobal_score)
        except:
            log.error(traceback.format_exc())
        return calc_result

    def calc_task(self):
        '''通过扫描es插入数据到neo4j'''
        q = {
                 "query": {
                    "bool": {"must_not": [
                        {"exists" : { "field" : "repeat_score" }}
                    ]}
                }
        }
        res = self.es.scan_source(index=self.INDEX_DATA_CENTER, doc_type=self.DOC_TYPE_TABLE, query=q)
        cnum = self.es.count(index=self.INDEX_DATA_CENTER, doc_type=self.DOC_TYPE_TABLE, body=q)['count']
        i = 0
        for row in res:
            i += 1
            try:
                log.info('%s / %s' % (i, cnum))
                log.info(self.main_calc(row['_id']))
                log.info('------------------------ success ------------------------')
            except:
                log.error(traceback.format_exc())

def phase_detail(sen_item):
    try:
        self = artcles_simhash()
        doc_data = []
        search_and_sim_start_time = time.time()
        for search_item in self.search_es_sim(sen_item['sentence_id'], unicode(sen_item['project']),
                                              unicode(sen_item['content']), sen_item['sentences_count']):
            try:
                pitem = self.phase_to_phase(search_item)
                if pitem:
                    doc_data.append(pitem)
            except:
                log.error(traceback.format_exc())
        search_and_sim_end_time = time.time()
        log.info('search_and_sim_time ' + str(search_and_sim_end_time - search_and_sim_start_time))
        return doc_data
    except:
        log.error(traceback.format_exc())
    return []

if __name__ == '__main__':
          am = artcles_simhash()
          am.calc_task()
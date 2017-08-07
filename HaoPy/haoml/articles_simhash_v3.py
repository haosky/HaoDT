# -*- coding: utf-8 -*-
import traceback
from haohbase.hbase_dao import hbase_dao
import jieba
from haounits.loggerDefTools import get_defTestLogger
from haounits.cfgOptionTools import get_items_in_cfg, get_uri_relative_parent_package
import json
import sys
import uuid
import copy
from haohbase.hbase.ttypes import TScan
from haokafka.same_art.phase2kafka import phase2kafka
from haoml.articlesimhash import art_get_phase
log = get_defTestLogger()
import haostorm.check_repeat as mainparent
import time
reload(sys)
sys.setdefaultencoding('utf8')


class artcles_simhash():


    QSDL_TYPE = 'caizheng'
    caizheng_t1 = 'MoNi__v2'
    caizheng_row_t1 = 'MoNi__v2_row'

    def __init__(self):
        self.__sim_config_file_path = get_uri_relative_parent_package(mainparent, 'sim_settings.properties')
        table_config = 'hbase_table'
        self.caizheng_table = get_items_in_cfg(table_config, 'caizheng_table',
                                                     self.__sim_config_file_path)

        self.exists_table = get_items_in_cfg(table_config, 'exists_table',
                                                     self.__sim_config_file_path)

        self.phase_table =  get_items_in_cfg(table_config, 'phase_table',
                                                     self.__sim_config_file_path)

        self.ks = ["project", "finical_unit", "finical_name", "date", "doc", "content", "unit", "finical","fl_type"]
        self.art_phase_sim_parse = None


    def get_hbase_con_one(self, docid):
        hd = hbase_dao()
        rec = hd.get(self.caizheng_table, docid)
        result = {"uuid":docid}
        for col in rec.columnValues:
            result.update({col.qualifier : col.value} )
        return result

    def scan_data_rowprex(self,docid,table):
        # fs = " ColumnPaginationFilter(%d, %d) AND PrefixFilter('%s')" % ( 100,0,rowprex)
        # columns = []
        #
        # for k in ks:
        #     columns.append(TColumn(family='a', qualifier=k))
        fs = "PrefixFilter('%s:')" %  docid
        scan = TScan(filterString=fs
                     # ,columns=columns
                    )
        return self.scan_data_list(scan,table)

    def scan_data_list(self,scan,table):
        hd = hbase_dao()
        groups = []
        scanner = hd.open_scan(table, scan)
        r = hd.client.getScannerRows(scanner, 30)
        i = 0
        maxrow = 30
        while r:
            try:
                i += 1
                if i>= maxrow:
                    break
                for c in r:
                    rowdata = {}
                    for cv in c.columnValues:
                        cm = cv.qualifier.strip()
                        rowdata.update({cm: cv.value})
                    groups.append(rowdata)
                r = hd.client.getScannerRows(scanner, 30)
            except:
                log.error(traceback.format_exc())
        return groups

    def consumer_result(self,doc2ka,group, doc_uuid):
        # doc2ka = phase2kafka()
        balanced_consumer = doc2ka.consumer_es_same_phase(str(group), str(doc_uuid))
        result = []
        for message in balanced_consumer:
            if message is not None:
                try:
                    mvalue = message.value
                    sent_com = json.loads(mvalue)
                    log.debug(mvalue)
                    balanced_consumer.commit_offsets()
                    result.append(sent_com)
                except:
                    log.error(traceback.format_exc().replace('\n', ' '))
        return result

    def main_calc(self,search_uuid,suuid = None):
        '''
        计算综合评价、相似详情、相似片段
        :param search_uuid: 匹配相似的文档 id
        :param suuid: 消费者组表述，最好是单个用户全局特征，例如ip地址
        :return:
        '''
        start = time.time()
        input_doc = self.get_hbase_con_one(search_uuid)
        input_content = input_doc['content']
        split_doc_phases = art_get_phase(input_content)
        con_start = 0
        con_stop = 0
        # 判断hbase 是否存在记录，如果没有插入kafka队列数据，并监听
        hd = hbase_dao()
        isexists = hd.exists(self.exists_table,search_uuid)
        kafka_queue = []
        if isexists:
            kafka_queue = self.scan_data_rowprex(search_uuid,self.phase_table)
        # 插入kafka
        else:
            try:
                doc2ka = phase2kafka()
                doc2ka.producer_es_split_phases({'sentences': split_doc_phases,
                                                 'docid': search_uuid,
                                                 'project': input_doc['project']})
                con_start = time.time()
                # time.sleep(3)
                if suuid is None:
                    uuid_str = str(uuid.uuid1())
                else:
                    uuid_str = suuid
                kafka_queue = self.consumer_result(doc2ka,uuid_str,search_uuid)
                con_stop = time.time()
            except:
                log.error(traceback.format_exc().replace('\n',''))
            print self.exists_table
            isexists = hd.exists(self.exists_table, search_uuid)
            if isexists:
                kafka_queue = self.scan_data_rowprex(search_uuid, self.phase_table)
        #
        mark_set = u''',.?'!<>，。？《》！[]()（）【】;；:： '''
        dcc = ''
        for mark in mark_set:
            dcc = input_content.replace(mark, '')

        word_count = len(list(jieba.cut(dcc)))
        single_word_count = len(unicode(dcc))
        parse_count = dcc.count('\n')

        # ---

        sentence_set = {}
        content_diff_map = {}

        for sentence_detail in kafka_queue:
            print(json.dumps(sentence_detail,ensure_ascii=False))
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

            # diff_con_list = content_diff_map[sam_doc_id]
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
        # gobal_score = round(float(source_count) / float(gobal_sam_senc_count), 3)

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
        print(start)
        print(end)
        print(con_start)
        print(con_stop)
        calc_result = {'sam_comment':result,'sam_info':info_result,'sam_phase':phase_result}
        return calc_result


if __name__ == '__main__':
    print json.dumps(artcles_simhash().main_calc('15921870063261156110b74bd869246b53fb8ff257b1cc2758ab'),ensure_ascii=False)

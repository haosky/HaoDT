# -*- coding: utf-8 -*-from pyleus.storm import SimpleBoltimport tracebackfrom pyleus.storm import namedtuplefrom haounits.loggerDefTools import get_defFileLogger as getlog,get_defTestLoggerfrom haoml.articles_simhash_v2 import  artcles_simhashfrom haoml.articlesimhash import art_get_phase,get_features,get_sim_distance,calc_distince,mark_same_content,get_different_2_docfrom haounits.cfgOptionTools import get_items_in_cfg, get_uri_relative_parent_packagefrom simhash import Simhash, SimhashIndeximport haostorm.check_repeat.qdsl as qsdlparentimport haostorm.check_repeat as repparentimport jsonimport sysreload(sys)sys.setdefaultencoding('utf-8')__author__ ='hao'log = getlog(fileName="es_search_phase2doc_bolt.log",loggerMain='es_search_phase2doc_bolt')# import logging# log = get_defTestLogger(level=logging.DEBUG)pass_obj = namedtuple("doc","key value")class es_search_phase2doc_bolt(SimpleBolt):    OUTPUT_FIELDS = pass_obj    # 搜索返回多少篇    PHASE_TO_DOC_LEN = 3    # 匹配相似的字数    PHASE_RAW_LEN = 8    '''    从es查询片段    content input should be unicode    '''    def initialize(self):        self.sa = artcles_simhash()        self.__settings_file = get_uri_relative_parent_package(repparent, 'sim_settings.properties')        self.pdistinct = int(get_items_in_cfg("simhash","doc2phase_distinct" ,                                                     self.__settings_file))    def process_tuple(self, tup):        try:            data = tup.values            log.info(data)            sen_id = data[0]            id_split = sen_id.split(':')            gets = data[1]            # 句子            doc_phase = unicode(gets[1])            # 文章uuid            docid = id_split[0]            #　标题名称            project = gets[0]            # 句子id            phase_id = gets[1]            # 句子数            sentences_count = gets[2]            log.info('search str'+ doc_phase)            search_es_list = self.sa.get_es_row_with_count(doc_phase,es_search_phase2doc_bolt.PHASE_TO_DOC_LEN)            src_docs_sim = []            src_set = {}            for src_doc in search_es_list:                try:                    src_doc_id = src_doc['_id']                    log.info(src_doc_id)                    if src_doc_id == docid:                        continue                    doc_body = src_doc['_source']                    if 'content' not in doc_body:                        continue                    if doc_body['project'] == project:                        continue                    dcon = unicode(doc_body['content'])                    src_doc_phases = art_get_phase(dcon)                    i = -1                    sim_doc_data = {                        "project": doc_body["project"],                        "finical_unit": doc_body["finical_unit"],                        "finical_name": doc_body["finical_name"],                        "date": doc_body["date"],                        "submiter": doc_body.get("submiter",""),                        "doc": doc_body["doc"],                        "unit": doc_body["unit"],                        "finical": doc_body["finical"],                        "fl_type": doc_body["fl_type"],                        "uuid": doc_body["_uuid"],                        "sentences_count":sentences_count                    }                    for src_phase in src_doc_phases:                        i += 1                        src_phase = unicode(src_phase.strip())                        if (len(src_phase.replace(u' ', u''))) < es_search_phase2doc_bolt.PHASE_RAW_LEN:                            continue                        src_docs_sim.append(['%s:%s' % (src_doc_id, i), Simhash(get_features(src_phase))])                        src_set.update(                            # 相似句子内容，相似文档句子数, 其他字段信息                            {'%s:%s' % (src_doc_id, i): [src_phase, len(src_doc_phases),sim_doc_data]})                except:                    log.error(traceback.format_exc().replace('\n',' '))                # doc_same_src={}                index = SimhashIndex(src_docs_sim, k=self.pdistinct)                s1 = Simhash(get_features(doc_phase))                sim_sames = index.get_near_dups(s1)                if len(sim_sames) == 0:                    continue                # doc_same_src.update({phase_id: []})                for same_id in sim_sames:                    # doc_same_src[phase_id].append({same_id: src_set[same_id]})                    # 原文句子id,原文句子内容,相似句子相关字段信息                    emit_data = (sen_id, [project,doc_phase,src_set[same_id],same_id])                    log.info("sam ----doc_phase %s: src_set[same_id] %s" % (doc_phase,src_set[same_id]))                    self.emit(emit_data)                    log.info("emit")                #'''docid+phaseid:same_list'''                '''                result:                docid+phaseid ,['project','phase',{'same_doc_items'},'same_doc_content',same_id]              '''        except Exception as e:            log.error(traceback.format_exc().replace('\n',' '))if __name__ == "__main__":    es_search_phase2doc_bolt().run()# ## # # @Test# from haostorm.testSite.SimpleBolt_MN import SimpleBolt# if __name__ == '__main__':#     es_sd = es_search_phase2doc_bolt()#     es_sd.initialize()#     class tup :#         values=['0000d71e38eda15c2cb789b8c72bb4c5:0', ['\xe6\xb1\x9f\xe9\x97\xa8\xe5\xb8\x822017\xe5\xb9\xb4\xe6\x89\xb6\xe6\x8c\x81\xe5\xb9\xbf\xe4\xb8\x9c\xe7\x9c\x81\xe8\x8c\xb6\xe5\x8f\xb6\xe6\x9c\xba\xe6\xa2\xb0\xe8\xbf\x9e\xe7\xbb\xad\xe5\x8c\x96\xe5\x8a\xa0\xe5\xb7\xa5\xe6\x88\x90\xe5\xa5\x97\xe8\xae\xbe\xe5\xa4\x87\xe9\xa1\xb9\xe7\x9b\xae\xe7\x94\xb3\xe6\x8a\xa5\xe6\xb1\x87\xe6\x80\xbb\xe8\xa1\xa8x', '\xe9\x99\x84\xe4\xbb\xb65-1\xef\xbc\x9a\xe6\xb1\x9f\xe9\x97\xa8\xe5\xb8\x822017\xe5\xb9\xb4\xe6\x89\xb6\xe6\x8c\x81\xe5\xb9\xbf\xe4\xb8\x9c\xe7\x9c\x81\xe8\x8c\xb6\xe5\x8f\xb6\xe6\x9c\xba\xe6\xa2\xb0\xe8\xbf\x9e\xe7\xbb\xad\xe5\x8c\x96\xe5\x8a\xa0\xe5\xb7\xa5\xe6\x88\x90\xe5\xa5\x97\xe8\xae\xbe\xe5\xa4\x87\xe9\xa1\xb9\xe7\x9b\xae\xe7\x94\xb3\xe6\x8a\xa5\xe6\xb1\x87\xe6\x80\xbb\xe8\xa1\xa8\xe5\xa1\xab\xe6\x8a\xa5\xe5\x8d\x95\xe4\xbd\x8d\xef\xbc\x88\xe5\x9c\xb0\xe7\xba\xa7\xe5\xb8\x82\xef\xbc\x89\xef\xbc\x9a\xe6\xb1\x9f\xe9\x97\xa8\xe5\xb8\x82\xe6\x96\xb0\xe4\xbc\x9a\xe9\x99\x88\xe7\x9a\xae\xe6\x9d\x91\xe5\xb8\x82\xe5\x9c\xba\xe8\x82\xa1\xe4\xbb\xbd\xe6\x9c\x89\xe9\x99\x90\xe5\x85\xac\xe5\x8f\xb8\xc2\xa0\xc2\xa0\xc2\xa0\xc2\xa0\xc2\xa0\xc2\xa0\xc2\xa0\xc2\xa0\xc2\xa0\xc2\xa0\xc2\xa0\xc2\xa0\xc2\xa0\xc2\xa0\xc2\xa0\xe5\x8d\x95\xe4\xbd\x8d\xef\xbc\x9a\xe4\xb8\x87\xe5\x85\x83\xe5\xba\x8f\xe5\x8f\xb7\t\xe5\xb8\x82\xef\xbc\x88\xe5\x8e\xbf\xe3\x80\x81\xe5\x8c\xba\xef\xbc\x89\t\xe9\xa1\xb9\xe7\x9b\xae\xe6\x89\xbf\xe6\x8b\x85\xe5\x8d\x95\xe4\xbd\x8d\t\xe5\xbb\xba\xe8\xae\xbe\xe5\x86\x85\xe5\xae\xb9\t\xe5\xbb\xba\xe8\xae\xbe\xe5\x9c\xb0\xe7\x82\xb9\t\xe7\xbb\xa9\xe6\x95\x88\xe7\x9b\xae\xe6\xa0\x87\t\xe7\x94\xb3\xe6\x8a\xa5\xe8\xb4\xa2\xe6\x94\xbf\xe8\xa1\xa5\xe5\x8a\xa9\xe9\x87\x91\xe9\xa2\x9d\t\xe6\x8a\xa5\xe9\x80\x81\xe6\x96\x87\xe5\x8f\xb7\t\xe5\xa4\x87\xe6\xb3\xa81\t\xe6\xb1\x9f\xe9\x97\xa8\xe5\xb8\x82\xe6\x96\xb0\xe4\xbc\x9a\xe5\x8c\xba\t\xe6\xb1\x9f\xe9\x97\xa8\xe5\xb8\x82\xe6\x96\xb0\xe4\xbc\x9a\xe9\x99\x88\xe7\x9a\xae\xe6\x9d\x91\xe5\xb8\x82\xe5\x9c\xba\xe8\x82\xa1\xe4\xbb\xbd\xe6\x9c\x89\xe9\x99\x90\xe5\x85\xac\xe5\x8f\xb8\t\xe6\x9f\x91\xe6\x99\xae\xe8\x8c\xb6\xe7\x9a\x84\xe7\xa0\x94\xe5\x8f\x91\xe4\xb8\x8e\xe7\x94\x9f\xe4\xba\xa7\t\xe6\xb1\x9f\xe9\x97\xa8\xe5\xb8\x82\xe6\x96\xb0\xe4\xbc\x9a\xe9\x99\x88\xe7\x9a\xae\xe6\x9d\x91\t2017\xe5\xb9\xb4\xe4\xba\xa7\xe5\x80\xbc3000\xe4\xb8\x87\xe5\x85\x83\t240\t\xe7\xb2\xa4\xe5\x86\x9c\xe8\xae\xa1[2016]49\xe5\x8f\xb7\t2\t\t\t\t\t\t\t\t\xe5\x88\xb6\xe8\xa1\xa8\xe4\xba\xba\xef\xbc\x9a\xe9\x98\xae\xe5\xb8\x8c\xe5\x87\xa1    \xe5\xae\xa1\xe6\xa0\xb8\xe4\xba\xba\xef\xbc\x9a\xc2\xa0\xc2\xa0\xc2\xa0\xc2\xa0\xc2\xa0\xc2\xa0\xe8\x81\x94\xe7\xb3\xbb\xe7\x94\xb5\xe8\xaf\x9d\xef\xbc\x9a13542146465\xc2\xa0\xc2\xa0\xe5\xa1\xab\xe6\x8a\xa5\xe6\x97\xa5\xe6\x9c\x9f\xef\xbc\x9a2016\xe5\xb9\xb410\xe6\x9c\x8826\xe6\x97\xa5', '1']]#     es_sd.process_tuple(tup())
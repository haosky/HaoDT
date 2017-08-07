# -*- coding: utf-8 -*-
from haokafka.same_art.phase2kafka import phase2kafka
from haohbase.hbase_dao import hbase_dao
from haohbase.hbase.ttypes import TScan,TColumn
from haoml.articlesimhash import art_get_phase
from haokafka.kafkaQueue.Skins.sampleSkin import actObjSkin
from haoml.articlesimhash import get_content_simvalue, main_calc ,get_sim_distance
from haoml.articles_simhash_v2 import  artcles_simhash
from haoml.articles_simhash_v3 import  artcles_simhash as artcles_simhash_v3
import time
import json
import traceback
class queue_for_hbase():

    def __init__(self):
        self.asm = artcles_simhash()
        self.phase2kafka = phase2kafka()
        self.balanced_consumer = self.phase2kafka.consumer_es_search_doc()
        self.hdao = hbase_dao()
        self.ks = ['content','project']
        aco = actObjSkin()
        self.topic = aco.get_topic(phase2kafka.ES_PHASE_TASK_NAME)
        self.producer = self.topic.get_sync_producer()


    def destory(self):
        self.producer.stop()

    def push_kafka_queue(self,data):
        content = data['content']
        docid =  data['row']
        project = data['project']
        sentences = art_get_phase(content)
        result_gen = self.phase2kafka.build_queue_spout_unit({'sentences': sentences, 'docid':docid, 'project':project})
        for result in result_gen:
            time.sleep(0.2)
            self.producer.produce(json.dumps(result))


    def scan_hbase_table_do_fun(self,fun,table):
        # fs = "PrefixFilter('%s')" % rowprex
        columns = []
        for k in self.ks:
            columns.append(TColumn(family='a', qualifier=k))
        scan = TScan(
                    # filterString=fs,
                     columns=columns,
            startRow='006e80ae069bc906ea4e76d3f9fec41e'
        )
        scanner = self.hdao.open_scan(table, scan)
        r = self.hdao.client.getScannerRows(scanner, 3000)
        print '---------@'
        i = 0
        row = ''
        try:
            while r:
                try:
                    i += 1
                    for c in r:
                        row = c.row
                        print row
                        rowdata = {'row':row}
                        for cv in c.columnValues:
                            cm = cv.qualifier.strip()
                            if cm in self.ks:
                                rowdata.update({cm: cv.value})
                        if 'content' in rowdata.keys() and 'project' in rowdata.keys():
                            fun(rowdata)
                            # print rowdata
                    # r = self.hdao.client.getScannerRows(scanner, 30)
                    print 'c end'
                    r = None
                except:
                    print traceback.format_exc()
            print 'end--'
            print row
            print str(i)
        finally:
            self.destory()

    def scan_es(self,fun):
        res = self.asm.es.scan_source(index=self.asm.INDEX_DATA_CENTER ,doc_type=self.asm.DOC_TYPE_TABLE,query={})
        cnum = self.asm.es.count(index=self.asm.INDEX_DATA_CENTER, doc_type=self.asm.DOC_TYPE_TABLE, body={})['count']
        i = 0
        for row in res:
            try:
                d = row['_source']
                i += 1
                print '%s / %s' % (i,cnum)
                # if i <= 100:
                #     continue
                if self.hdao.exists('GDSpecialFinancial_SamExists',row['_id']):
                    continue
                rowdata = {'row': row['_id'], 'content': d['content'], 'project': d['project']}
                print row['_id']
                fun(rowdata)
            except:
                print traceback.format_exc()

    def search_es_kw(self,fun,kw):
        data = self.asm.get_search_list(kw)
        i =0
        for vc in data:
            i+=1
            d = vc.values()[0]
            try:
                rowdata = {'row': d['uuid'],'content':d['content'],'project':d['project']}
                print d['uuid']
                if self.hdao.exists('GDSpecialFinancial_SamExists',d['_id']):
                    continue
                fun(rowdata)
            except :
                print traceback.format_exc()

if __name__ == '__main__':
    qh = queue_for_hbase()
    qh.scan_hbase_table_do_fun(qh.push_kafka_queue, 'GDSpecialFinancial')
    kz = ['大数据','专项资金申报书','专项资金','资金']
    # kz = [ '专项资金申报书', '专项资金', '资金']
    for k in kz :
        qh.search_es_kw(qh.push_kafka_queue,k)
    # 0010429e56b74e79679ddd31261aa113
    # qh.scan_es(qh.push_kafka_queue)
    qh.producer.stop()
# -*- coding: utf-8 -*-

from haokafka.kafkaQueue.Skins.sampleSkin import actObjSkin
import time
import json
__author__ = 'hao'

class phase2kafka():
    ES_PHASE_NAME = 'search_es_phase_queue2'
    ES_PHASE_TASK_NAME = 'search_es_task_phase_queue2'
    DOC_SAME_LIST_NAME = 'd2_'
    ES_PHASE_GROUP = 'def_es_group'

    def build_queue_spout_unit(self,phases):
        sentences = phases['sentences']
        docid = phases['docid']
        project = phases['project']
        # result = []
        sentence_id = 0
        sentences_count = len(sentences)
        for content in sentences:
            if len(content.strip()) > 5:
                # result.append({u'sentence_id': u'%s:%s' % (docid, sentence_id), u'project': unicode(project),
                #                u'content': unicode(content), u'sentences_count': unicode(sentences_count)})
                yield {u'sentence_id': u'%s:%s' % (docid, sentence_id), u'project': unicode(project),
                               u'content': unicode(content), u'sentences_count': unicode(sentences_count)}
            sentence_id += 1
        # return result

    def producer_es_split_phases(self, phases):
        '''
        句子插入kafka，作为storm的数据入口
        phases :: {docid:'',project:'',sentences:{
            id:content
        }
        result = {'sentence_id':'','project':'','content':''}
        '''
        result_gen = self.build_queue_spout_unit(phases)
        aco = actObjSkin()
        topic = aco.get_topic(phase2kafka.ES_PHASE_NAME)
        producer = topic.get_sync_producer()
        i = 0
        for result in result_gen:
            # @TODO
            i+=1
            time.sleep(0.2)
            if i>=100:
                break
            producer.produce(json.dumps(result))
        producer.stop()



    def producer_es_task_split_phases(self, phases):
        '''
        句子插入kafka，作为storm的数据入口
        phases :: {docid:'',project:'',sentences:{
            id:content
        }
        result = {'sentence_id':'','project':'','content':''}
        '''
        result_gen = self.build_queue_spout_unit(phases)
        aco = actObjSkin()
        topic = aco.get_topic(phase2kafka.ES_PHASE_TASK_NAME)
        producer = topic.get_sync_producer()
        for result in result_gen:
            time.sleep(0.2)
            producer.produce(json.dumps(result))
        producer.stop()

    def consumer_es_search_doc(self):
        aco = actObjSkin()
        queue = str(phase2kafka.ES_PHASE_NAME)
        topic = aco.get_topic(queue)
        balanced_consumer = topic.get_balanced_consumer(consumer_group=phase2kafka.ES_PHASE_GROUP
                                                        ,consumer_timeout_ms=5000
                                                        )
        return balanced_consumer

    def consumer_es_search_task_doc(self):
        aco = actObjSkin()
        queue = str(phase2kafka.ES_PHASE_TASK_NAME)
        topic = aco.get_topic(queue)
        balanced_consumer = topic.get_balanced_consumer(consumer_group=phase2kafka.ES_PHASE_GROUP,
                                                        consumer_timeout_ms=5000)
        return balanced_consumer


    def start_same_phase_producer(self,doc_uuid):
        aco = actObjSkin()
        queue = str(phase2kafka.DOC_SAME_LIST_NAME + doc_uuid)
        print type(queue)
        topic = aco.get_topic(queue)
        self.producer = topic.get_sync_producer()

    def consumer_es_same_phase(self,group, doc_uuid):
        '''
        在一定时间内，根据uuid获取所有相似的片段，一个用户对应一个消费者组
        '''
        aco = actObjSkin()
        queue = str(phase2kafka.DOC_SAME_LIST_NAME + doc_uuid)
        topic = aco.get_topic(queue)
        # consumer_timeout_ms 用户等待时间
        balanced_consumer = topic.get_balanced_consumer(consumer_group=group,
                                                        consumer_timeout_ms=aco.consumer_timeout_ms)
        return balanced_consumer

    def producer_same_phase(self, sam_detail):
        self.producer.produce(json.dumps(sam_detail))

    def stop_same_phase_producer(self):
        self.producer.stop()


# if __name__ == '__main__':

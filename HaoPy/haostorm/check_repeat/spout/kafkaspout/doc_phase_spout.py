# -*- coding: utf-8 -*-

from pyleus.storm import Spout
from pyleus.storm import namedtuple
import traceback
import json
import sys
from haounits.loggerDefTools import get_defFileLogger as getlog
from haokafka.same_art.phase2kafka import phase2kafka

reload(sys)
sys.setdefaultencoding('utf8')

__author__ = 'hao'
log = getlog(fileName="doc_phase_spout.log",loggerMain='doc_phase_spout')
pass_obj = namedtuple("kaphase","key value")
'''拉取kafka获取文章断落列表'''


class doc_phase_spout(Spout):
    # 定义输出结构
    OUTPUT_FIELDS = pass_obj

    def initialize(self):
        '''
        实现spout的初始化方法
        :return:
        '''
        self.init()

    def init(self):
        '''
        初始化kafka消费者
        :return:
        '''
        self.phase2kafka =  phase2kafka()
        self.balanced_consumer =self.phase2kafka.consumer_es_search_doc()


    def next_tuple(self):
        '''
        实现spout的next_tuple方法,spout将会持续执行该方法，处理业务逻辑
        :return: 调用emit 提交一个关键字
        '''
        try:
            for message in self.balanced_consumer:
                if message is not None:
                    try:
                        log.info(message.offset)
                        # 转载kafka的信息
                        phase = json.loads(message.value)
                        result = (phase['sentence_id'], [unicode(phase['project']), unicode(phase['content']),phase['sentences_count']])
                        self.emit((result))
                        log.info(result)
                        self.balanced_consumer.commit_offsets()
                    except:
                        log.error(traceback.format_exc().replace('\n', ' '))
                        break
        except:
            log.error(traceback.format_exc().replace('\n',' '))
            try:
                self.balanced_consumer.stop()
            except:
                log.error(traceback.format_exc().replace('\n', ' '))

if __name__ == "__main__":
    doc_phase_spout().run()

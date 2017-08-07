# -*- coding: utf-8 -*-

from haokafka.kafkaQueue.Skins.sampleSkin import actObjSkin
from haokafka.kafkaQueue.kafkaObjSkinInter import act_obj
import haokafka as parent
from haokafka.kafkaQueue.queueBase import queueBase
from haounits.loggerDefTools import get_defTestLogger
import msgpack

__author__ = 'hao'


class SampleQueue(queueBase):
    def __init__(self, ObjSkinInter):
            queueBase.__init__(self,ObjSkinInter)


# if __name__ == '__main__':
#
#     aco=actObjSkin()
#     ao=act_obj(aco,'test')
#     sq=SampleQueue(ao)
#     a={"a":"b"}
#     sq._push(config.weibo_home_queue,a)
#     d=sq._pop(config.weibo_home_queue)
#     for s in d :
#         print(msgpack.loads(s.value))
#         break


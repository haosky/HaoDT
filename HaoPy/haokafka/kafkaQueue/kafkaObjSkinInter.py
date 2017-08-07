# -*- coding: utf-8 -*-

import msgpack

__author__ = 'hao'


class act_obj():
    
    def __init__(self,obj_skin_interf,group):
        self.obj_skin_interf=obj_skin_interf
        self.group=group

    def pop(self,quename):
        balanced_consumer = self.obj_skin_interf.get_balanced_consumer(quename,self.group)
        try :
            for message in balanced_consumer:
                yield message
        finally:
            balanced_consumer.stop()

    def push(self,quename,value):
        topic = self.obj_skin_interf.get_topic(quename)
        producer = topic.get_sync_producer()
        producer.produce(msgpack.dumps(value))
        # dv="offset:%s" % topic.latest_available_offsets()
        producer.stop()
        # return dv

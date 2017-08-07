# -*- coding: utf-8 -*-

from pykafka import KafkaClient
from haounits.cfgOptionTools import get_items_in_cfg, get_uri_relative_parent_package
import haokafka as parent

__author__ = 'hao'


class actObjSkin:
    def __init__(self):
        self.__settings_file_path = get_uri_relative_parent_package(parent, 'kafka.properties')
        self.broker_hosts = get_items_in_cfg( 'server','broker_hosts', self.__settings_file_path)
        self.zookeeper_hosts = get_items_in_cfg( 'server','zookeeper_hosts', self.__settings_file_path)
        self.socket_timeout_ms = int(get_items_in_cfg( 'server','socket_timeout_ms', self.__settings_file_path))
        self.offsets_channel_socket_timeout_ms = int(get_items_in_cfg('server','offsets_channel_socket_timeout_ms',
                                                                   self.__settings_file_path))
        self.consumer_timeout_ms = int(get_items_in_cfg('server','user_consumer_timeout_ms',
                                                                   self.__settings_file_path))

    def get_balanced_consumer(self,queue,group):
        topic = self.get_topic(queue)
        balanced_consumer = topic.get_balanced_consumer(consumer_group=group,auto_commit_enable=True)
        return balanced_consumer

    def get_topic(self,queue):
        client = KafkaClient(hosts=self.broker_hosts,  zookeeper_hosts=self.zookeeper_hosts,
                             socket_timeout_ms=self.socket_timeout_ms,
                             offsets_channel_socket_timeout_ms=self.offsets_channel_socket_timeout_ms)
        topic = client.topics[queue]
        return topic
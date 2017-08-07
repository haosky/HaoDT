# -*- coding: utf-8 -*-

from haoneo4j.neo4junit import neo4junit,json_to_properties
from haomongodb.product_v1.modles.mongodb_modles import TableCols
from haounits.loggerDefTools import  get_defTestLogger as glog
import logging
import jieba


__author__ = 'hao'


class base_cyqoperator():

    class entry__relationship :
        relationship_name = None
        relationship_properties = {}
        '''
       relationship_properties =
       {'name':value,...}
       '''

        label_from = None
        label_to = None
        '''
       label_form or label_to =

        {
        'label':..
        'name':..
        'properties':{'name':value,...}
        }
       '''

        properties = {}

    entries = []
    '''
    [
    {
    'name':..
    'properties':{'name':value,...}
    }
    ]
    '''
    def __init__(self,neo=None,mongodb=None,logLEVEL=logging.INFO):
        self.neo = neo
        self.logLEVEL = logLEVEL
        self.mongodb = mongodb

    def keywords_int_cols(self, mongo_json, cols_name):
        return list(jieba.cut(mongo_json[cols_name]))

    def insert_entry(self):
        log = glog(level=self.logLEVEL ,clazz=base_cyqoperator)
        if not self.neo:
            self.neo = neo4junit()
        for entry in self.entries:
            name = entry['name']
            prop =  entry['properties']
            label = entry['label']
            insert_crystr = '''MERGE(%s:%s %s)'''  %( name,label, json_to_properties(prop))
            log.debug(insert_crystr)
            self.neo.cyrun(insert_crystr)

    def insert_relationship(self):
        log = glog(level=self.logLEVEL ,clazz=base_cyqoperator)
        if not self.neo:
            self.neo = neo4junit()
        if self.entry__relationship.relationship_name:
            cyqstr  = None
            if self.entry__relationship.label_to :
                cyqstr = '''MATCH (a:%s {_KEY:\"%s\"}),''' % (
                         self.entry__relationship.label_from['label'], self.entry__relationship.label_from['_KEY']) + \
                         ''' (b:%s {_KEY:\"%s\"}) ''' % (
                         self.entry__relationship.label_to['label'], self.entry__relationship.label_to['_KEY']) + \
                         ''' MERGE (a)-[r:%s  %s ]->(b) ''' % (
                             self.entry__relationship.relationship_name,
                             json_to_properties(self.entry__relationship.properties))
            else:
                pass

            if  cyqstr:
                log.debug(cyqstr)
                self.neo.cyrun(cyqstr)
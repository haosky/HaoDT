# -*- coding: utf-8 -*-

from haoneo4j.neo4jdb import gxneo4j
import json

__author__ = 'hao'


class neo4junit():

    def __init__(self,autocommit=False):
        self.conn=gxneo4j().get_conn()
        self.autocommit = autocommit

        self.tran = self.conn.begin(autocommit=autocommit)

    def get_client(self):
        return self.conn

    def cyquery(self,cypher_str):
        cursor = self.conn.run(cypher_str)
        for cur in cursor:
            yield cur

    def cyrun(self,cypher_str):
        if self.autocommit:
            self.tran = self.conn.begin(autocommit= self.autocommit)
        self.tran.run(cypher_str)

    def finish(self):
        self.tran.commit()
        self.tran.finish()


def json_to_properties(obj):
    obj_seriliza=[]
    for key in obj.keys():
        field = obj[key]
        obj_seriliza.append(json.dumps({key:field},ensure_ascii=False).replace("{\"%s\":" % key,"%s:" % key, 1)[:-1])
    return "{"+",".join(obj_seriliza)+"}"
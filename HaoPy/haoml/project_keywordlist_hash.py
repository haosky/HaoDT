# -*- coding: utf-8 -*-

import re
from simhash import Simhash, SimhashIndex
from haomongodb.mongodbmaster import gxmongo
import sys
import json
import jieba
reload(sys)
sys.setdefaultencoding('utf8')

class project_keywordset():
    def __init__(self):
        self.odbsdb = gxmongo()
        self.odbs =  self.odbsdb.get_odbs()
        self.dstore = self.odbsdb.get_dstore()
        self.unit = list()


    def art_get_phase(self) :
        COMPLETE_WORKITEM = self.dstore['PROJECTS']
        for com in COMPLETE_WORKITEM.find():
            self.unit.append(unicode(com['NAME'].strip()))

    def __search_project(self):
        COMPLETE_WORKITEM = self.odbs['L1_PROJECT']
        for com in COMPLETE_WORKITEM.find():
            try:
                self.dstore['UNITS'].insert({'NAME': com['ENT_NAME'], 'CODE': com['ENT_CODE']})
                self.dstore['PROJECTS'].insert({'NAME': com['PRJ_NAME'], 'CODE': com['PRJ_CODE']})
                self.dstore['USERS'].insert({'NAME': com['USER_NAME'], 'CODE': com['USER_CODE']})
                print('---')
            except Exception as e:
                print e.message

        COMPLETE_WORKITEM = self.odbs['L2_PROJECT']
        for com in COMPLETE_WORKITEM.find():
            try:
                self.dstore['UNITS'].insert({'NAME': com['ENT_NAME'], 'CODE': com['ENT_CODE']})
                self.dstore['PROJECTS'].insert({'NAME': com['PRJ_NAME'], 'CODE': com['PRJ_CODE']})
                self.dstore['USERS'].insert({'NAME': com['USER_NAME'], 'CODE': com['USER_CODE']})
                print('---')
            except Exception as e:
                print e.message


    def get_features(self,s):
        width = 1
        da = [s[i:i + width] for i in range(max(len(s) - width + 1, 1))]
        return da

    def calc_distince(self,input_phases,kdistince):
        input_dict = []
        for pharse in input_phases:
            input_dict.append([ '%s'%  pharse, Simhash(self.get_features(pharse)) ])
        self.index = SimhashIndex(input_dict, k=kdistince)


    def search(self,comp):
        s1 = Simhash(self.get_features(unicode(comp)))
        return self.index.get_near_dups(s1)

    def main(self,distince):
        self.art_get_phase()
        self.calc_distince(self.unit, distince)

# if __name__ == '__main__':
#     d = project_keywordset()
#     d.main(12)
#     print json.dumps(d.search(unicode('地震防御区经费')),ensure_ascii=False,indent=2)

# -*- coding: utf-8 -*-

import re
from simhash import Simhash, SimhashIndex
from haomongodb.mongodbmaster import gxmongo
import sys
import json
import jieba
reload(sys)
sys.setdefaultencoding('utf8')

class user_keywordset():
    def __init__(self):
        self.odbsdb = gxmongo()
        self.odbs =  self.odbsdb.get_odbs()
        self.dstore = self.odbsdb.get_dstore()
        self.unit = list()


    def art_get_phase(self) :
        COMPLETE_WORKITEM = self.dstore['USERS']
        for com in COMPLETE_WORKITEM.find():
            self.unit.append(unicode(com['NAME'].strip()))

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
#     d = user_keywordset()
#     d.main(13)
#     print json.dumps(d.search(unicode('陈建军')),ensure_ascii=False,indent=2)

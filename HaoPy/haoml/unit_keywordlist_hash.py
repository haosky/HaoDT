# -*- coding: utf-8 -*-

import re
from simhash import Simhash, SimhashIndex
from haomongodb.mongodbmaster import gxmongo
import sys
import json
import jieba
reload(sys)
sys.setdefaultencoding('utf8')

class unit_keywordset():
    def __init__(self):
        self.odbsdb = gxmongo()
        self.odbs =  self.odbsdb.get_odbs()
        self.dstore = self.odbsdb.get_dstore()
        self.unit = list()

    def __search_compnamy(self):
        COMPLETE_WORKITEM = self.odbs['COMPLETE_WORKITEM']
        for com in COMPLETE_WORKITEM.find():
            try:
                self.dstore['UNITS'].insert({'NAME':com['DEP_NAME'],'CODE':com['DEP_CODE']})
                self.dstore['USERS'].insert({'NAME': com['USER_NAME'], 'CODE': com['USER_CODE']})
                print('---')
            except Exception as e:
                print e.message

    def art_get_phase(self) :
        for com in self.art_get_yield():
            self.unit.append(com)

    def art_get_yield(self):
        COMPLETE_WORKITEM = self.dstore['UNITS']
        for com in COMPLETE_WORKITEM.find():
            yield com['NAME'].strip()

    def build_units_dictionary(self):
        for com in self.art_get_yield():
            line_unit =  u'%s nt 1' % com
            print line_unit

    # def get_features(self,s):
    #     width = 2
    #     s = unicode(s.lower().strip())
    #     # s = re.sub(re.compile(u'[^\w]+'), '', s)
    #     da = [s[i:i + width] for i in range(max(len(s) - width + 1, 1))]
    #     return da

    # def get_features(self,s):
    #     # width = 2
    #     s = unicode(s.lower().strip())
    #     # s = re.sub(re.compile(u'[^\w]+'), '', s)
    #     # al =  [s[i:i + width] for i in range(max(len(s) - width + 1, 1))]
    #     al = list(jieba.cut(s))
    #     # codes = [str(hash(a)) for a in al]
    #     return al

    def get_features(self,s):
        width = 2
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

if __name__ == '__main__':
# #     # unit_keywordset().__search_compnamy()
#     d = unit_keywordset()
#     d.main(17)
#     print json.dumps(d.search(unicode('广东监管')),ensure_ascii=False,indent=2)
    unit_keywordset().build_units_dictionary()

# -*- coding: utf-8 -*-
import os
import sys
from simhash import Simhash, SimhashIndex
from haounits.fSTools import get_dir_sons
import traceback
import re
import json
import jieba
reload(sys)
sys.setdefaultencoding('utf-8')

class file_phase_sim():
    def __init__(self):
        self.phases_sim_fea = []
        self.docdir = {}

    def get_features(self,content):
        al = list(jieba.cut(content))
        return al

    def phase_clear(self,phase):
        return re.sub(re.compile(u'''\s|,|、|，|\n|\r\n'''),'',unicode(phase))

    def get_arts(self,parentDir):
        for son_dir in get_dir_sons(parentDir):
            son_dir_path = u'%s%s%s' % (parentDir,os.sep,son_dir)
            for filename in get_dir_sons(son_dir_path):
                try:
                    file_path   = u'%s%s%s' % (son_dir_path,os.sep,filename)
                    fob = open(file_path,'rb')
                    phaseid = 0
                    line_str =fob.readline()
                    print(filename)
                    while line_str:
                        line = unicode(line_str)
                        doc_phases = re.split(re.compile(u'。|；|！|？|\?'),line)
                        # doc_phases=line.split('\。')
                        for doc_phase in doc_phases:
                            if(len(doc_phase)) <=5 :
                                continue
                            phaseid += 1
                            ids = '%s：%s'%(filename,phaseid)
                            self.docdir.update({ids:doc_phase})
                            doc_phase = self.phase_clear(doc_phase)
                            self.phases_sim_fea.append([ids, Simhash(self.get_features(doc_phase))])
                        line_str = fob.readline()
                except:
                    print traceback.format_exc()


    def build_index(self,kval):
        self.index = SimhashIndex(self.phases_sim_fea, k=kval)

    def search(self,pharse):
        s1 = Simhash(self.get_features(self.phase_clear(unicode(pharse))))
        ids = self.index.get_near_dups(s1)
        result = {}
        for i in ids:
            result.update({i:self.docdir[i]})
        return result


if __name__ == '__main__':
    fp = file_phase_sim()
    f = fp.get_arts('D:\\建议原文_标题')
    f = fp.get_arts('D:\\议案原文_标题')
    fp.build_index(12)
    df = open('map_grap','wb')
    for phase in fp.docdir:
        result = fp.search(phase)
        outline = [result,phase]
        v = json.dumps(outline,ensure_ascii=False)+'\n'
        print v
        df.write(v)

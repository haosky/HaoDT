# -*- coding: utf-8 -*-
from haothrift.applications.BaseServerController import BaseServerController
from haoml.gemsim_topic import gemsim_topic
import re
import json
from haohbase.data.sfoa_files2hbase import sfoa_files
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

__author__ = 'hao'


class Server(BaseServerController):

    def __init__(self,**kwargs):
        BaseServerController.__init__(self, **kwargs)
        self.sf = sfoa_files()
        self.sf.load_mongo_sf()
        docid = []
        for data in self.sf.datasets:
                docid.append([data['_id'], data['title']])
        self.gt = gemsim_topic()
        self.gt.docindex = docid
        self.gt.load_data()
        self.gt.load_w2v()

    def get_file_tree(self):
        return json.dumps(self.sf.load_tree(),ensure_ascii=False)

    def get_doc_by_id(self,_id=None):
        return json.dumps(self.sf.get_doc_by_id(_id),ensure_ascii=False)

    def get_keyword_weight(self,_id=None,count=30):
        cut_content = unicode(self.sf.get_doc_by_id(_id)['cut_content'])
        mark_set = u''',.?'!<>，。？《》！[]()（）【】;；:：、'''
        for mark in mark_set:
            cut_content = cut_content.replace(mark, ' ')
        p = re.compile(u'''[\s,a-z,A-Z,0-9]''', re.S)
        kws = p.split(cut_content)
        kw_count = {}
        try:
            kws.remove(u'')
        except:
            pass
        for kw in kws:
            if len(kw) >=2 :
                kw_count.update({kw: kws.count(kw)})
        sort_list = []
        for kw, count_z in kw_count.items():
            sort_list.append({count_z: kw})
        sort_list.sort(reverse=True)
        dz = sort_list[:count]
        return json.dumps(dz,ensure_ascii=False)

    def get_lda_topic(self,_id=None):
        simsets = self.gt.similarity_query(self.sf.get_doc_by_id(_id)['cut_content'])
        results = []
        for row in simsets:
            _id, value = row
            if value > 0:
                md = self.gt.docindex[_id]
                results.append({"_id":md[0],"title":md[1],"score":str(value)})
        return json.dumps(results,ensure_ascii=False)

    def get_word2vec_similarity(self,word=None):
        data = self.gt.word2vec_query(word)
        result = []
        for da in data:
            kw, value = da
            result.append({"word":kw,"score":value})
        return json.dumps(result, ensure_ascii=False)


if __name__ == '__main__':
    # print Server().get_lda_topic('2017-2020')
    # print Server().get_word2vec_similarity("广东")
    print Server().get_keyword_weight("2017-1757")
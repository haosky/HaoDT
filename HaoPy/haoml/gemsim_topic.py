# -*- coding: utf-8 -*-
from haounits.loggerDefTools import get_defTestLogger as getlog
from haocommon.quicktools.txtExtract import txtExtract,cread_stop_list
from haounits.cfgOptionTools import get_items_in_cfg, get_uri_relative_parent_package
from gensim import corpora, models, similarities
import sources as source
from gensim import corpora
from collections import defaultdict

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


__author__ = 'hao'

class gemsim_topic():
    NUM_TOPICS = 20
    def __init__(self):
        self.docindex = None

    def text_distribution(self,documents):
         stopwords = get_uri_relative_parent_package(source, 'stopwords.txt')
         stoplist  = cread_stop_list(stopwords)
         stoplist = set(stoplist)
         texts = [[unicode(word) for word in document.lower().split() if unicode(word) not in stoplist and len(unicode(word))> 2]
                       for document in documents]
         frequency = defaultdict(int)
         for text in texts:
             for token in text:
                 frequency[token] += 1
        
         texts = [[token for token in text if frequency[token] > 1]
                       for text in texts]

         return texts

    def save_dictionary(self,texts):
        dictionary = corpora.Dictionary(texts)
        sfoa_dict = get_uri_relative_parent_package(source, 'sfoa.dict')
        dictionary.save(sfoa_dict)
        corpus = [dictionary.doc2bow(text) for text in texts]
        # doc2bow
        sfoa_bv = get_uri_relative_parent_package(source, 'sfoa.bv')
        corpora.MmCorpus.serialize(sfoa_bv, corpus)
        model = models.LdaModel(corpus, id2word=dictionary, num_topics=gemsim_topic.NUM_TOPICS)
        index = similarities.MatrixSimilarity(model[corpus])
        sfoa_index = get_uri_relative_parent_package(source, 'sfoa.index')
        index.save(sfoa_index)

    def load_data(self):
        sfoa_dict = get_uri_relative_parent_package(source, 'sfoa.dict')
        sfoa_bv = get_uri_relative_parent_package(source, 'sfoa.bv')
        self.dictionary = corpora.Dictionary.load(sfoa_dict)
        self.corpus = corpora.MmCorpus(sfoa_bv)
        self.model = models.LdaModel(self.corpus, id2word=self.dictionary, num_topics=gemsim_topic.NUM_TOPICS)
        sfoa_index = get_uri_relative_parent_package(source, 'sfoa.index')
        self.index = similarities.MatrixSimilarity.load(sfoa_index)

    def get_topic(self):
        data = self.model.top_topics(self.corpus,5)
        result = []
        for d in data:
            for i in d:
                if isinstance(i,list):
                    words = []
                    for z in i:
                        words.append(z[1])
                else:
                    if len(words) > 0:
                        result.append({float(i): words})
        return result

    def save_word2vec(self,texts):
        model = models.Word2Vec(texts, size=100, window=5, min_count=5, workers=4)
        sfoa_w2v = get_uri_relative_parent_package(source, 'sfoa.w2v')
        model.save(sfoa_w2v)

    def similarity_query(self,doc):
        vec_bow = self.dictionary.doc2bow(unicode(doc.lower()).split())
        vec_lda = self.model[vec_bow]
        sims = self.index[vec_lda]
        sims = sorted(enumerate(sims), key=lambda item: -item[1])
        return sims

    def load_w2v(self):
        sfoa_w2v = get_uri_relative_parent_package(source, 'sfoa.w2v')
        self.w2v = models.Word2Vec.load(sfoa_w2v)

    def word2vec_query(self,word):
        return self.w2v.wv.most_similar(unicode(word))


if __name__ == '__main__':
    from haohbase.data.sfoa_files2hbase import sfoa_files
    import json
    sf = sfoa_files()
    mondata = sf.load_mongo_sf()
    documents = []
    docid = []
    for data in mondata:
        documents.append(unicode(data['cut_content']))
        docid.append([data['_id'],data['title']])
    gt = gemsim_topic()
    gt.docindex = docid

    #LDA
    # learn
    # texts = gt.text_distribution(documents)
    # gt.save_dictionary(texts)
    # predict
    gt.load_data()
    # result =  gt.similarity_query(sf.get_doc_by_id('2017-2020')['cut_content'])
    # i = 0
    # for row in result:
    #     _id,value = row
    #     if value > 0:
    #         md  = gt.docindex[_id]
    #         md.append(str(value))
    #         print json.dumps(md,ensure_ascii=False)+'\n'
    #         i+=1
    # print str(i)

    #
    import json
    print json.dumps(gt.get_topic(),ensure_ascii=False,indent=1)

    # #WORD2VEC
    # texts = gt.text_distribution(documents)
    # # gt.save_word2vec(texts)
    # gt.load_w2v()
    # data = gt.word2vec_query("广东")
    # for da in data:
    #     kw,value = da
    #     print kw

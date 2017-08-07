# -*- coding: utf-8 -*-

import numpy as np
from sklearn.cluster import KMeans
from haounits.cfgOptionTools import get_items_in_cfg, get_uri_relative_parent_package
import json
import traceback
import jieba
import sources as source
userdict = get_uri_relative_parent_package(source, 'userdict.txt')
keywrod_entry_relationship_p = get_uri_relative_parent_package(source, 'zhoa_keywrod_entry_relationship')
jieba.load_userdict(userdict)
import jieba.posseg as pseg
import jieba.analyse as ja
from haounits.bunchUtils import writebunchobj,readbunchobj
import sys
reload(sys)
sys.setdefaultencoding('utf8')

__author__ = 'hao'

class kw_entry_KMeans():

    def __init__(self):
        self.vocabulary = []
        self.idf = 0
        self.tf = 0
        self.tdm = 0
        self.pcates = {}
        self.labels = {}
        self.doclength = 0
        self.vocablen = 0
        self.testset = 0
        self.vclassVec = {}
        self.wordmap = {}

    def load_data_set(self,path):
        entry_list = []
        class_values = []
        return entry_list,class_values

    def train_set(self,trainset,classVec):
        self.cate_prob(classVec)
        self.doclength = len(trainset)
        # 构建词典
        tempset = set()
        [tempset.add(str(hash(word))) for doc in trainset for word in doc]
        self.vocabulary = list(tempset)
        self.vocablen = len(self.vocabulary)
        self.calc_tfidf(trainset)
        self.build_tdm()

    def calc_wordfreq(self,trainset):
        self.idf = np.zeros([1,self.vocablen])
        self.tf = np.zeros([self.doclength,self.vocablen])
        for index in xrange(self.doclength):
            for dw in trainset[index]:
                word = str(hash(dw))
                self.tf[index,self.vocabulary.index(word)] += 1
            for singleword in set(trainset[index]):
                self.idf[0,self.vocabulary.index(singleword)] +=1

    def calc_tfidf(self,trainset):
        self.idf =  np.zeros([1,self.vocablen])
        self.tf = np.zeros([self.doclength,self.vocablen])
        for index in xrange(self.doclength):
            for dw in trainset[index]:
                word = str(hash(dw))
                self.tf[index,self.vocabulary.index(word)] += 1

            # 优化句子长度偏差
            self.tf[index] = self.tf[index] / (float(len(trainset[index])))

            for dw in set(trainset[index]):
                singleword = str(hash(dw))
                self.idf[0,self.vocabulary.index(singleword)] += 1

        self.idf = np.log(float(self.doclength)/ self.idf)
        self.tf = np.multiply(self.tf,self.idf)

    # 按分类计算P(X|yi)
    def build_tdm(self):
        self.tdm = np.zeros([len(self.pcates), self.vocablen])
        sumlist = np.zeros([len(self.pcates),1])
        for indx in xrange(self.doclength):
            tm = self.vclassVec[self.labels[indx]]
            self.tdm[tm] += self.tf[indx]
            sumlist[tm] = np.sum(self.tdm[tm])
        self.tdm = self.tdm / sumlist
        self.kmeans = KMeans(n_clusters=5, random_state=0).fit(self.tdm)
        result = {}
        # print json.dumps(self.wordmap,ensure_ascii=False)
        for i,dki in enumerate(self.kmeans.labels_):
            try:
                ki = str(dki)
                data = result.get(ki,[])
                ld = self.labels[i]
                bp = self.wordmap.get(ld)
                if len(bp)>1:
                    data.append(bp)
                    result.update({ki:data})
            except:
                print traceback.format_exc()
        self.class_cluster = result

    # 按分类计算P(yi)
    def cate_prob(self,classVec):
        self.labels = classVec
        labeltemps = set(self.labels)
        for labeltemp in labeltemps:
            self.pcates[labeltemp] = float(self.labels.count(labeltemp) /float(len(self.labels)))

    def map2vocab(self,testdata):
        testset = np.zeros([1,self.vocablen])
        for dw in testdata:
            word =str(hash(dw))
            try:
                testset[0,self.vocabulary.index(word)] += 1
            except:
                print traceback.format_exc()
        return testset

    def  predict(self,testset):
        if np.shape(testset)[1] != self.vocablen:
            print "输入错误"
            exit(0)
        pv = self.kmeans.predict(testset)[0]
        return self.class_cluster.get(str(pv))

def load_neo4j_kw_entry():
    postingList = []
    classVec = []  # 1 is abusive, 0 not
    of = open(keywrod_entry_relationship_p, 'r')
    l = of.readline()
    i = 0
    map_doc = {}
    while l:
        try:
            l = l.replace('、','')
            lp = l.split('|')
            words = json.loads(lp[1])
            words.extend(list(jieba.cut(lp[0])))
            postingList.append(words)
            kz = hash(lp[0])
            map_doc.update({kz:lp[0]})
            classVec.append(kz)
        except:
            print traceback.format_exc()
        finally:
            l = of.readline()
    print 'load finish!!'
    sw = set(classVec)
    vclassVec = {}

    for i, w in enumerate(list(sw)):
        vclassVec.update({w: i})

    return postingList, classVec, vclassVec,map_doc


if __name__ == '__main__':
    # 0.00014842935319
    nb = kw_entry_KMeans()
    dataSet, listClasses,vclassVec,map_doc = load_neo4j_kw_entry()
    nb.vclassVec = vclassVec
    nb.wordmap = map_doc
    nb.train_set(dataSet, listClasses)
    writebunchobj('./data/zhoa_kw_entry_KMeans.bin',nb)
    # nb = readbunchobj('./data/kw_entry_KMeans.bin')
    testset = nb.map2vocab([u"设施设备", u"管理团队", u"生产基地", u"专业合作社"])
    # print json.dumps(dataSet[12],ensure_ascii=False)
    print json.dumps(nb.predict(testset),ensure_ascii=False)
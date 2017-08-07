# -*- coding: utf-8 -*-

import numpy as np
import json
import traceback
import jieba
# jieba.load_userdict("/root/work/HaoPy/haohbase/entry/userdict.txt")
jieba.load_userdict("D:\\\\workspace\\\\java_project\\\\Integration\\\\HaoPy\\\\haohbase\\\\entry\\\\userdict.txt")
import jieba.posseg as pseg
import jieba.analyse as ja
from haounits.bunchUtils import writebunchobj,readbunchobj
import sys
reload(sys)
sys.setdefaultencoding('utf8')

__author__ = 'hao'

class kw_entry_NBayes():

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
        self.tp = zip(self.tdm,self.pcates)

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

    # 按分类计算P(yi)
    def cate_prob(self,classVec):
        self.labels = classVec
        labeltemps = set(self.labels)
        for labeltemp in labeltemps:
            self.pcates[labeltemp] = float(self.labels.count(labeltemp) /float(len(self.labels)))

    def map2vocab(self,testdata):
        self.testset = np.zeros([1,self.vocablen])
        for dw in testdata:
            word =str(hash(dw))
            self.testset[0,self.vocabulary.index(word)] += 1

    def predict(self,testset):
        if np.shape(testset)[1] != self.vocablen:
            print "输入错误"
            exit(0)
        predvalue = 0
        predclass = ""
        for tdm_vect, keyclass in self.tp:
            temp = np.sum(testset*tdm_vect*self.pcates[keyclass])
            if temp > predvalue:
                predvalue = temp
                predclass = keyclass
        return self.wordmap.get(predclass)
    
def load_neo4j_kw_entry():
    postingList = []
    classVec = []  # 1 is abusive, 0 not
    of = open('D:\\workspace\\java_project\\Integration\\HaoPy\\haoml\\data\\keywrod_entry_relationship', 'r')
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

def loadDataSet():
    postingList=[]
    classVec = []    #1 is abusive, 0 not
    # of = open('/root/work/HaoPy/haohbase/entry/hrows2','r')
    of = open('D:\\\\workspace\\\\java_project\\\\Integration\\\\HaoPy\\\\haohbase\\\\entry\\\\hrows2', 'r')
    l = of.readline()
    i =0
    while l :
        try:
            data = json.loads(l.strip())
            fl_type = unicode(data['fl_type'])
            content = unicode(data['content'].strip())
            words = list(jieba.cut(content))
            postingList.append(list(set(words)))
            classVec.append(fl_type)
        except:
            print traceback.format_exc()
            print l.strip()
        finally:
            l = of.readline()
    print 'load finish!!'
    sw = set(classVec)
    vclassVec = {}
    for i,w in enumerate(list(sw)):
        kz = hash(w)
        vclassVec.update({kz:i})
    return postingList,classVec,vclassVec

if __name__ == '__main__':
    # nb = kw_entry_NBayes()
    # dataSet, listClasses,vclassVec,map_doc = load_neo4j_kw_entry()
    # nb.vclassVec = vclassVec
    # nb.wordmap = map_doc
    # nb.train_set(dataSet, listClasses)
    # writebunchobj('./data/kw_entry_NBayes.bin',nb)
    nb = readbunchobj('./data/kw_entry_NBayes.bin')
    nb.map2vocab([u"设施设备", u"管理团队", u"生产基地", u"专业合作社"])
    # print json.dumps(dataSet[12],ensure_ascii=False)
    print nb.predict(nb.testset)
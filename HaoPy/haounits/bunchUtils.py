# -*- coding: utf-8 -*-

import pickle
import sys
reload(sys)
sys.setdefaultencoding('utf8')

__author__ = 'hao'


# 读取bunch对象
def readbunchobj(path):
    file_obj = open(path, "r")
    bunch = pickle.load(file_obj)
    file_obj.close()
    return bunch


# 写入bunch对象
def writebunchobj(path, bunchobj):
    file_obj = open(path, "w")
    pickle.dump(bunchobj, file_obj)
    file_obj.close()
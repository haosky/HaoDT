# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

__author__ ='hao'

class SimpleBolt():

    def emit(self,obj):
        print obj
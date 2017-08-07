# -*- coding: utf-8 -*-

import traceback
from haounits.loggerDefTools import get_defTestLogger as getlog

__author__ = 'hao'


class queueBase():
     def __init__(self,queob):
         self.queob = queob
         self.log = getlog()

     def _pop(self,quename):
         try:
            return self.queob.pop(quename)
         except:
             self.log.error(traceback.format_exc().replace('\n' ,' '))

     def _push(self,quename,unit):
         try:
             self.queob.push(quename,unit)
             return True
         except:
             self.log.error(traceback.format_exc().replace('\n' ,' '))


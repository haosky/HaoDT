# -*- coding: utf-8 -*-

import sys
from haounits.loggerDefTools import get_defTestLogger as getlog
import json
reload(sys)
sys.setdefaultencoding('utf8')


class BaseServerController():
    def __init__(self,**kwargs):
        self.LOG = getlog()

    def main_exec(self,json_params):
        '''
        适配方法并执行
        :param json_params:  {'action':方法名,'params',{参数}}
        :return json格式的字符串:
        '''
        params = json_params.get('params',{})
        return getattr(self,json_params['action'])(**params)

class FunctionDistribute():
    def __init__(self):
        self.LOG = getlog()
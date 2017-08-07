# -*- coding: utf-8 -*-
from haothrift.applications.BaseServerController import BaseServerController
from haocommon.quicktools.txtExtract import txtExtract
import json
import traceback

__author__ = 'hao'


class Server(BaseServerController):

    def __init__(self, **kwargs):
        BaseServerController.__init__(self, **kwargs)
        self.ext = txtExtract()

    def image2txt(self,finename):
        try:
            return self.ext.extract_img2txt(finename)
        except:
            print traceback.format_exc()
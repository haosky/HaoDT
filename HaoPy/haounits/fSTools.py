# -*- coding: utf-8 -*-
import os
import json
import sys
import copy
reload(sys)
sys.setdefaultencoding('utf8')

def get_dir_sons(parentDir):
    for f in os.listdir(unicode(parentDir)):
        yield f
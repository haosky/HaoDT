# -*- coding: utf-8 -*-
from haounits.loggerDefTools import get_defTestLogger as getlog
from haounits.cfgOptionTools import get_items_in_cfg, get_uri_relative_parent_package
import xlrd
import sources as source
import traceback
import json
try:
    import Image
except ImportError:
    from PIL import Image
import pytesseract
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


import logging
__author__ = 'hao'

log = getlog(level=logging.DEBUG)

def cread_stop_list(stopwordspath):
    stwlist = [unicode(line.strip())
               for line in open(stopwordspath, 'r').readlines()]
    return stwlist

class txtExtract:

    def extract_img2txt(self,imagefle):
        image = Image.open(unicode(imagefle))
        image.load()
        _str = pytesseract.image_to_string(image,lang=['chi_sim'])
        image.close()
        return _str

    def extract_col_excel2record(self,excel):
        workbook = xlrd.open_workbook(unicode(excel))
        sheet_names = workbook.sheet_names()
        data = {}
        for sheet_name in sheet_names:
            sheet = workbook.sheet_by_name(sheet_name)
            data.update({sheet_name:[]})
            for rs in sheet.get_rows():
                try:
                    clo_value = []
                    for clo in rs:
                        clo_value.append(clo.value)
                    data[sheet_name].append(clo_value)
                except:
                    print traceback.format_exc()
                    break
        return data


if __name__ == '__main__':
   # print txtExtract().extract_img2txt(u'H:\\word_data\\发文\\关于协助做好土壤污染状况详查试点工作的函\\428_0.jpg')
   dim_excel = get_uri_relative_parent_package(source, '公文目录.xls')
   print json.dumps(txtExtract().extract_col_excel2record(dim_excel),ensure_ascii=False,indent=1)
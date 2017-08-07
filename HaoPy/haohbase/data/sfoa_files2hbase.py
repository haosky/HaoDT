# -*- coding: utf-8 -*-
from haounits.loggerDefTools import get_defTestLogger as getlog
from haounits.cfgOptionTools import get_items_in_cfg, get_uri_relative_parent_package
from haounits.fSTools import get_dir_sons
from haomongodb.mongodbmaster import gxmongo
from haocommon.quicktools.txtExtract import txtExtract,cread_stop_list
import sources as source
import traceback
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


import logging
__author__ = 'hao'

log = getlog(level=logging.DEBUG)

class sfoa_files():
    def __init__(self):
        self.datasets=None
        self.oaclient = gxmongo().get_zhoastore()

    def data_loads(self,srcdir):
        te  = txtExtract()
        for fu in get_dir_sons(srcdir):
            ishad = False
            f = srcdir+"\\"+fu
            filename = f.split('\\')[-1]
            txtfile = f+"\\"+filename+'.txt'
            content = unicode(open(txtfile,'r').read())
            data_sub = []
            for img_fileu in get_dir_sons(f):
                img_file= f + "\\" + img_fileu
                img_filename = f.split('\\')[-1]
                if img_fileu.endswith(u'.txt'):
                    continue
                offist =img_fileu.split(u'_')[0]
                try:
                    print img_file
                    data = te.extract_img2txt(img_file)
                    if data:
                        data_sub.append({int(offist):unicode(data)})
                        ishad = True
                except:
                    print traceback.format_exc()
            data_sub.sort()
            i = 0
            cont_split = []
            content_offest = 0
            for da in data_sub:
                of =  da.keys()[0]
                dap = da.values()[0]
                dlcontent = content[content_offest:of - 1]
                content_offest = of + i
                cont_split.append(dlcontent)
                cont_split.append(dap)
                i += 1
            if ishad:
                yield  filename,u"".join(cont_split)
            else:
                yield  filename,content

    def data_cron(self):
        te = txtExtract()
        dim_excel = get_uri_relative_parent_package(source, 'gwml.xls')
        data = te.extract_col_excel2record(dim_excel)
        for typename,info in data.items():
            for row in info:
                try:
                    if typename == "发文":
                        path = "H:\\word_data\\last_fa"
                    elif typename == "收文":
                        path = "H:\\word_data\\last_sou"
                    filepath = path+u"\\"+row[3]
                    row_content = open(filepath,"r").read()
                    if len(row_content.strip()) > 0:
                        row.append(row_content)
                        yield row
                except:
                    # print row[3]
                    print traceback.format_exc()

    def load_mongo_sf(self):
        self.datasets = []
        for data in self.oaclient['doc'].find():
            self.datasets.append(data)
        return self.datasets

    def load_tree(self):
        tree = {u"收文":{},u"发文":{}}
        for data in self.datasets:
            titleset = tree[data['type']].get(data['level'],[])
            titleset.append({"title":data['title'],"_id":data["_id"]})
            tree[data['type']].update({data['level']:titleset})
        return tree

    def get_doc_by_id(self,_id):
        return self.oaclient['doc'].find_one({"_id":_id})

    def count_keywords(self):
        kws= []
        for data in self.datasets:
           for kw in data['keywords']:
               kws.append(kw)
        kw_count = {}
        for kw in kws:
            kw_count.update({kw:kws.count(kw)})
        sort_list = []
        for kw,count in kw_count.items():
            sort_list.append({count:kw})
        sort_list.sort(reverse=True)
        return sort_list

# if __name__ == '__main__':
#     for filename,content in sfoa_files2hbase().data_loads(u"H:\\word_data\\发文"):
#         try:
#             rw = open(u"H:\\word_data\\last_fa\\"+filename,"w")
#             rw.write(str(content))
#             rw.close()
#         except:
#             print traceback.format_exc()

# if __name__ == '__main__':
#     for filename,content in sfoa_files2hbase().data_loads(u"H:\\word_data\\收文"):
#         try:
#             rw = open(u"H:\\word_data\\last_sou\\"+filename,"w")
#             rw.write(str(content))
#             rw.close()
#         except:
#             print traceback.format_exc()

if __name__ == '__main__2':
    import jieba
    import copy
    from jieba.analyse import extract_tags
    zhoadict = get_uri_relative_parent_package(source, 'zhoadict.txt')
    stopwords = get_uri_relative_parent_package(source, 'stopwords.txt')
    jieba.load_userdict(zhoadict)
    oaclient = gxmongo().get_zhoastore()
    for data in sfoa_files().data_cron():
         cut_content = " ".join(jieba.cut(data[8]))
         dc = copy.deepcopy(data[8])
         stops = cread_stop_list(stopwords)
         for d in stops:
             dc = dc.replace(d,"")
         keywordlist = list(set(extract_tags(dc,12)))
         oaclient['doc'].insert({'_id':data[0],'type':data[1],'level':data[2],'title':data[3],'docnum':data[4],'datestr':data[5],'uploader':data[6],'status':data[7],'content':data[8],'cut_content':cut_content,'keywords':keywordlist})

if __name__ == '__main__':
    import json
    sf = sfoa_files()
    sf.load_mongo_sf()
    # tree = sf.load_tree()
    # json.dumps(tree,ensure_ascii=False,indent=1)
    # print sf.get_doc_by_id('2017-1764')
    print json.dumps(sf.count_keywords(),ensure_ascii=False,indent=1)

# if __name__ == '__main__':
#     zhoadict = get_uri_relative_parent_package(source, 'zhoadict.txt')
#     d = open(zhoadict,'r')
#     mz=set()
#     import json
#     for m in d.read().split('\n'):
#       mz.add(m.strip())
#     print "\n".join(mz)
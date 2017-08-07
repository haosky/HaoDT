# -*- coding: utf-8 -*-

from haothrift.eshandler.ttypes import *
from haocommon.quicktools.esutils import ElasitcUtil
from haothrift.eshandler import data_complex_query as handler_desc
from haounits.loggerDefTools import get_defTestLogger as getlog
from haounits.cfgOptionTools import get_items_in_cfg, get_uri_relative_parent_package
import haothrift.eshandler.qdsl as parent
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.server import TServer
from thrift.protocol import TBinaryProtocol
import jieba.analyse
import logging
import json

__author__ = 'hao'

log = getlog(level=logging.DEBUG)


class searcher():
    INDEX_DATA_CENTER = 'gdfinanical'
    DOC_TYPE_TABLE = 'alldata'
    QUERY_COMPLEX = 'alldata__v1'

    GDFINANICAL = 'guangdongfinanical'
    PDS = 'Pdfs'

    PDS_t1 = 'Pdfs__v1'

    KW_RED_CSS_CLASS = 'red_text'
    def __init__(self):
        self.es = ElasitcUtil()
        self.__qdsl_file_path = get_uri_relative_parent_package(parent, 'search.qdsl')
        print self.__qdsl_file_path
        self.query_table_data_dsl = get_items_in_cfg(searcher.GDFINANICAL, searcher.PDS_t1, self.__qdsl_file_path)

    def search_art_keyword(self,article_src):
        listkw = jieba.analyse.extract_tags(article_src, 5)
        kws = []
        for i in listkw:
            kws.append(i)

        search_body_str = self.query_table_data_dsl % (','.join(kws))
        search_body = json.loads(search_body_str)

        response_hits = self.es.search(index=searcher.GDFINANICAL,doc_type=searcher.PDS,body=search_body)


        row = response_hits.get('hits',{}).get('hits',[])

        for cont in row:
            source = cont['_source']
            for i in listkw:
                source['content'] = source['content'].replace(i,'<span class="%s">%s</span>' % (searcher.KW_RED_CSS_CLASS,i) )
                source['title'] = source['title'].replace(i,'<span class="%s">%s</span>' % (searcher.KW_RED_CSS_CLASS,i))

        return json.dumps(row,ensure_ascii=False)

    def search_art_keyword_art(self, article_src):
        listkw = jieba.analyse.extract_tags(article_src, 5)
        kws = []
        for i in listkw:
            # , {"match": {"keywords_str": "财务"}}, {"match": {"keywords_str": "资金"}}
            kws.append('{"match": {"keywords_str": "%s"}} ' % i)

        search_body_str = self.query_table_data_dsl % (','.join(kws))
        print(search_body_str)
        search_body = json.loads(search_body_str)

        response_hits = self.es.search(index=searcher.INDEX_DATA_CENTER, doc_type=searcher.DOC_TYPE_TABLE, body=search_body)
        # return json.dumps(response_hits.get('hits', {}).get('hits', []), ensure_ascii=False,indent=2).replace('\\r\\n', '\r\n')

        clos_name_last = '__STR'
        clos_desc_last = '__COMMENTS'

        color_style = '<span class="'+searcher.KW_RED_CSS_CLASS+'">%s</span>'
        tables = []
        for rowdata in response_hits.get('hits', {}).get('hits', []) :
             source = rowdata['_source']
             trs = []
             for prex,vdata in source.items():
                    if  prex.endswith(clos_desc_last):
                        clos_data_key = prex.replace('__COMMENTS','')
                        dv = source[clos_data_key].strip()
                        for kw in listkw:
                            vdata = vdata.replace(kw,color_style % (kw))

                        if len(dv) ==0:
                            dv = '/'

                        td = '''<tr><td>%s</td><td>%s</td></tr>''' % (vdata,source[clos_data_key])
                        trs.append(td)

             tablestr = '''<table>%s</table>'''% ('\n'.join(trs))
             tables.append({'content':tablestr,'title':'','_id':rowdata['_id']})

        return json.dumps(tables,ensure_ascii=False,indent=1)

if __name__ == '__main__':
    print(".....starting....")
    handler = searcher()
    proc = handler_desc.Processor(handler)
    trans_ep = TSocket.TServerSocket(host="192.168.100.146",port=9992)
    # trans_ep = TSocket.TServerSocket(host="127.0.0.1", port=9992)
    trans_fac = TTransport.TBufferedTransportFactory()
    proto_fac = TBinaryProtocol.TBinaryProtocolFactory()
    server = TServer.TSimpleServer(proc, trans_ep, trans_fac, proto_fac)
    server.serve()

# if __name__ == '__main__':
#     searcher().search_art_keyword("财务管理资金")
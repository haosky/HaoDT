# -*- coding: utf-8 -*-

import logging
from haocommon.quicktools.esutils import ElasitcUtil
from haothrift.eshandler import data_complex_query as handler_desc
from haounits.loggerDefTools import get_defTestLogger as getlog
from haounits.cfgOptionTools import get_items_in_cfg, get_uri_relative_parent_package
import haothrift.eshandler.qdsl as parent
import jieba.analyse
import logging
import json

__author__ = 'hao'


log = getlog(level=logging.INFO)


class searcher():
    INDEX_DATA_CENTER = 'gdfinanical'
    DOC_TYPE_TABLE = 'alldata'
    QUERY_COMPLEX = 'alldata__v1'

    GDFINANICAL = 'guangdongfinanical'
    PDS = 'Pdfs'

    PDS_t1='Pdfs__v1'

    def __init__(self):
        self.es = ElasitcUtil()
        self.__qdsl_file_path = get_uri_relative_parent_package(parent, 'search.qdsl')
        print self.__qdsl_file_path
        # self.query_table_data_dsl = get_items_in_cfg(searcher.INDEX_DATA_CENTER, searcher.QUERY_COMPLEX, self.__qdsl_file_path)
        self.query_table_data_dsl = get_items_in_cfg(searcher.GDFINANICAL, searcher.QUERY_COMPLEX, self.__qdsl_file_path)

    def search_art_keyword(self, article_src):
        listkw = jieba.analyse.extract_tags(article_src, 5)
        kws = []
        for i in listkw:
            # , {"match": {"keywords_str": "财务"}}, {"match": {"keywords_str": "资金"}}
            kws.append('{"match": {"KEYWORDOBJ": "%s"}}' % i)

        search_body_str = self.query_table_data_dsl % (','.join(kws))
        search_body = json.loads(search_body_str)

        response_hits = self.es.search(index=searcher.INDEX_DATA_CENTER, doc_type=searcher.DOC_TYPE_TABLE, body=search_body)
        clos_name_last = '__STR'
        clos_desc_last = '__COMMENTS'

        color_style = '<span class="kw">%s</span>'
        tables = []
        for rowdata in response_hits.get('hits', {}).get('hits', []) :

             table_data = {}
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
                        table_data.update({ source[clos_data_key+clos_name_last]: {vdata:dv}})
                        td = '''<tr><td>%s</td><td>%s</td></tr>''' % (vdata,source[clos_data_key])
                        trs.append(td)
             tablestr = '''<table>%s</table>'''% ('\n'.join(trs))
             tables.append(tablestr)
        print(json.dumps(tables,ensure_ascii=False,indent=1 ))

if __name__ == '__main__':
    print searcher().search_art_keyword("财务")
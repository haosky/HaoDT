# -*- coding: utf-8 -*-
import os
import re
import traceback
import json
import sys
from haoml.keyword_extract import keyword_extract
from haocommon.quicktools.esutils import ElasitcUtil
from haounits.cfgOptionTools import get_items_in_cfg, get_uri_relative_parent_package
from haounits.loggerDefTools import get_defTestLogger
from haoneo4j.neo4junit import neo4junit
import haostorm.check_repeat.qdsl as parent
import logging
reload(sys)
sys.setdefaultencoding('utf8')

__author__ = 'hao'
log = get_defTestLogger(logging.INFO,clazz='art_relative')
class art_relative():

    QSDL_TYPE = 'caizheng'
    caizheng_t1 = 'MoNi__v2'
    caizheng_row_t1 = 'MoNi__v2_row'

    def __init__(self):
        self.ke = keyword_extract()
        self.ke.openHanlp()
        self.es = ElasitcUtil()
        self.__qdsl_file_path = get_uri_relative_parent_package(parent, 'search.qdsl')
        self.query_table_data_dsl = get_items_in_cfg(art_relative.QSDL_TYPE, art_relative.caizheng_t1,
                                                     self.__qdsl_file_path)

        self.query_table_data_dsl_row = get_items_in_cfg(art_relative.QSDL_TYPE, art_relative.caizheng_row_t1,
                                                         self.__qdsl_file_path)

        self.INDEX_DATA_CENTER = get_items_in_cfg('index_type', 'CZ_INDEX_DATA_CENTER',
                                                  self.__qdsl_file_path)
        self.DOC_TYPE_TABLE = get_items_in_cfg('index_type', 'CZ_DOC_TYPE_TABLE',
                                               self.__qdsl_file_path)

    def extract_entry(self,content):
        dz = self.ke.hanlp_cut(content)
        m = str(dz)
        das = m[1:-1].split(', ')
        entry = set()
        for d in das:
            wsplit = d.split('/')
            wtype = wsplit[1]
            if wtype == 'nr' or wtype == 'nt' or wtype == 'nt':
                entry.add(d)
        return list(entry)

    def scan_es(self):
        res = self.es.scan_source(index=self.INDEX_DATA_CENTER ,doc_type=self.DOC_TYPE_TABLE,query={})
        cnum = self.es.count(index=self.INDEX_DATA_CENTER, doc_type=self.DOC_TYPE_TABLE, body={})['count']
        i = 0
        wr = open('relative_f','w')
        for row in res:
            try:
                d = row['_source']
                i += 1
                print '%s / %s' % (i,cnum)
                list_entry = self.extract_entry(d['content'])
                if len(list_entry) > 0:
                    data = {'_uuid':d['_uuid'],'project':d['project'],'kws':list_entry}
                    # data = {'uuid':d['uuid'],'project':d['project'],'entry':wsplit[0],'entry_type':wsplit[1]}
                    wr.write(json.dumps(data,ensure_ascii=False)+'\n')
            except:
                print traceback.format_exc()
        wr.close()
    
    def scan_to_neo4j(self):
        '''通过扫描es插入数据到neo4j'''
        res = self.es.scan_source(index=self.INDEX_DATA_CENTER, doc_type=self.DOC_TYPE_TABLE, query={})
        cnum = self.es.count(index=self.INDEX_DATA_CENTER, doc_type=self.DOC_TYPE_TABLE, body={})['count']
        i = 0
        for row in res:
            try:
                neo = neo4junit(autocommit=False)
                neo.tran = neo.conn.begin(autocommit= False)
                con = row['_source']
                i += 1
                print '%s / %s' % (i, cnum)
                PleceEntry = list(set(json.loads(con["PleceEntry"])))
                [self.put_entry(neo,entry,'PleceEntry') for entry in PleceEntry]
                KwEntry = list(set(json.loads(con["KwEntry"])))
                [self.put_entry(neo, entry, 'KwEntry') for entry in KwEntry]
                OrgEntry = list(set(json.loads(con["OrgEntry"])))
                [self.put_entry(neo, entry, 'OrgEntry') for entry in OrgEntry]
                ChineseEntry = list(set(json.loads(con["ChineseEntry"])))
                [self.put_entry(neo, entry, 'ChineseEntry') for entry in ChineseEntry]
                YyEntry = list(set(json.loads(con["YyEntry"])))
                [self.put_entry(neo, entry, 'YyEntry') for entry in YyEntry]
                self.put_project(neo,con["project"],row["_id"])
                neo.tran.commit()
                neo.finish()
            except:
                print traceback.format_exc()

    def put_constant(self,neo):
        start_create_proj = '''CREATE CONSTRAINT ON (p:SpecialFinancialProject_v1)
                        ASSERT p.uuid IS UNIQUE'''
        neo.cyrun(start_create_proj)

        start_create_ent = '''CREATE CONSTRAINT ON (p:SpecialFinancialEntry_v1)
                                ASSERT p.entry IS UNIQUE'''
        neo.cyrun(start_create_ent)

    def put_entry(self,neo,name,typename):
        try:
            cypher_str_ent = '''MERGE (a:SpecialFinancialEntry_v1 {entry: '%s',type:'%s'}) ON CREATE SET a.entry = '%s'
                                ''' % (name, typename, name)
            # print cypher_str_ent
            neo.cyrun(cypher_str_ent)
        except:
            print traceback.format_exc()

    def put_project(self,neo,name,_uuid):
        try:
            cypher_str_proj = '''MERGE (a:SpecialFinancialProject_v1 {project: '%s',uuid:'%s'}) ON CREATE SET a.project = '%s'
                                                    ''' % (name, _uuid, name)
            neo.cyrun(cypher_str_proj)
        except:
            print traceback.format_exc()


    def relative_to_neo4j(self):
        neo = neo4junit(autocommit=False)
        # start_create_proj = '''CREATE CONSTRAINT ON (p:SpecialFinancialProject)
        #                 ASSERT p.project IS UNIQUE'''
        # neo.cyrun(start_create_proj)
        #
        # start_create_ent = '''CREATE CONSTRAINT ON (p:SpecialFinancialEntry)
        #                         ASSERT p.entry IS UNIQUE'''
        # neo.cyrun(start_create_ent)
        vset = open('relative_f','r')
        v = vset.readline()
        dwset = []
        f = False
        i = 0
        beg = neo.conn.begin(autocommit=False)
        while v:
            try:
                data = json.loads(v.strip())
                project = data['project']
                uuid = data['_uuid']
                i+=1
                if uuid == '567d6cc20b3ebe2c8cf3cd1036a9f60b':
                    f = True
                print str(i)

                if not f :
                    v = vset.readline()
                    continue

                if i % 1000 == 0 :
                    print 'commit'
                    beg.commit()
                    beg = neo.conn.begin(autocommit=False)

                cypher_str_proj = '''MERGE (a:SpecialFinancialProject {project: '%s',uuid:'%s'}) ON CREATE SET a.project = '%s'
                                        ''' % (project, uuid,project)
                try:
                    neo.cyrun(cypher_str_proj)
                except:
                    # print  traceback.format_exc()
                    pass
                for kw in data['kws']:
                    kwsplit = kw.split('/')
                    entry = kwsplit[0]
                    entry_type = kwsplit[1]
                    if entry in dwset:
                        continue
                    cypher_str_ent = '''MERGE (a:SpecialFinancialEntry {entry: '%s',type:'%s'}) ON CREATE SET a.entry = '%s'
                    ''' % (entry,entry_type,entry)
                    try:
                        neo.cyrun(cypher_str_ent)
                        dwset.append(dwset)
                    except:
                        # print  traceback.format_exc()
                        pass
                    cypher_str_reav = '''MATCH (a:SpecialFinancialEntry {entry: '%s'})
                    MATCH (b:SpecialFinancialProject {project: '%s'})
                    MERGE (a)-[r:InProject] -> (b)
                    ON CREATE SET  r.project = '%s'
                    ON MATCH SET  r.project = '%s'
                    ''' % (entry,project,project,project)
                    try:
                        # print cypher_str_reav
                        neo.cyrun(cypher_str_reav)
                    except:
                        pass
                        # print traceback.format_exc()
                body = self.es.get(index=self.INDEX_DATA_CENTER ,doc_type=self.DOC_TYPE_TABLE,id=uuid)['_source']
                body.update({'isre':True})
                self.es.index(index=self.INDEX_DATA_CENTER ,doc_type=self.DOC_TYPE_TABLE,id=uuid,body=body)
                print uuid
            except:
                print traceback.format_exc()
            v = vset.readline()
        beg.commit()
        beg.finish()

    def __del__(self):
        try:
            self.ke.closeHanlP()
        except:
            print traceback.format_exc()

if __name__ == '__main__':
    # art_relative().scan_es()
    # art_relative().relative_to_neo4j()
    # art_relative().neo_uuid_es()

    #5672e215d19a0f17692a6c921ed4c9c2
    # art_relative().put_constant()
    art_relative().scan_to_neo4j()
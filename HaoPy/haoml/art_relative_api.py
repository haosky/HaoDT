# -*- coding: utf-8 -*-
import os
import re
import traceback
import json
import sys
from haoneo4j.neo4junit import neo4junit
import haostorm.check_repeat.qdsl as parent
reload(sys)
sys.setdefaultencoding('utf8')

__author__ = 'hao'

class art_relative_api():
    # RELATIONSHISP = 'InProject_v1'
    # 智慧OA
    RELATIONSHISP = 'InzhoaProject_v1'

    def __init__(self):
        self.neo = neo4junit()

    def query_project_relative(self,suuid,num=100):
        try:
            result = []
            cypher_str = '''MATCH (p)-[r:%s]->(d {uuid:'%s'})
                        WITH p
                        MATCH d=(p)-[r:%s]->(f) where f.project <> ''
                        return f.project  order by f.project limit %s''' % (art_relative_api.RELATIONSHISP,suuid,art_relative_api.RELATIONSHISP,num)
            da = self.neo.cyquery(cypher_str)
            for s in da:
                result.append(s[0])
            return list(set(result))
        except:
            print traceback.format_exc()
            return None

    def return_for_data(self,data):
        result_nodes = {'nodes': [], 'links': []}
        reu = []
        ln = []
        for s in data:
                d = s
                m = d[0]
                if d[0]['entry'] == "" or d[1]['project'] == "" :
                    continue

                dtype = {'KwEntry':1,'OrgEntry':2,'PleceEntry':3,'YyEntry':4,'ChineseEntry':5} # 0 == project
                itype = d[0]['type']
                caretory = dtype.get(itype,0)

                v = {'category': caretory, 'name': d[0]['entry']}
                v2 = {'category': 0, 'name': d[1]['project']}

                if d[0]['entry'] not in reu:
                    result_nodes['nodes'].append(v)
                    reu.append(d[0]['entry'])

                if d[1]['project'] not in reu:
                    result_nodes['nodes'].append(v2)
                    reu.append(d[1]['project'])

                l = {
                    'source': d[0]['entry'],
                    'target': d[1]['project']
                }

                ll = '%s|%s' % (l['source'], l['target'])
                if ll not in ln:
                    result_nodes['links'].append(l)
                    ln.append(ll)
        data = json.dumps(result_nodes,ensure_ascii=False) #.replace("\"category\"","category").replace("\"name\"","name").replace("\"source\"","source").replace("\"target\"","target")
        print data
        return data

    def query_relative(self,_uuid,num=100):
        try:
            cypher_str = '''MATCH (p)-[r:%s]->(d {uuid:'%s'})
                        WITH p
                        MATCH d=(p)-[r:%s]->(f) where f.project <> ''
                        return p,r,f  order by p.entry limit %s''' % (art_relative_api.RELATIONSHISP,_uuid,art_relative_api.RELATIONSHISP,num)

            da = self.neo.cyquery(cypher_str)
            return self.return_for_data(da)
        except:
            print traceback.format_exc()
        return None

    def query_relative_entrices(self,_uuid,entrices,num=100):
        try:
            cypher_str = '''MATCH (p)-[r:%s]->(d {uuid:'%s'})
                         WITH p
                         MATCH d=(p)-[r:%s]->(f) where p.entry in %s and f.project <> ''
                         return p,r,f  order by p.entry limit %s''' % (art_relative_api.RELATIONSHISP,_uuid,art_relative_api.RELATIONSHISP,entrices,num)

            da = self.neo.cyquery(cypher_str)
            return self.return_for_data(da)
        except:
            print traceback.format_exc()
        return None

    def query_projectuuid2entry(self,entry,num=100):
        try:
            cypher_str = '''MATCH (p {entry:'%s'})-[r:%s]->(f) where f.project <> ''
                        return f.uuid order by f.uuid limit %s''' % (entry,art_relative_api.RELATIONSHISP,num)
            result = set()
            da = self.neo.cyquery(cypher_str)
            for s in da:
                result.add(s.get(0))
            return list(result)
        except:
            print traceback.format_exc()
        return []

    def query_project2entry_relative(self,entry,num=100):
        try:
            cypher_str = '''MATCH (p {entry:'%s'})-[r:%s]->(f ) where f.project <> ''
                        return p,r,f  order by p.entry limit %s''' % (entry,art_relative_api.RELATIONSHISP,num )
            da = self.neo.cyquery(cypher_str)
            return self.return_for_data(da)
        except:
            print traceback.format_exc()
        return None

    def query_project2entryset_relative(self,entrys,num=100):
        try:
            cypher_str = '''MATCH (p)-[r:%s]->(f ) where p.entry in %s and f.project <> ''
                        return p,r,f  order by p.entry limit %s ''' % (art_relative_api.RELATIONSHISP,entrys,num )
            da = self.neo.cyquery(cypher_str)
            return self.return_for_data(da)
        except:
            print traceback.format_exc()
        return None

    def query_entry2project_relative(self,_uuid,num):
        try:
            cypher_str = '''MATCH (p )-[r:%s]->(f {project:'%s'})
                        return p,r,f  order by p.entry limit %s''' % (art_relative_api.RELATIONSHISP,_uuid,num)
            da = self.neo.cyquery(cypher_str)
            return self.return_for_data(da)
        except:
            print traceback.format_exc()
        return None

if __name__ == '__main__':
#     # art_relative().scan_es()
#    print  art_relative_api().query_project2entryset_relative('[\'股分有限公司\',\'文向法院\']',100)
    pa = {"params":{"project":"","content":""},"model":"applications.multisearch.MainServer","action":"get_art_same"}
    print json.dumps(pa,ensure_ascii=False).replace("\"","\\\"")
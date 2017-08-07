# -*- coding: utf-8 -*-
import sys
from haoneo4j.neo4junit import neo4junit
import json
from haounits.loggerDefTools import get_defTestLogger
import logging
reload(sys)
sys.setdefaultencoding('utf8')

log = get_defTestLogger(level=logging.DEBUG)
class neo4j_entry():
    INPROJECT_RELATIONSHIP = '''MATCH p=(a:SpecialFinancialEntry)-[r:InProject]-> (b:SpecialFinancialProject) RETURN a,b.project,p'''
    def __init__(self):
        self.neo = neo4junit(autocommit=True)

    def query_keywrod_entry_relationship(self):
        entry_file = open('./data/keywrod_entry_relationship','wb')
        data_set = {}
        for sitem in self.neo.cyquery(neo4j_entry.INPROJECT_RELATIONSHIP):
            entry_data = sitem[0][u'entry']
            project_name = str(sitem[1])
            entry_set = data_set.get(project_name, [])
            entry_set.append(entry_data)
            data_set.update({project_name:entry_set })
        for project,entry in data_set.items():
            entry_file.write(u'''%s|%s\n''' % (project,json.dumps(entry,ensure_ascii=False)))
        entry_file.close()


if __name__ == '__main__':
    neo4j_entry().query_keywrod_entry_relationship()
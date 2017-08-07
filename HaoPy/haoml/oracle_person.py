# -*- coding: utf-8 -*-
import os
import re
import traceback
import json
import sys
from haoneo4j.neo4junit import neo4junit
import haostorm.check_repeat.qdsl as parent
# from haocommon.quicktools.oracleutils import oracleutils
import xlrd
from haounits.cfgOptionTools import get_items_in_cfg, get_uri_relative_parent_package
import sources as source
reload(sys)
sys.setdefaultencoding('utf8')

__author__ = 'hao'

class oracle_person():
    #
    # def query_data(self):
    #     o = oracleutils()
    #     children  = get_uri_relative_parent_package(source, 'children.txt')
    #     cf = open(children,'w')
    #     for r in o.execute("select GUID,CHILDREN_NAME,IDENTITY_NUMBER,Biological_Father_Guid,Biological_MOTHER_Guid from POP_CHILDREN"):
    #         try:
    #             rm = r[2] if  r[2] is not None else u""
    #             try:
    #                 rm = unicode(rm)
    #             except:
    #                 rm=u""
    #
    #             cf.write(json.dumps([unicode(r[0]),
    #                                  unicode(r[1]),
    #                                  rm,
    #                                  unicode(r[3]),
    #                                  unicode(r[4])],
    #                                 ensure_ascii=False)+u'\n')
    #         except:
    #             print r[0]
    #             print traceback.format_exc()
    #     cf.close()

    # def extract_children(self, excel):
    #     workbook = xlrd.open_workbook(unicode(excel))
    #     sheet_names = workbook.sheet_names()
    #     neo = neo4junit()
    #     for sheet_name in sheet_names:
    #         sheet = workbook.sheet_by_name(sheet_name)
    #         for rs in sheet.get_rows():
    #             try:
    #                 neo.tran = neo.conn.begin(autocommit=False)
    #                 cypher_str_ent = '''CREATE (a:WJWPERSON {CHILDREN_NAME :'%s',GUID :'%s',IDENTITY_NUMBER :'%s'})
    #                                                              ''' % (
    #                 rs[1].value, rs[0].value, rs[2].value)
    #                 neo.cyrun(cypher_str_ent)
    #                 neo.tran.commit()
    #                 print rs[1].value
    #             except:
    #                 print traceback.format_exc()
    #     neo.tran.finish()


    def extract_person(self, excel):
        workbook = xlrd.open_workbook(unicode(excel))
        sheet_names = workbook.sheet_names()
        neo = neo4junit()
        for sheet_name in sheet_names:
            sheet = workbook.sheet_by_name(sheet_name)
            for rs in sheet.get_rows():
                try:
                    neo.tran = neo.conn.begin(autocommit=True)
                    cypher_str_ent = '''CREATE (a:WJWPERSON {CHILDREN_NAME :'%s',GUID :'%s',IDENTITY_NUMBER :'%s'})
                                                        ''' % (
                    rs[2].value, rs[0].value, rs[1].value)
                    neo.cyrun(cypher_str_ent)
                    # neo.tran.commit()
                    print rs[1].value
                except:
                    print traceback.format_exc()
        neo.tran.finish()

    def person_relationship(self,excel):
        # children
        workbook = xlrd.open_workbook(unicode(excel))
        sheet_names = workbook.sheet_names()
        neo = neo4junit()
        for sheet_name in sheet_names:
            sheet = workbook.sheet_by_name(sheet_name)
            for rs in sheet.get_rows():
                try:
                    neo.tran = neo.conn.begin(autocommit=True)
                    cypher_str_reav = '''MATCH (a:WJWPERSON {GUID: '%s'})
                                     MATCH (b:WJWPERSON {GUID: '%s'})
                                     MERGE (a)-[r:FatherOf] -> (b)
                                        ''' % (rs[3].value, rs[0].value)
                    neo.cyrun(cypher_str_reav)
                    print rs[0].value
                except:
                    print traceback.format_exc()

                try:
                    neo.tran = neo.conn.begin(autocommit=True)
                    cypher_str_reav = '''MATCH (a:WJWPERSON {GUID: '%s'})
                                     MATCH (b:WJWPERSON {GUID: '%s'})
                                     MERGE (a)-[r:MotherOf] -> (b)
                                        ''' % (rs[4].value, rs[0].value)
                    neo.cyrun(cypher_str_reav)
                    print rs[0].value
                except:
                    print traceback.format_exc()
        neo.tran.finish()

    def create_qy(self,excel):
            # 企业
        workbook = xlrd.open_workbook(unicode(excel))
        sheet_names = workbook.sheet_names()
        neo = neo4junit()
        for sheet_name in sheet_names:
            sheet = workbook.sheet_by_name(sheet_name)
            for rs in sheet.get_rows():
                try:
                    neo.tran = neo.conn.begin(autocommit=True)
                    cypher_str_ent = '''CREATE (a:QY {NAME :'%s',UNIT_CODE :'%s',TRUE_CODE :'%s'})
                                                                            ''' % (
                     rs[2].value, rs[1].value, rs[0].value)
                    neo.cyrun(cypher_str_ent)
                    # neo.tran.commit()
                    print rs[1].value
                except:
                    print traceback.format_exc()
        print 'finish'
        neo.tran.finish()

    def create_proj(self,excel):
        # 项目
        workbook = xlrd.open_workbook(unicode(excel))
        sheet_names = workbook.sheet_names()
        neo = neo4junit()
        for sheet_name in sheet_names:
            sheet = workbook.sheet_by_name(sheet_name)
            for rs in sheet.get_rows():
                try:
                    neo.tran = neo.conn.begin(autocommit=True)
                    cypher_str_ent = '''CREATE (a:PROJ {pro_name :'%s',pro_seq :'%s'})
                                                                            ''' % (
                     rs[1].value, rs[0].value)
                    neo.cyrun(cypher_str_ent)
                    # neo.tran.commit()
                    print rs[1].value
                except:
                    print traceback.format_exc()
        print 'finish'
        neo.tran.finish()

    def gudon_relationship(self,excel):
        # 股东 for 企业
        workbook = xlrd.open_workbook(unicode(excel))
        sheet_names = workbook.sheet_names()
        neo = neo4junit()
        for sheet_name in sheet_names:
            sheet = workbook.sheet_by_name(sheet_name)
            for rs in sheet.get_rows():
                try:
                    neo.tran = neo.conn.begin(autocommit=True)
                    cypher_str_reav = '''MATCH (a:WJWPERSON {IDENTITY_NUMBER: '%s'})
                                     MATCH (b:QY {TRUE_CODE: '%s'})
                                     MERGE (a)-[r:GuDonOf] -> (b)
                                        ''' % (rs[0].value, rs[1].value)
                    neo.cyrun(cypher_str_reav)
                    # neo.tran.commit()
                    print rs[1].value
                except:
                    print traceback.format_exc()
        print 'finish'
        neo.tran.finish()

    def create_proj_for_qy_reloationship(self,excel):
        # 企业for项目
        workbook = xlrd.open_workbook(unicode(excel))
        sheet_names = workbook.sheet_names()
        neo = neo4junit()
        for sheet_name in sheet_names:
            sheet = workbook.sheet_by_name(sheet_name)
            for rs in sheet.get_rows():
                try:
                    neo.tran = neo.conn.begin(autocommit=True)
                    cypher_str_reav = '''MATCH (a:PROJ {pro_seq: '%s'})
                                                         MATCH (b:QY {UNIT_CODE: '%s'})
                                                         MERGE (a)-[r:QYOfPorj] -> (b)
                                                            ''' % (rs[1].value, rs[0].value)
                    neo.cyrun(cypher_str_reav)
                    # neo.tran.commit()
                    print rs[1].value
                except:
                    print traceback.format_exc()
        print 'finish'
        neo.tran.finish()

    def create_faren_for_qy_reloationship(self,excel):
        # 法人 of 企业
        workbook = xlrd.open_workbook(unicode(excel))
        sheet_names = workbook.sheet_names()
        neo = neo4junit()
        for sheet_name in sheet_names:
            sheet = workbook.sheet_by_name(sheet_name)
            for rs in sheet.get_rows():
                try:
                    neo.tran = neo.conn.begin(autocommit=False)
                    cypher_str_reav = '''MATCH (a:WJWPERSON {IDENTITY_NUMBER: '%s'})
                                                         MATCH (b:QY {TRUE_CODE: '%s'})
                                                         MERGE (a) -[r:FRForQY] -> (b)
                                                            ''' % (rs[1].value, rs[0].value)
                    neo.cyrun(cypher_str_reav)
                    neo.tran.commit()
                    print rs[1].value
                except:
                    print traceback.format_exc()
        print 'finish'
        neo.tran.finish()

if __name__ == '__main__':
    # GUID,CHILDREN_NAME,IDENTITY_NUMBER,Biological_Father_Guid,Biological_MOTHER_Guid  WJWPERSON
    # 插入完成
    # try:
    #     dim_excel = get_uri_relative_parent_package(source, 'person.xlsx')
    #     oracle_person().extract_person(dim_excel)
    # except:
    #     print traceback.format_exc()

    try:
        dim_excel = get_uri_relative_parent_package(source, 'children.xlsx')
        oracle_person().person_relationship(dim_excel)
    except:
        print traceback.format_exc()
    #
    # try:
    #     dim_excel = get_uri_relative_parent_package(source, 'qiye.xlsx')
    #     oracle_person().create_qy(dim_excel)
    # except:
    #     print traceback.format_exc()
    #
    # try:
    #     dim_excel = get_uri_relative_parent_package(source, 'project.xlsx')
    #     oracle_person().create_proj(dim_excel)
    # except:
    #     print traceback.format_exc()
    #
    # try:
    #     dim_excel = get_uri_relative_parent_package(source, 'qiye_for_proj.xlsx')
    #     oracle_person().create_proj_for_qy_reloationship(dim_excel)
    # except:
    #     print traceback.format_exc()
    #
    # try:
    #     dim_excel = get_uri_relative_parent_package(source, 'gdon.xlsx')
    #     oracle_person().gudon_relationship(dim_excel)
    # except:
    #     print traceback.format_exc()

    # try:
    #     dim_excel = get_uri_relative_parent_package(source, 'faren_for_qy.xlsx')
    #     oracle_person().create_faren_for_qy_reloationship(dim_excel)
    # except:
    #     print traceback.format_exc()

'''
CREATE CONSTRAINT ON (p:QY) ASSERT p.TRUE_CODE IS UNIQUE
CREATE CONSTRAINT ON (p:PROJ) ASSERT p.pro_seq IS UNIQUE
'''

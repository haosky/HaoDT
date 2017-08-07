# -*- coding: utf-8 -*-

from haohbase.hbase_dao import hbase_dao
from haocommon.quicktools.esutils import ElasitcUtil
from haounits.cfgOptionTools import get_items_in_cfg, get_uri_relative_parent_package
from haothrift.simhandler import sim_develop
from haoml.articlesimhash import get_content_simvalue, main_calc ,get_sim_distance,get_different_info,get_different_parse,get_different_comment,get_different_2_doc,calc_distince,art_get_phase,mark_same_content
from haohbase.simart.get_for_scan import sim_sets
from haounits.loggerDefTools import get_defTestLogger as getlog
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.server import TServer
from thrift.protocol import TBinaryProtocol
import logging
import copy
import haothrift.eshandler.qdsl as parent
import json
import traceback
import jieba

__author__ = 'hao'

log = getlog(level=logging.DEBUG)


class developer():
    INDEX_DATA_CENTER = 'monidatas'
    DOC_TYPE_TABLE = 'raw'

    QSDL_TYPE = 'caizheng'
    caizheng_t1 = 'MoNi__v1'

    def __init__(self):
        self.es = ElasitcUtil()
        self.sim_len = 8
        self.hm_distinct = 10

        self.__qdsl_file_path = get_uri_relative_parent_package(parent, 'search.qdsl')
        self.query_table_data_dsl = get_items_in_cfg(developer.QSDL_TYPE, developer.caizheng_t1, self.__qdsl_file_path)
        self.caizheng_table = 'CaiZhengMoNiSim'
        self.hscan = sim_sets()

    def get_art_sim(self, art_content):
        return str(get_content_simvalue(art_content))

    def get_difference2arts(self,art_src,art_dst):
        return main_calc(art_src, art_dst, 10)

    def get_differencelist(self):
        return sim_sets().scan_data()

    def get_differencelist_for_art(self,content):
        sim_value = str(get_content_simvalue(content))
        groups = sim_sets().scan_data_rowprex(sim_value[0:self.sim_len],self.caizheng_table)
        # print json.dumps(groups, ensure_ascii=False ,indent=1)
        # print json.dumps(groups,ensure_ascii=False,indent=1)

        differencelist = []
        sim_dist_keys = set()
        for group in groups:
            fname, docprop = group.items()[0] # simvalue,filename,content
            simvalue = docprop[0]
            #print json.dumps(main_calc(content,docprop[1],self.hm_distinct),ensure_ascii=False,indent=1)
            sim_content_info = main_calc(docprop[2],content,self.hm_distinct)
            calc_weghit_groups = {}
            for output_phase_id,input_phase_idset in sim_content_info['similar'].items():

                for iid in input_phase_idset:
                    sim_distinct = get_sim_distance(sim_content_info["index"][int(iid)],
                                                    sim_content_info["search"][int(output_phase_id)] )

                    # 输入内容断落id :匹配内容断落id -- 距离
                    calc_weghit_groups.update({"%s:%s" % (iid, output_phase_id): 1 - sim_distinct * 0.04})

                sim_content_info.update({'weight':calc_weghit_groups})

            dist_absvalue = abs(int(sim_value) - int(simvalue))
            sim_dist_keys.add(dist_absvalue)
            differencelist.append({dist_absvalue:sim_content_info})
        return differencelist

    # not rpc function
    def search_for_one(self,article_src):
        listkw = jieba.cut(article_src)
        kws = []
        for i in list(listkw):
            kws.append(i)
        search_body_str = self.query_table_data_dsl % (' '.join(kws))
        search_body = json.loads(search_body_str)
        response_hits = self.es.search(index=developer.INDEX_DATA_CENTER,doc_type=developer.DOC_TYPE_TABLE,body=search_body)
        row = response_hits.get('hits',{}).get('hits',[])
        for cont in row:
            result = cont['_source']
            if 'content' in result and 'project' in result:
                return result

    # not rpc function
    def get_hbase_con_one(self,docid):
        hd = hbase_dao()
        rec = hd.get(self.caizheng_table, docid)
        result = {"content":"","project":"","uuid":docid}
        for col in rec.columnValues:
            if col.qualifier == 'content':
                result["content"] = col.value
            if col.qualifier == 'project':
                result["project"] = col.value

        return result

    def get_differenceinfo(self, docid):
        hbase_row = self.get_hbase_con_one(docid)
        content = hbase_row['content']
        groups = self.hscan.scan_data_rowprex(docid,self.caizheng_table)
        max_distince=10
        data = get_different_info(content,groups,max_distince ,minsource = 0)
        result = {'project':hbase_row['project'],'uuid':hbase_row['uuid'],'data':data}
        return  json.dumps(result,ensure_ascii=False)

    def get_differenceparse(self, docid):
        hbase_row = self.get_hbase_con_one(docid)
        content = hbase_row['content']
        max_distince = 10
        groups = self.hscan.scan_data_rowprex(docid, self.caizheng_table)
        data = get_different_parse(content,groups, max_distince, minsource=0)
        result = {'project': hbase_row['project'], 'uuid': hbase_row['uuid'], 'data': data}
        return json.dumps(result, ensure_ascii=False)

    def get_differencecomment(self,docid):
        hbase_row = self.get_hbase_con_one(docid)
        content = hbase_row['content']
        max_distince = 10
        groups = self.hscan.scan_data_rowprex(docid, self.caizheng_table)
        data = get_different_comment(content,groups, max_distince, minsource=0)
        result = {'project': hbase_row['project'], 'uuid': hbase_row['uuid'], 'data': data}
        return json.dumps(result, ensure_ascii=False)

    def get_same_list(self, inputdata):
        # 文档查重-汇总列表
        result = []
        art = self.search_for_one(inputdata)
        if art is None :
            return  None
        input_content = unicode(art['content'])
        title = art['project']
        par_uuid = art['_uuid']
        if art is not None:
            row = art['_uuid']
            scan_list = self.hscan.scan_data_rowprex(row,self.caizheng_table,hase_self = False)
            for row in scan_list:
                try:
                    rowkey, con = row.items()[0]
                    con['content'] = unicode(con['content'])
                    source = get_sim_distance(input_content, con['content'])
                    str_source = str( 100 - source * 4)[0:5] + "%"
                    result.append({source:{
                                            "project":con["project"],
                                           "finical_unit":con["finical_unit"],
                                           "finical_name":con["finical_name"],
                                           "date":con["date"] ,"doc":con["doc"],
                                           # "content":con["content"] ,
                                            "unit":con["unit"],
                                           "finical":con["finical"],
                                           "source":str_source,
                                           "uuid":rowkey
                                           }})
                except:
                    print traceback.format_exc()
        result.sort()

        return json.dumps({'project':title,'uuid':par_uuid,'data':result},ensure_ascii=False)

    def get_different_2_docid(self, left_id, right_id):
        left =  self.get_hbase_con_one(left_id)
        art_left =left['content']
        right = self.get_hbase_con_one(right_id)
        art_right = right['content']
        max_distince = 10
        djson = get_different_2_doc(art_left, art_right, max_distince=max_distince)
        djson.update({'left_title':left['project'],'right_title':right['project']})
        return json.dumps(djson,ensure_ascii=False)
#
# if __name__ == '__main__':
#     dc = developer()
# #     # d = dc.get_hbase_con_one('103012946508812823141fd375085cffcaea49767177ce2287c1')
# #     # print(json.dumps(d,ensure_ascii=False,indent=1))
# #     # b = dc.get_hbase_con_one('1030129465413605815455d6f5388cece9313a5849e8b660f9b7')
# #     # print('---------------')
# #     # print(json.dumps(b, ensure_ascii=False, indent=1))
#     b=dc.get_different_2_docid('103012946508812823141fd375085cffcaea49767177ce2287c1','1030129465413605815455d6f5388cece9313a5849e8b660f9b7')
#     print b

# if __name__ == '__main__':
#     content = "省直有关单位： \r\n\r\n今年 3月，我厅以粤财农„2016‟53号文下达 2016 年省级\r\n\r\n农业标准化发展资金，其中，涉及省直单位的资金 455万元。根\r\n\r\n据组织省直单位项目申报和专家评审结果，现对该项资金安排作\r\n\r\n相应调整（具体单位和金额详见附件），并就有关事项通知如下： \r\n\r\n一、此项资金专项用于省级农业标准化项目等方面。请加强\r\n\r\n资金监管，确保专款专用，并按国库集中支付规定办理资金拨付\r\n\r\n手续。 \r\n\r\n二、此项资金请列入 2016年度 “农林水支出—农业—农产\r\n\r\n品质量安全（2130109）”一般公共预算支出科目；经济科目根据\n支出性质与实际用途列支。年终编报支出决算。 \r\n\r\n \r\n\r\n附件: 2016年省农业标准化专项资金（省直部分）安排表 \r"
#     ddoc = developer().get_differencelist_for_art(content)
#     print(json.dumps(ddoc,ensure_ascii=False,indent=1))

# if __name__ == '__main__':
#        print  '''省社保基金管理局： \r\n\r\n你局•关于请拨 2016 年 12 月省本级社会保险待遇及 2016\r\n\r\n年 11 月代发省财政统发退休人员待遇资金的函‣(粤社保函\r\n\r\n„2016‟463号)收悉。根据省财政厅•转发财政部 劳动和社会保\r\n\r\n障部关于印发†社会保险基金财务制度‡的通知‣（粤财社„1999‟\r\n\r\n74号）等相关规定，经审核，同意从省级社会保险基金财政专\r\n\r\n户中拨付 168,633 万元，用于预付 2016 年 12 月省本级社会保险\r\n\r\n待遇。其中：列入“20901 社会保险基金支出—基本养老保险\r\n\r\n基金支出”167,621 万元(含预付机关事业单位养老保险待遇\r\n\r\n20,288万元)，列入“20904社会保险基金支出—工伤保险基金支\n出” 1,012万元。年终按规定统一编报决算。 \r\n\r\n请结合省人力资源社会保障厅、省财政厅•关于省财政统发退\r\n\r\n休人员待遇发放问题的通知‣（粤人社函„2016‟830号）等有关\r\n\r\n文件要求，及时做好 2016年 12月省财政统发退休人员待遇发放工\r\n\r\n作。 \r'''
# #
if __name__ == '__main__':
    # ddoc = developer().get_different_2_docid("10003899642146308774bbe80347dc6dd43e545ae3ec25430c89","1000389964214630877431e318dcd34c335b75e47aaa32462c37")
    ddoc = developer().get_differenceparse("10003899642146308774bbe80347dc6dd43e545ae3ec25430c89")
    print ddoc

# if __name__ == '__main__':
#     dc = developer()
#
#     dp = dc.get_same_list("立法")
#     print dp
    # db = dc.get_differenceinfo('10003899642146308774015d507e10dccc995f70be4bf4f08c6c')
    # print db
    # left = dc.get_hbase_con_one('10003899642146308774bbe80347dc6dd43e545ae3ec25430c89')
    # right = dc.get_hbase_con_one('1000389964214630877431e318dcd34c335b75e47aaa32462c37')
    # print left
    #
    # print '------------------------------------------------------------------'
    #
    # print right



# if __name__ == '__main__':
#     print(".....starting....")
#     handler = developer()
#     print(".....finish....")
#     proc = sim_develop.Processor(handler)
#     # trans_ep = TSocket.TServerSocket(host="192.168.18.236",port=9994)
#     trans_ep = TSocket.TServerSocket(host="192.168.100.146", port=9994)
#     trans_fac = TTransport.TBufferedTransportFactory()
#     proto_fac = TBinaryProtocol.TBinaryProtocolFactory()
#     server = TServer.TThreadPoolServer(proc, trans_ep, trans_fac, proto_fac)
#     server.setNumThreads(10)
#     server.serve()
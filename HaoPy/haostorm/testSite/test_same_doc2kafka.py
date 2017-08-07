# -*- coding: utf-8 -*-

import unittest

from haokafka.same_art.phase2kafka import phase2kafka
from haoml.articlesimhash import art_get_phase
import traceback
import sys
import json
import copy
reload(sys)
sys.setdefaultencoding('utf-8')


class MyTestCase(unittest.TestCase):

    def test_build_2_kafka(self):
        content = '''　　第一章 总则\n　　第一条 根据北京市委、市政府《关于促进体育产业发展的若干意见》（京发[2007]15号）及《 北京市体育产业发展引导资金管理办法（试行）》（京体产业字[2010]11号）的有关规定，制定本办法。 第二条 本办法所称贷款贴息是指对在本市地域范围内从事体育产业及相关活动的企业及项目单位在项目实施期内从商业银行获得信贷资金后，对发生的利息进行归还部分的补贴。贷款贴息资金来源于北京市体育产业发展引导资金（以下简称引导资金）。 第三条 贷款贴息资金的使用应符合北京市体育产业发展规划及相关产业政策，在公开、公平、公正的基础上，遵循“差别优惠、比例核定、额度控制、先付后贴”的原则。\n　　第二章 贴息资金的管理机构与职责\n　　第四条 北京市体育产业部门联席会议（以下简称联席会议）负责贷款贴息资金管理工作中重大事项的研究、审议和决策:\n　　（一）研究制定贷款贴息资金的相关管理制度；\n　　（二）审定贷款贴息资金年度使用计划和项目预算；\n　　（三）监督贷款贴息政策和项目贴息资金的执行情况；\n　　（四）组织对项目贷款贴息资金使用情况进行监督检查。 第五条 北京市财政局负责贷款贴息资金的预算安排和资金监管:\n　　（一）根据预算管理有关规定，审核并下达年度项目贷款贴息预算；\n　　（二）对重大项目的资金使用情况进行绩效考评。 第六条 北京市体育产业部门联席会议办公室（以下简称联席会议办公室）负责贷款贴息资金日常管理工作:\n　　（一）研究编制贷款贴息资金年度使用计划和项目预算；\n　　（二）受理引导资金的贷款贴息项目申请，对申报项目初审，并组织专家进行评审；\n　　（三）根据专家评审意见提出项目贷款贴息支持方案，报联席会议审定；\n　　（四）跟踪检查项目贷款贴息资金使用情况，委托专业机构审计贴息资金使用情况；\n　　（五）对北京市体育产业贷款贴息项目资金的使用情况进行监督检查、考评等管理工作。\n　　第三章 贷款贴息条件\n　　第七条 贷款贴息申报条件:\n　　（一）项目单位在北京市注册且项目实施地为北京地区；\n　　（二）项目应符合引导资金的支持方向，内容应属于体育竞赛表演业、全民健身服务业、体育场馆服务业、体育用品生产销售业、体育中介服务业、与体育有关的新兴产业等行业；\n　　（三）项目贷款的银行应在北京市注册；\n　　（四）项目单位已在商业银行获得项目贷款；\n　　（五）项目贷款期限原则上不超过2年。 第八条 有下列情形之一的，不予贷款贴息支持:\n　　（一）在项目贷款延长期间发生的贷款利息；\n　　（二）项目贷款期到期不能按期偿还贷款本息；\n　　（三）贷款资金改变申报用途的；\n　　（四）已由或应由政府其他资金支持的；\n　　（五）贷款资金用途为基础设施建设的。\n　　第四章 贴息方式、期限、标准和额度\n　　第九条 贷款贴息方式为先付后贴，即项目单位已向贷款银行支付利息后，贷款贴息资金再予以贴息支持。 第十条 贴息期限原则上不超过2年。 第十一条 贴息资金实行比例核定，即贴息比例原则上为贷款贴息期限内实际支付利息总额的50％至100％。 第十二条 项目贷款贴息资金额度依据《借款合同》及借款人向商业银行实际支付的利息计算，即:\n　　项目贷款贴息支持额＝贴息期限内实际支付利息总额×贷款贴息比例\n　　第五章 贴息项目的申报、审定和执行\n　　第十三条 项目贴息申请原则上与年度北京市体育产业发展引导资金项目申报工作同时进行。 第十四条 项目单位在获得商业银行贷款后，根据年度北京市体育产业发展引导资金征集公告向联席会议办公室提交贷款贴息项目申请材料。 第十五条 联席会议办公室按照年度项目征集公告要求对项目进行初审。 第十六条 联席会议办公室组织专家对项目进行评审，并根据专家评审意见提出项目贴息方案编制项目预算，上报联席会议。 第十七条 联席会议审定贴息支持方案和项目预算。 第十八条 市财政局根据联席会议审核意见批复项目预算。项目预算一经批复下达后，项目单位不得自行调整。由于项目发生变化而引起预算需要调整的，由项目单位报联席会议办公室审定后，按有关程序报批。\n　　第六章 监督检查\n　　第十九条 项目单位应接受北京市体育产业部门联席会议办公室和市财政局的监督检查，并接受审计部门的审计。有下列行为之一的，市财政局追回所拨资金，并依据《 财政违法行为处罚处分条例》的规定进行处理。构成犯罪的，依法移交司法机关追究其法律责任:\n　　（一）提供虚假资料的；\n　　（二）截留、挤占、挪用引导资金，造成贷款贴息用途发生变化的；\n　　（三）其他违反国家有关法律、法规的行为。\n　　第七章 附则\n　　第二十条 本办法由联席会议办公室负责解释。 第二十一条 本办法自发布之日起执行。\n　　北京市体育产业部门联席会议办公室\n　　二〇一〇年四月十五日\n\t'''
        docid = '11040051325368615466a907ca01e2d19dcd7600fd93da311fc6'
        project = '北京市体育产业发展引导资金贷款贴息管理办法（试行）'
        sentences = art_get_phase(content)
        doc2ka = phase2kafka()
        doc2ka.producer_es_split_phases({'sentences': sentences, 'docid':docid, 'project':project})

    def test_pop_sentences_f_kafka(self):
        doc2ka = phase2kafka()
        balanced_consumer = doc2ka.consumer_es_search_doc()
        for message in balanced_consumer:
            if message is not None:
                try:
                    phases = json.loads(message.value)
                    for phase in phases:
                        result = (phase['sentence_id'], [unicode(phase['project']), unicode(phase['content'])])
                        print result
                    balanced_consumer.commit_offsets()
                except:
                    print traceback.format_exc().replace('\n', ' ')

    def test_pop_same_f_kafka(self):
        doc2ka = phase2kafka()
        group = 'a'
        doc_uuid = '11040051325368615466a907ca01e2d19dcd7600fd93da311fc6'
        balanced_consumer = doc2ka.consumer_es_same_phase(group, doc_uuid)
        for message in balanced_consumer:
            if message is not None:
                try:
                    print message.value
                    balanced_consumer.commit_offsets()
                except:
                    print traceback.format_exc().replace('\n', ' ')


    def test_data_converge(self):
        # 参数:--
        input_content = '''　　第一章 总则\n　　第一条 根据北京市委、市政府《关于促进体育产业发展的若干意见》（京发[2007]15号）及《 北京市体育产业发展引导资金管理办法（试行）》（京体产业字[2010]11号）的有关规定，制定本办法。 第二条 本办法所称贷款贴息是指对在本市地域范围内从事体育产业及相关活动的企业及项目单位在项目实施期内从商业银行获得信贷资金后，对发生的利息进行归还部分的补贴。贷款贴息资金来源于北京市体育产业发展引导资金（以下简称引导资金）。 第三条 贷款贴息资金的使用应符合北京市体育产业发展规划及相关产业政策，在公开、公平、公正的基础上，遵循“差别优惠、比例核定、额度控制、先付后贴”的原则。\n　　第二章 贴息资金的管理机构与职责\n　　第四条 北京市体育产业部门联席会议（以下简称联席会议）负责贷款贴息资金管理工作中重大事项的研究、审议和决策:\n　　（一）研究制定贷款贴息资金的相关管理制度；\n　　（二）审定贷款贴息资金年度使用计划和项目预算；\n　　（三）监督贷款贴息政策和项目贴息资金的执行情况；\n　　（四）组织对项目贷款贴息资金使用情况进行监督检查。 第五条 北京市财政局负责贷款贴息资金的预算安排和资金监管:\n　　（一）根据预算管理有关规定，审核并下达年度项目贷款贴息预算；\n　　（二）对重大项目的资金使用情况进行绩效考评。 第六条 北京市体育产业部门联席会议办公室（以下简称联席会议办公室）负责贷款贴息资金日常管理工作:\n　　（一）研究编制贷款贴息资金年度使用计划和项目预算；\n　　（二）受理引导资金的贷款贴息项目申请，对申报项目初审，并组织专家进行评审；\n　　（三）根据专家评审意见提出项目贷款贴息支持方案，报联席会议审定；\n　　（四）跟踪检查项目贷款贴息资金使用情况，委托专业机构审计贴息资金使用情况；\n　　（五）对北京市体育产业贷款贴息项目资金的使用情况进行监督检查、考评等管理工作。\n　　第三章 贷款贴息条件\n　　第七条 贷款贴息申报条件:\n　　（一）项目单位在北京市注册且项目实施地为北京地区；\n　　（二）项目应符合引导资金的支持方向，内容应属于体育竞赛表演业、全民健身服务业、体育场馆服务业、体育用品生产销售业、体育中介服务业、与体育有关的新兴产业等行业；\n　　（三）项目贷款的银行应在北京市注册；\n　　（四）项目单位已在商业银行获得项目贷款；\n　　（五）项目贷款期限原则上不超过2年。 第八条 有下列情形之一的，不予贷款贴息支持:\n　　（一）在项目贷款延长期间发生的贷款利息；\n　　（二）项目贷款期到期不能按期偿还贷款本息；\n　　（三）贷款资金改变申报用途的；\n　　（四）已由或应由政府其他资金支持的；\n　　（五）贷款资金用途为基础设施建设的。\n　　第四章 贴息方式、期限、标准和额度\n　　第九条 贷款贴息方式为先付后贴，即项目单位已向贷款银行支付利息后，贷款贴息资金再予以贴息支持。 第十条 贴息期限原则上不超过2年。 第十一条 贴息资金实行比例核定，即贴息比例原则上为贷款贴息期限内实际支付利息总额的50％至100％。 第十二条 项目贷款贴息资金额度依据《借款合同》及借款人向商业银行实际支付的利息计算，即:\n　　项目贷款贴息支持额＝贴息期限内实际支付利息总额×贷款贴息比例\n　　第五章 贴息项目的申报、审定和执行\n　　第十三条 项目贴息申请原则上与年度北京市体育产业发展引导资金项目申报工作同时进行。 第十四条 项目单位在获得商业银行贷款后，根据年度北京市体育产业发展引导资金征集公告向联席会议办公室提交贷款贴息项目申请材料。 第十五条 联席会议办公室按照年度项目征集公告要求对项目进行初审。 第十六条 联席会议办公室组织专家对项目进行评审，并根据专家评审意见提出项目贴息方案编制项目预算，上报联席会议。 第十七条 联席会议审定贴息支持方案和项目预算。 第十八条 市财政局根据联席会议审核意见批复项目预算。项目预算一经批复下达后，项目单位不得自行调整。由于项目发生变化而引起预算需要调整的，由项目单位报联席会议办公室审定后，按有关程序报批。\n　　第六章 监督检查\n　　第十九条 项目单位应接受北京市体育产业部门联席会议办公室和市财政局的监督检查，并接受审计部门的审计。有下列行为之一的，市财政局追回所拨资金，并依据《 财政违法行为处罚处分条例》的规定进行处理。构成犯罪的，依法移交司法机关追究其法律责任:\n　　（一）提供虚假资料的；\n　　（二）截留、挤占、挪用引导资金，造成贷款贴息用途发生变化的；\n　　（三）其他违反国家有关法律、法规的行为。\n　　第七章 附则\n　　第二十条 本办法由联席会议办公室负责解释。 第二十一条 本办法自发布之日起执行。\n　　北京市体育产业部门联席会议办公室\n　　二〇一〇年四月十五日\n\t'''


        word_count = 0
        single_word_count = 0
        parse_count = 0
        # ---

        # 从kafka拉取,代表每一句
        kafka_queue=[
            {"sam_in_phase": "", "sim_rate_value": 33.333,
             "same_doc_title": "\u5317\u4eac\u5e02\u4f53\u80b2\u4ea7\u4e1a\u53d1\u5c55\u5f15\u5bfc\u8d44\u91d1\u7ba1\u7406\u529e\u6cd5\uff08\u8bd5\u884c\uff09",
             "sam_sentence_id": "110575797397590699944e61ee33aa4a00803e7d0b1a599fccff:1",
             "sentence": "\u5173\u4e8e\u4fc3\u8fdb\u4f53\u80b2\u4ea7\u4e1a\u53d1\u5c55\u7684\u82e5\u5e72\u610f\u89c1",
             "upload_at": "\\N", "wordcount": 45, "sentences_count": 52, "doc_sentence_word_count": 15,
             "submiter": "\u67d0\u67d0", "doc_sentence_uuid": "11040051325368615466a907ca01e2d19dcd7600fd93da311fc6:1",
             "doc_title": "\u5317\u4eac\u5e02\u4f53\u80b2\u4ea7\u4e1a\u53d1\u5c55\u5f15\u5bfc\u8d44\u91d1\u8d37\u6b3e\u8d34\u606f\u7ba1\u7406\u529e\u6cd5\uff08\u8bd5\u884c\uff09",
             "find_sam_sentence": "<span class=\"lsim gray\">\u5173\u4e8e\u4fc3\u8fdb\u4f53\u80b2\u4ea7\u4e1a\u53d1\u5c55\u7684\u82e5\u5e72\u610f\u89c1</span>",
             "sim_rate": "33.333%", "doc_sentence_id": "1",
             "doc_sentence": "<span class=\"sim gray\">\u5173\u4e8e\u4fc3\u8fdb\u4f53\u80b2\u4ea7\u4e1a\u53d1\u5c55\u7684\u82e5\u5e72\u610f\u89c1</span>",
             "sam_sentence_word_count": 15,
             "find_sentence": "\u5173\u4e8e\u4fc3\u8fdb\u4f53\u80b2\u4ea7\u4e1a\u53d1\u5c55\u7684\u82e5\u5e72\u610f\u89c1"}
            ,{"sam_in_phase": "", "sim_rate_value": 33.333,
             "same_doc_title": "\u4e0a\u6d77\u5e02\u4eba\u6c11\u653f\u5e9c\u5173\u4e8e\u53d1\u5e03\u300a\u5173\u4e8e\u3008\u4e0a\u6d77\u5e02\u8d37\u6b3e\u9053\u8def\u5efa\u8bbe\u8f66\u8f86\u901a\u884c\u8d39\u5f81\u6536\u7ba1\u7406\u529e\u6cd5\u3009\u7b2c\u4e8c\u5341\u4e8c\u6761\u548c\u7b2c\u4e8c\u5341\u4e09\u6761\u9002\u7528\u95ee\u9898\u7684\u89e3\u91ca\u300b\u7684\u901a\u77e5",
             "sam_sentence_id": "158495815632212344946b6ee3982b126174af5a4bba150b7cc3:16",
             "sentence": "\u7684\u89c4\u5b9a\u8fdb\u884c\u5904\u7406", "upload_at": "\\N", "wordcount": 21,
             "sentences_count": 52, "doc_sentence_word_count": 7, "submiter": "\u67d0\u67d0",
             "doc_sentence_uuid": "11040051325368615466a907ca01e2d19dcd7600fd93da311fc6:45",
             "doc_title": "\u5317\u4eac\u5e02\u4f53\u80b2\u4ea7\u4e1a\u53d1\u5c55\u5f15\u5bfc\u8d44\u91d1\u8d37\u6b3e\u8d34\u606f\u7ba1\u7406\u529e\u6cd5\uff08\u8bd5\u884c\uff09",
             "find_sam_sentence": "\u7b2c\u4e8c\u5341\u4e8c\u6761<span class=\"lsim gray\">\u7684\u89c4\u5b9a\u8fdb\u884c\u5904\u7406</span>",
             "sim_rate": "33.333%", "doc_sentence_id": "45",
             "doc_sentence": "<span class=\"sim gray\">\u7684\u89c4\u5b9a\u8fdb\u884c\u5904\u7406</span>",
             "sam_sentence_word_count": 7,
             "find_sentence": "\u7b2c\u4e8c\u5341\u4e8c\u6761\u7684\u89c4\u5b9a\u8fdb\u884c\u5904\u7406"},
            {"sam_in_phase": "", "sim_rate_value": 33.333,
             "same_doc_title": "\u4e0a\u6d77\u5e02\u4eba\u6c11\u653f\u5e9c\u5173\u4e8e\u53d1\u5e03\u300a\u5173\u4e8e\u3008\u4e0a\u6d77\u5e02\u8d37\u6b3e\u9053\u8def\u5efa\u8bbe\u8f66\u8f86\u901a\u884c\u8d39\u5f81\u6536\u7ba1\u7406\u529e\u6cd5\u3009\u7b2c\u4e8c\u5341\u4e8c\u6761\u548c\u7b2c\u4e8c\u5341\u4e09\u6761\u9002\u7528\u95ee\u9898\u7684\u89e3\u91ca\u300b\u7684\u901a\u77e5",
             "sam_sentence_id": "158495815632212344946b6ee3982b126174af5a4bba150b7cc3:25",
             "sentence": "\u7684\u89c4\u5b9a\u8fdb\u884c\u5904\u7406", "upload_at": "\\N", "wordcount": 21,
             "sentences_count": 52, "doc_sentence_word_count": 7, "submiter": "\u67d0\u67d0",
             "doc_sentence_uuid": "11040051325368615466a907ca01e2d19dcd7600fd93da311fc6:45",
             "doc_title": "\u5317\u4eac\u5e02\u4f53\u80b2\u4ea7\u4e1a\u53d1\u5c55\u5f15\u5bfc\u8d44\u91d1\u8d37\u6b3e\u8d34\u606f\u7ba1\u7406\u529e\u6cd5\uff08\u8bd5\u884c\uff09",
             "find_sam_sentence": "\u7b2c\u4e8c\u5341\u4e8c\u6761<span class=\"lsim gray\">\u7684\u89c4\u5b9a\u8fdb\u884c\u5904\u7406</span>",
             "sim_rate": "33.333%", "doc_sentence_id": "45",
             "doc_sentence": "<span class=\"sim gray\">\u7684\u89c4\u5b9a\u8fdb\u884c\u5904\u7406</span>",
             "sam_sentence_word_count": 7,
             "find_sentence": "\u7b2c\u4e8c\u5341\u4e8c\u6761\u7684\u89c4\u5b9a\u8fdb\u884c\u5904\u7406"}
        ]

        sentence_set = {}
        content_diff_map = {}

        for sentence_detail in kafka_queue:
            sentence_detail['doc_sentence_id'] = int(sentence_detail['doc_sentence_id'])
            sam_id = sentence_detail['doc_sentence_uuid']
            # 去从并按分值排序
            if sam_id not in sentence_set.keys():
                sentence_set.update({sam_id:[]})
            sentence_set[sam_id].append({sentence_detail['sim_rate_value']:sentence_detail})

            # 文本差异映射列表
            sam_sentence_id = sentence_detail['sam_sentence_id']
            sam_sentence_id_split = sam_sentence_id.split(':')
            same_doc_id = sam_sentence_id_split[0]
            doc_sentence_id = sentence_detail['doc_sentence_id']

            diff_list = content_diff_map.get(same_doc_id,{})
            sdetail = {doc_sentence_id:{
                'doc_sentence':sentence_detail['doc_sentence'],
                'find_sam_sentence': sentence_detail['find_sam_sentence'],
                'wordcount': len(sentence_detail['find_sentence'].strip()),
                'sentence':sentence_detail['sentence']
            }}
            diff_list.update(sdetail)
            content_diff_map.update({same_doc_id : diff_list})

        sam_sent_unique = []
        sam_doc_score = {}
        max_score_set = []
        distribution = []
        # 获取最大分数
        check_count = 0
        sam_count = 0
        source_count = 0
        isFirst = True
        docDetail = {}
        isHad = False
        doc_same_list = []
        same_info_content = copy.deepcopy(input_content)
        sim_doc_map = {}
        # 逐句的相似
        for doc_sentence_uuid,sam_sentence in sentence_set.items():
            sam_sentence.sort(reverse=True)
            sam_detail = sam_sentence[0].values()[0]

            score = sam_detail['sim_rate_value']
            max_score_set.append(score)
            classname = 0
            str_classname = 'warn'
            local = int( float(sam_detail['doc_sentence_id']) * 100 / float(sam_detail['sentences_count']))
            if 40 >= score < 70:
                classname = 1
            elif score >= 70:
                classname = 2
                str_classname = 'serious'
            distribution.append({'local': local, 'type': classname})

            # same_info 内容替换 start:
            orig_sent = sam_detail['sentence'].strip()
            doc_sent_id = int(sam_detail['doc_sentence_id'])
            link_txt = u'''<a onclick="simInfo(this);" href="javascript:void(0);" source="%s" class="%s" id="%s" local="%s" >%s</a>''' % (
                sam_detail['sim_rate'], str_classname, doc_sent_id,
                local, orig_sent)
            same_info_content = same_info_content.replace(orig_sent, link_txt)
            # same_info 内容替换 end:

            # 分数累加
            check_count = check_count + sam_detail['wordcount']
            sam_count = sam_count + sam_detail['doc_sentence_word_count']
            source_count = source_count + score

            if isFirst:
                docDetail = sam_detail
                isFirst = False
                isHad = True

            # 相似列表
            doc_sent_id_split = doc_sentence_uuid.split(':')
            doc_id = doc_sent_id_split[0]
            sent_id = doc_sent_id_split[1]

            sam_sentence_id = sam_detail['sam_sentence_id']
            sam_sent_id_split = sam_detail['sam_sentence_id'].split(':')
            sam_id = sam_sent_id_split[0]
            sam_sent_id = sam_sent_id_split[1]

            if sam_sentence_id not in sam_sent_unique:
                sam_sent_unique.append(sam_sentence_id)
                if sam_id not in sam_doc_score.keys():
                    sam_doc_score.update({sam_id:[0.0, {'come_from':''
                                                        ,'upload_at':sam_detail['upload_at']
                                                        , 'upload_for': sam_detail['submiter']
                                                        , 'doc_name': sam_detail['same_doc_title']
                                                        , 'info_url': ''
                                                        ,  'uuid':sam_id
                                                       }]})
                sam_doc_score[sam_id][0] = sam_doc_score[sam_id][0] + sam_detail['sim_rate_value']

        sam_phase_content = []
        dcontent_ids = []
        for sam_doc_id, detail in sam_doc_score.items():
            iscore = detail[0]
            data_detail = detail[1]
            data_detail.update({"source": str(round(iscore / float(docDetail['sentences_count']),3))+'%'})
            doc_same_list.append({iscore:data_detail})

            # sam_info 组装右边数据结构 start :

            diff_con_list = content_diff_map[sam_doc_id]

            for sen_id,diff_con in diff_con_list.items():
                if sen_id not in dcontent_ids:
                    dcontent_ids.append(sen_id)
                    localvalue = int(float(sen_id) * 100 / float(docDetail['sentences_count']))
                    link_txt = u'''<a href="javascript:parseSimInfo('%s')" class="%s" id="%s" local="%s">%s</a>''' % (
                        sen_id, "black", sen_id, str(localvalue), diff_con['sentence'])
                    sam_phase_content.append({sen_id:[link_txt, localvalue]})

                mapsets = sim_doc_map.get(sen_id, [])
                sdetail = {
                "uuid": sam_doc_id,
                "title": docDetail['doc_title'],
                "index_parse": diff_con['doc_sentence'],
                "sim_parse_doc": "",
                "sim_parse": diff_con['find_sam_sentence'],
                "submiter": data_detail['upload_for'],
                "upload_at": data_detail['upload_at'],
                "wordcount": diff_con["wordcount"],
                "sim_rate": str(iscore)+ "%"
                }
                mapsets.append(sdetail)
                sim_doc_map.update({sen_id: mapsets})

            # sam_info 组装右边数据结果 end:

        doc_same_list.sort(reverse=True)
        # sam_info

        data = {"content": same_info_content.replace('\n', '<br>'), "right": sim_doc_map}
        info_result = {'project': docDetail['doc_title'], 'uuid': docDetail['doc_sentence_uuid'].split(':')[0], 'data': data}
        # sam_phase

        data_parse_result_content = []
        for d in sam_phase_content:
            vd = d.values()[0]
            data_parse_result_content.append({'id': d.keys()[0], 'name': vd[0], 'local': vd[1]})

        phase_main_data = {"content": data_parse_result_content, "right": sim_doc_map}
        phase_result = {'project': docDetail['doc_title'], 'uuid': docDetail['doc_sentence_uuid'].split(':')[0],
                       'data': phase_main_data}

        # sam_comment
        gobal_score = round(float(source_count) / float(docDetail['sentences_count']),3)


        data = {}
        if isHad:
            data = {"sim_source": str(gobal_score) + "%", "title": docDetail['doc_title'], "same_list": doc_same_list,
                    "check_count": check_count, "sim_count": sam_count, "word_count": word_count,
                    "parse_count":parse_count,
                    "single_word_count": single_word_count,
                    "distribution": distribution,
                    'sentence_count': docDetail['sentences_count'],
                    'sim_original': str(100.0 - gobal_score) + '%'}

        result = {'project': docDetail['doc_title'], 'uuid': docDetail['doc_sentence_uuid'].split(':')[0], 'data': data}
        print json.dumps(phase_result, ensure_ascii=False, indent=1)
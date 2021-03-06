# -*- coding: utf-8 -*-

import sys
import jieba
from jieba import analyse
from jieba import posseg
from haounits.loggerDefTools import get_defTestLogger
from haounits.cfgOptionTools import get_items_in_cfg, get_uri_relative_parent_package
import sources as source
reload(sys)
sys.setdefaultencoding('utf8')
userdictcnr = get_uri_relative_parent_package(source, 'userdict_cnr.txt')
userdictcns = get_uri_relative_parent_package(source, 'userdict_cns.txt')
userdictcnse = get_uri_relative_parent_package(source, 'userdict_cne.txt')
hanlp_data = get_uri_relative_parent_package(source, 'hanlp_data')
jieba.load_userdict(userdictcnr)
jieba.load_userdict(userdictcns)
jieba.load_userdict(userdictcnse)
from multiprocessing import Queue,Process
import traceback
log = get_defTestLogger()
__author__ = 'hao'


class jieba_keyword_extract():
    def __init__(self):
        pass

    def get_keywords(self,content):
        al = list(jieba.cut(content))
        return al

    def jieba_cut_entry(self,content):
        das = list(posseg.cut(content))
        result = []
        for d in das:
            wtype = d.flag
            if wtype == 'cnr' or wtype == 'cnrf' or wtype == 'cnrj' or wtype == 'cns' or wtype == 'cnt' or wtype == 'cne': # 中国人名识别 音译人名识别  日本人名识别 地名识别 机构名识别
                result.append([d.word, wtype])
        return result


if __name__ == '__main__':
    ke = jieba_keyword_extract()
    arts = u'''　　第一条 为规范江苏省著名商标认定工作，黑龙江省地方法规西藏自治区地方法规保护江苏省著名商标所有人的合法权益，提高本省产品的知名度和市场竞争能力，促进经济发展，根据《 中华人民共和国商标法》、《 中华人民共和国商标法实施细则》等有关法律、法规，结合本省实际，制定本办法。 第二条 本办法所称的江苏省著名商标是指在市场上享有较高声誉、为相关公众熟知，并经省工商行政管理部门依照本办法认定的注册商标。\n　　江苏省著名商标以被认定的注册商标及其核定使用的商品为限。 第三条 江苏省著名商标的认定和保护适用本办法。\n　　本办法有关商品商标的规定，适用于服务商标。 第四条 省工商行政管理部门负责江苏省著名商标的认定和管理工作。\n　　其他组织和个人不得认定或者采取其他方式变相认定江苏省著名商标。 第五条 江苏省著名商标的认定实行公平、公正、公开原则。 第六条 认定江苏省著名商标实行商标注册人自愿申请。\n　　申请认定江苏省著名商标应当符合下列条件：\n　　（一）该商标为国内注册商标，且商标注册人住所在本省境内；\n　　（二）使用该商标的商品市场覆盖面和占有率在省内同行业中位居前列；\n　　（三）使用该商标商品近三年来的销售额、利税或者出口创汇额等主要经济指标在省内同行业中领先；\n　　（四）该商标在相关公众中具有较高的认知程度，并能注重对该商标的广告宣传；\n　　（五）出口商品的商标应当在主要出口国（地区）注册，使用该商标的商品销售量较大或者销售地区广泛；\n　　（六）使用该商标的商品质量达到国际标准或者国内外先进标准，有明确的修理、更换、退货方式，消费者投诉率低；\n　　（七）未发生过侵犯他人注册商标专用权行为，具有较强的商标自我保护意识和严格的商标使用管理制度；\n　　（八）未发生过其他违反商标法律、法规、规章的行为。 第七条 商标注册人认为其注册商标符合本办法第六条第二款所列条件的，可以通过其所在地的设区的市或者县工商行政管理部门向省工商行政管理部门提出申请。 第八条 申请认定江苏省著名商标，应当填写《江苏省著名商标认定申请表》，并按照本办法第六条第二款规定的条件提供有关证明材料。证明材料必须真实可靠，并标明出处。 第九条 设区的市或者县工商行政管理部门应当在收到申请人提交的申请和有关证明材料之日起十五日内将有关材料上报省工商行政管理部门（县工商行政管理部门应当通过设区的市工商行政管理部门转报）。省工商行政管理部门应当在三十日内对有关材料进行审查，符合条件的，应予受理；不符合条件的，退回申请和证明材料并说明理由。予以受理或者不予以受理的，应当向申请人发出书面通知。\n　　申请书件基本齐备，但需补正的，省工商行政管理部门应当通知申请人在限期内按指定内容补正。逾期不补正的，退回申请材料。 第十条 省工商行政管理部门受理申请后，应当按照本办法第六条第二款所列条件进行调查、论证，并征询有关地区、部门、行业组织和社会团体的意见，在三个月内作出认定或者不予认定的决定，特殊情况可以延长一个月。 第十一条 对符合江苏省著名商标条件的，予以认定，由省工商行政管理部门发给《江苏省著名商标证书》，并予以公告；对不符合条件的，不予认定，书面通知申请人，并说明理由。 第十二条 江苏省著名商标所有人可以在其核定使用的商品和商品包装、装潢、说明书、交易文书上或者广告宣传、展览以及其他业务活动中使用“江苏省著名商标”字样，同时应当标明认定有效期。 第十三条 江苏省著名商标一经认定，其商标专用权在本省范围内即受到下列保护：\n　　（一）自著名商标公告之日起，他人将与该著名商标相同或近似的文字作为生产相同或类似产品的企业字号使用，且可能引起公众误认的，工商行政管理部门不予核准登记。\n　　（二）任何单位和个人不得擅自使用被认定为江苏省著名商标的商品特有的名称、包装、装潢或与其近似的名称、包装、装潢，造成混淆，引起购买者误认。\n　　（三）任何单位和个人均不得以任何方式丑化、贬低江苏省著名商标。\n　　（四）法律、法规、规章规定的其他保护措施。 第十四条 江苏省著名商标有效期为三年，自公告之日起计算。期满前三个月由该著名商标所有人重新提出认定申请。 第十五条 被认定为江苏省著名商标的，省工商行政管理部门可以向国家工商行政管理部门推荐认定驰名商标。 第十六条 江苏省著名商标所有人和使用人应当履行下列义务：\n　　（一）江苏省著名商标只能使用在被认定为江苏省著名商标时所核定的商品上，不得扩大使用范围；\n　　（二）应当加强商标的内部管理和自我保护，提高产品或者服务质量，维护著名商标的声誉；\n　　（三）江苏省著名商标所有人许可他人使用时，应当依法办理许可使用手续，并同时报送省工商行政管理部门备案；\n　　（四）江苏省著名商标所有人变更注册人名义、地址及其他注册事项的，应当在核准变更之日起三十日内将变更事项报送省工商行政管理部门备案；\n　　（五）江苏省著名商标所有人依法转让其商标时，受让人应当按本办法的规定重新申请认定江苏省著名商标；\n　　（六）法律、法规、规章规定的其他义务。 第十七条 有下列情形之一的，省工商行政管理部门应当撤销该江苏省著名商标资格并予以公告：\n　　（一）以提供虚假证明材料等欺骗手段获取江苏省著名商标的；\n　　（二）在产品中掺杂、掺假，以假充真，以次充好，或者以不合格产品冒充合格产品，损害消费者或者用户利益的；\n　　（三）侵犯他人注册商标专用权的；\n　　（四）违反本办法第十六条第（二）、（三）、（五）项规定，情节严重的；\n　　（五）有其他违反法律、法规、规章行为，严重影响江苏省著名商标声誉的。\n　　有前款所列行为的，任何单位或者个人可以向省工商行政管理部门提出撤销该著名商标的建议。 第十八条 对侵犯江苏省著名商标专用权的，工商行政管理部门可以依法采取行政措施制止侵权行为，并可以视情节轻重处以非法经营额３０％以上５０％以下或者侵权所获利润三倍以上五倍以下的罚款。对侵犯著名商标专用权的单位的直接责任人，工商行政管理部门可以视情节轻重处以５０００元以上１００００以下罚款；构成犯罪的，依法追究刑事责任。 第十九条 违反本办法第十三条第（二）项规定的，由工商行政管理部门依据《 中华人民共和国反不正当竞争法》的有关规定处罚；对违反本办法 第十三条第（三）项规定的，工商行政管理部门应当责令停止违法行为，并可以处以２００元以上１０００元以下罚款；有经营行为的，可以处以５００元以上５０００元以下罚款。\n　　未经省工商行政管理部门认定，伪称其商标为江苏省著名商标或者违反本办法第十六条第（一）项规定扩大使用范围的，工商行政管理部门应当责令停止违法行为，并可以处以１０００元以上１００００元以下的罚款；有违法所得的，可以处以５０００元以上３００００元以下的罚款。\n　　商标印制单位为实施本条第二款所列违法行为提供便利条件的，依照本条第二款规定处罚。 第二十条 工商行政管理部门依照本办法实施罚款时，应当使用省财政部门统一监制的罚款收据，罚款收入上缴国库。 第二十一条 工商行政管理工作人员及其他有关人员在认定和保护江苏省著名商标工作中，滥用职权、徇私舞弊的，应当依法给予行政处分；构成犯罪的，依法追究刑事责任。 第二十二条 本办法自发布之日起施行。\n\t'''
    import json
    print json.dumps(ke.jieba_cut_entry(arts),ensure_ascii=False)
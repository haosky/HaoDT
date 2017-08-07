# -*- coding: utf-8 -*-
import os
import re
import sys
import traceback
import argparse
from datetime import datetime
from simhash import Simhash, SimhashIndex
from haohbase.simart.get_for_scan import sim_sets
import jieba
from jieba import analyse
import json
import sys
import copy

reload(sys)
sys.setdefaultencoding('utf8')

rowprefixlen=8

def parse_args():
    global args

    parser = argparse.ArgumentParser(description='artucke simhash count')

    parser.add_argument('-i', '--input_data', help='input data', action='store_true', default=False)

    parser.add_argument('-s', '--search_data', help='data for calc the simhash distince', default=False)

    parser.add_argument('-d', '--distince', help='data for calc the simhash distince', default=False)

    args = parser.parse_args()


def art_get_phase(content) :
#     p = re.compile('''
#
# ''',re.S)
    content = unicode(content)
    # p = re.compile(u'''。|\.|!|？|！|\?|\n|\r\n|\r''',re.S)
    p = re.compile(u'''\r\n|\n|。|!|？|！|\?|；|》|《|[a-z,A-Z]''',re.S)
    return p.split(content)

def get_features(content):
    # width = 3
    content = unicode(content.strip())
    content = re.sub(re.compile(u'[\r\n，。,\.:"";“”\{\}【】：、）；（》《\n\s〔〕,0-9]+'), '', unicode(content.strip()))
    # s = re.sub(re.compile(u'， '),'', content)
    # al =  [content[i:i + width] for i in range(max(len(content) - width + 1, 1))]
    al = list(jieba.cut(content))
    # codes = [str(hash(a)) for a in al]

    # al = []
    # width = 2
    # for left_content in re.split(u'[\r\n，。,\.:"";“”\{\}【】：、）；（》《\n\s〔〕]+',unicode(content)):
    #     al.extend(list(jieba.analyse.extract_tags(left_content,width)))
    # al.sort()

    return al

def calc_distince(index_phases,search_phases,kdistince):

    input_dict = []
    i= -1
    for pharse in index_phases:
        i += 1
        pharse = pharse.strip()
        if(len(pharse)) <=3:
            continue
        input_dict.append([ '%s'%  i, Simhash(get_features(pharse)) ])
    index = SimhashIndex(input_dict, k=kdistince)
    i= -1
    for oput in search_phases:
        i += 1
        oput = oput.strip()
        if (len(oput)) <= 3:
            continue
        s1 = Simhash(get_features(oput))
        yield index.get_near_dups(s1), i


def main_calc(index,search,max_distince):
    input_phases = art_get_phase(unicode(index))
    search_phases = art_get_phase(unicode(search))
    gens = calc_distince(input_phases, search_phases, max_distince)
    result = {"similar": {}, "index": input_phases, "search": search_phases}
    for contentids, docid in gens: # art_src , art_dst
        if len(contentids) > 0:
            result["similar"].update({docid: []})
            for contentid in contentids:
                try:
                    result["similar"][docid].append(contentid)
                except Exception as e:
                    pass
    return  result


def main(input_file,search_file,distince):
    input_file = open(input_file).read().decode('utf8')
    search_file = open(search_file).read().decode('utf8')
    input_phases = art_get_phase(input_file)
    search_phases = art_get_phase(search_file)
    gens = calc_distince(input_phases, search_phases, distince)
    result={"similar":{},"index":input_phases,"search":search_phases}
    for contentids, docid in gens:
        if len(contentids) > 0:
            result["similar"].update({docid:[]})
            for contentid in contentids:
                try:
                    result["similar"][docid].append(contentid)
                except Exception as e:
                    print(e.message)
    # print json.dumps(result,ensure_ascii=False,encoding='utf8',indent=1)

    sim_content_info = result
    calc_weghit_groups = {}
    for output_phase_id, input_phase_idset in sim_content_info['similar'].items():

        for iid in input_phase_idset:
            sim_distinct = get_sim_distance(sim_content_info["index"][int(iid)],
                                            sim_content_info["search"][int(output_phase_id)])

            # 输入内容断落id :匹配内容断落id -- 距离
            calc_weghit_groups.update({"%s:%s" % (iid, output_phase_id): 1 - sim_distinct * 0.04})

        sim_content_info.update({'weight': calc_weghit_groups})

    html = build_weight_color_text(input_file, sim_content_info['weight'], sim_content_info['index'])
    json.dumps(sim_content_info, ensure_ascii=False, encoding='utf8', indent=1)
    print html


def doc_sim_list(content,doc,same_list):
    # 详细报告
    '''
    {id1;{doc1:iid1,doc2:iid2,doc3:iid2},id2:}
    '''
    page_html = {'html':''}
    for id, doc_sim_parse in same_list.items():

        viewhtml = None
        djson =[]
        for simdoc,simdocprop in doc_sim_parse.items():
            docstr = doc[id]
            ycontent = mark_same_content(docstr, simdocprop['content'])
            simcontent = mark_same_content(simdocprop['content'], docstr)
            html_parse =  {'ycontent': ycontent, 'simcontent': simcontent, 'simparse': simdocprop['parse'], 'title': simdocprop['title'],
             'unit': simdocprop['unit'], 'submiter': simdocprop['submiter'],
             'date': simdocprop['date']}
            djson.append(html_parse)

            # 左边列表长的内容展示
            if viewhtml is None :
                link_txt = '''<a href='javascript:simView()' content="%s">%s</a>''' % (json.dumps(viewhtml), docstr)
                content = re.sub(re.compile('[^>]' + docstr + '[^<]'), link_txt, content)

    page_html.update({'html':content})


def parse_sim_list(doc,same_list):
    # 相似片段
    pareses = {}
    for id, doc_sim_parse in same_list.items():

        djson =[]
        for simdoc,simdocprop in doc_sim_parse.items():
            docstr = doc[id]
            # ycontent = mark_same_content(docstr, simdocprop['content'])
            simcontent = mark_same_content(simdocprop['content'], docstr)
            html_parse =  { 'simcontent': simcontent, 'simparse': simdocprop['parse'], 'title': simdocprop['title'],
             'unit': simdocprop['unit'], 'submiter': simdocprop['submiter'],
             'date': simdocprop['date']}
            djson.append(html_parse)

    pareses.update({id:{'parse':doc[id],'simlist':djson}})
    return pareses



def build_weight_color_text(content, simdocs): # weight_info, doclist
    for term in simdocs:
        doclist = term['index']
        searchlist = term['search']
        weight_info = term['weight']
        for id_map,weight in weight_info.items():
            ids = id_map.split(':')
            index_id = int(ids[0])
            search_id = int(ids[1])
            docstr =  doclist[index_id]
            searchstr = searchlist[search_id]
            ycontent = mark_same_content(docstr, searchstr)
            simcontent = mark_same_content(searchstr, docstr)
            viewhtml = [{'ycontent':ycontent,'simcontent':simcontent,'simparse':'','title':'','unit':'','submiter':'','date':''}]
            link_txt = '''<a href='simView()' content="%s">%s</a>''' % (json.dumps(viewhtml),docstr)
            content = re.sub(re.compile('[^>]'+docstr+'[^<]' ),link_txt,content) #content.replace(docstr, link_txt)
    return content


def test_main():
    a ='C:\Users\gxkj-hao\PycharmProjects\untitled\ss'
    b = 'C:\Users\gxkj-hao\PycharmProjects\untitled\ss2'
    c = 10
    input_file = open(a).read().decode('utf8')
    search_file = open(b).read().decode('utf8')
    input_phases = art_get_phase(input_file)
    search_phases = art_get_phase(search_file)

    gens = calc_distince(input_phases, search_phases, c)
    for contentids,docid in gens :
        if len(contentids) > 0:
            print(search_phases[int(docid)])
            print("similarity:\n\n")
            for contentid in contentids:
                try:
                    print("doc:")
                    print(input_phases[int(contentid)])
                    print("\n")
                except Exception as e:
                    print(e.message)
                    print(" ")
            print("------------------------")

def get_sim_distance(content_src,content_dst):
    return  float(Simhash(get_features(content_src)).distance(Simhash(get_features(content_dst))))


def mark_same_content(left_content,right_content,classname,prefix_str=u'<span class="%s">%s</span>%s'):
    width = 3
    left_list = []
    left_content = unicode(left_content)
    enc = len(left_content) % 3
    sim_word_count = 0
    if enc == 1:
        left_content = left_content+u'  '
    else:
        left_content = left_content + u' '

    right_content = unicode(right_content)
    copy_right = copy.deepcopy(right_content)
    like_parse = []
    mxlen =  len(left_content)
    for ln in  xrange(0,mxlen,1):
        curr_str_len = mxlen - ln
        if curr_str_len < width:
            break
        for i in xrange(0,ln):
            left_list.append({left_content[i:curr_str_len + i]:[i,curr_str_len + i]})

    i = 0
    for cz in left_list:
        lw,index = cz.items()[0]
        while lw in copy_right:
            like_parse.append(lw)
            copy_right = copy_right.replace(lw,u'%|'+str(i)+u'|%',1)
        i+=1
    copy_right = copy_right + u' '

    parse_build_set = copy_right.split(u'%|')
    re_str_buff= []
    for pb in parse_build_set:
        if u'|%' in pb:
            lx = pb.split(u'|%')
            list_index = int(lx[0])
            re_str_buff.append(prefix_str % (classname,left_list[list_index].keys()[0] , lx[1]))
            sim_word_count = sim_word_count + len(unicode(left_list[list_index].keys()[0].replace(u' ',u'')))
        else:
            re_str_buff.append(pb)
    return u''.join(re_str_buff).strip(), sim_word_count

def get_content_simvalue(content):
    content = unicode(content)
    s1 = Simhash(get_features(content)).value
    s1 = '00000000000' + str(s1)
    return s1[-20:]

def get_content_simsource(contentleft,contentright):
    sim_distinct = get_sim_distance(contentleft,
                                    contentright)

    # 输入内容断落id :匹配内容断落id -- 距离
    source = 1 - sim_distinct * 0.04
    return source

def get_differencelist_for_art(content,groups):

    differencelist = []

    for group in groups:
        fin_content = group.values()[0]['content']
        sim_content_info = main_calc(fin_content, content, 10)
        calc_weghit_groups = {}
        souce_sun = 0
        for output_phase_id, input_phase_idset in sim_content_info['similar'].items():

            for iid in input_phase_idset:
                sim_distinct = get_sim_distance(sim_content_info["index"][int(iid)],
                                                sim_content_info["search"][int(output_phase_id)])

                # 输入内容断落id :匹配内容断落id -- 距离
                weight = 1 - sim_distinct * 0.04
                calc_weghit_groups.update({"%s:%s" % (iid, output_phase_id): weight})
                souce_sun = weight + souce_sun
            sim_content_info.update({'weight': calc_weghit_groups})

        source = float(souce_sun) * 100 /  float((len(sim_content_info["index"]) - sim_content_info["index"].count("") ))
        differencelist.append({source:sim_content_info})
    differencelist.sort(reverse=-1)
    return differencelist

def get_different_info(content,groups,max_distince ,minsource = 0):
     index_doc_parse = art_get_phase(unicode(content))
     sim_doc_map = {}
     #获取相似文章
     sim_doc_list = groups
     sim_source_list = {}
     for doc in sim_doc_list:
         simdoc = doc.values()[0]
         doc_content = unicode(simdoc['content'])
         search_doc_parse = art_get_phase(doc_content)
         gens = calc_distince(copy.deepcopy(index_doc_parse), copy.deepcopy(search_doc_parse), max_distince)
         for contentids, docid in gens:  # search_docid , index_docid
             first_source = True
             for contentid in contentids:
                 try:
                     leftcontent = index_doc_parse[int(contentid)]
                     rightcontent = search_doc_parse[int(docid)]
                     ilocal = max(doc_content.index(rightcontent) - 10,0)
                     sim_parse_doc = doc_content[ilocal:len(rightcontent)+10+ilocal]
                     sim_parse_doc = sim_parse_doc.replace(rightcontent,"<span class='sim_parse'>"+rightcontent+"</span>")
                     right,sim_word_count = mark_same_content(leftcontent,rightcontent,"sim gray")
                     left,sim_word_count = mark_same_content(rightcontent, leftcontent,"lsim gray")
                     source = get_content_simsource(leftcontent, rightcontent)
                     if first_source and docid not in sim_source_list.keys():
                         sim_source_list.update({docid:[source,contentid]})
                     sdetail = {
                     "title": simdoc["project"],
                      "index_parse":left,
                      "sim_parse_doc":sim_parse_doc,
                      "sim_parse" : right,
                      "submiter": "aaa",
                      "upload_at": simdoc["date"],
                      "wordcount": len(doc_content),
                      "sim_rate": str(source*100)[0:5] +"%"
                     }
                     mapsets = sim_doc_map.get(docid, [])
                     mapsets.append(sdetail)
                     sim_doc_map.update({docid: mapsets})
                     break
                 except:
                    print traceback.format_exc()

     for contentid,docval in sim_source_list.items():
         docid = docval[1]
         source  = docval[0]
         classname = 'warn'
         if source >= 0.7:
             classname='serious'
         docstr = index_doc_parse[int(docid)]
         localvalue = int(float(docid) * 100 / float(len(index_doc_parse)))
         link_txt = u'''<a href="javascript:simInfo('%s')" source="%s" class="%s" id="%s" local="%s" >%s</a>''' % (contentid, str(source*100)[0:5] +"%",classname,contentid,str(localvalue),docstr)
         #content = re.sub(re.compile(u'[^>]' + docstr), link_txt, content)
         content = content.replace(docstr,link_txt)
     result = {"content":content.replace('\n','<br>'),"right":sim_doc_map}
     return result

def get_different_parse(content,groups,max_distince ,minsource = 0):
    index_doc_parse = art_get_phase(unicode(content))
    sim_doc_map = {}
    # 获取相似文章
    sim_doc_list = groups
    sim_source_list = {}
    for doc in sim_doc_list:
        simdoc = doc.values()[0]
        doc_content = unicode(simdoc['content'])
        search_doc_parse = art_get_phase(doc_content)
        gens = calc_distince(copy.deepcopy(index_doc_parse), copy.deepcopy(search_doc_parse), max_distince)
        for contentids, docid in gens:  # search_docid , index_docid
            first_source = True
            mapsets = []
            for contentid in contentids:
                leftcontent = index_doc_parse[int(contentid)]
                rightcontent = search_doc_parse[int(docid)]
                ilocal = 0
                try:
                    ilocal = 0 if simdoc['content'] is None else max(doc_content.index(rightcontent) - 10, 0)
                except:
                    print traceback.format_exc()
                    print doc_content
                sim_parse_doc = doc_content[ilocal:len(rightcontent) + 10 + ilocal]
                sim_parse_doc = sim_parse_doc.replace(rightcontent,
                                                      "<span class='sim_parse'>" + rightcontent + "</span>")
                right,sim_word_count = mark_same_content(leftcontent, rightcontent, "sim gray")
                left,sim_word_count = mark_same_content(rightcontent, leftcontent, "lsim gray")
                source = get_content_simsource(leftcontent, rightcontent)
                if first_source and docid not in sim_source_list.keys():
                    sim_source_list.update({docid: [source,contentid]})
                sdetail ={- source:{
                    "title": simdoc["project"],
                    "index_parse": left,
                    "sim_parse_doc": sim_parse_doc,
                    "sim_parse": right,
                    "submiter": "aaa",
                    "upload_at": simdoc["date"],
                    "wordcount": len(doc_content),
                    "sim_rate": str(source * 100)[0:5] + "%",
                }}
                mapsets = sim_doc_map.get(docid, [])
                mapsets.append(sdetail)
                sim_doc_map.update({docid: mapsets})
                break

    for doc,maps in sim_doc_map.items():
         sim_doc_map[doc].sort()

    content_parse=[]
    for contentid,docval in sim_source_list.items():
        docid = docval[1]
        source = docval[0]
        # classname = 'warn'
        # if source >= 0.7:
        #     classname = 'serious'
        docstr = index_doc_parse[int(docid)]
        localvalue = int(float(docid) * 100 / float(len(index_doc_parse)))
        link_txt = u'''<a href="javascript:parseSimInfo('%s')" class="%s" id="%s" local="%s">%s</a>''' % (
            contentid, "black", contentid, str(localvalue),docstr)
        # # content = re.sub(re.compile(u'[^>]' + docstr), link_txt, content)
        # content = content.replace(docstr, link_txt)

        content_parse.append(link_txt)

    result = {"content": content_parse, "right": sim_doc_map}
    return result


def get_different_comment(content,groups,max_distince ,minsource = 0):
    index_doc_parse = art_get_phase(unicode(content))
    sim_doc_map = {}
    # 获取相似文章
    sim_doc_list = groups
    sim_source_list = {}
    check_count = 0
    sim_g_count = 1
    cdict= list(jieba.cut(content))
    word_count = len(cdict)
    single_word_count = 0
    # for w in cdict:
    #     single_word_count = single_word_count + len(w)
    single_word_count = len(content)
    parse_count = content.count(u'''\n''')
    doc_same_list = []
    isfist = True
    distribution = []
    for doc in sim_doc_list:
        simdoc = doc.values()[0]
        docname = simdoc['project']
        doc_content = unicode(simdoc['content'])
        search_doc_parse = art_get_phase(doc_content)
        gens = calc_distince(copy.deepcopy(index_doc_parse), copy.deepcopy(search_doc_parse), max_distince)
        phase_len = len(index_doc_parse)
        doccheckcount = 0
        docsimcount = 0
        docsource = {}

        for contentids, docid in gens:  # search_docid , index_docid
            for contentid in contentids:
                leftcontent = index_doc_parse[int(contentid)]
                rightcontent = search_doc_parse[int(docid)]
                source = get_content_simsource(leftcontent, rightcontent)
                classname = 0
                if 0.4 >= source < 0.7:
                    classname = 1
                elif source >= 0.7:
                    classname = 2
                if isfist:
                    distribution.append({'local': int(float(contentid) * 100 / float(phase_len)), 'type': classname})
                    if docid not in sim_source_list.keys():
                        sim_source_list.update({contentid: source})
                        right, sim_word_count = mark_same_content(leftcontent, rightcontent, "sim gray")
                        check_count = check_count + len(leftcontent)
                        sim_g_count = sim_g_count + sim_word_count
                        break
                else :
                    if docid not in docsource.keys():
                        docsource.update({contentid: source})
                        right, sim_word_count_c = mark_same_content(leftcontent, rightcontent, "sim gray")
                        doccheckcount = doccheckcount + len(leftcontent)
                        docsimcount = docsimcount + sim_word_count_c
                        break

        if not isfist:
            isource = 0 if doccheckcount == 0 else min(float(docsimcount) / float(doccheckcount) * 100, 100)
            if isource <= 0:
                continue
            doc_same_list.append({-isource: {"come_from": "专项资金项目库", "upload_at": "广州", "upload_for": "左桂春",
                                               "doc_name": docname, "source": str(isource)[0:5] + "%", "info_url": "",
                                               "uuid": doc.keys()[0]}})

        isfist = False


        # 基于距离
        # doc_source = get_sim_distance(content, simdoc['content'])
        # isource = 100 - doc_source * 4

    doc_same_list.sort()
    art_sim_source = 0 if check_count ==0 else min(float(sim_g_count) / float(check_count) * 100,100)
    result = {"sim_source":str(art_sim_source)[0:5] + "%","title":"","same_list": doc_same_list, "check_count": check_count,"sim_count":sim_g_count,"word_count":word_count,"parse_count":parse_count,"single_word_count":single_word_count, "distribution":distribution}
    return result

def get_different_2_doc(left_doc,right_doc, max_distince=10):
    index_doc_parse = art_get_phase(unicode(left_doc))
    search_doc_parse = art_get_phase(unicode(right_doc))
    gens = calc_distince(copy.deepcopy(index_doc_parse), copy.deepcopy(search_doc_parse), max_distince)
    sim_list = {}
    for contentids, docid in gens:  # search_docid , index_docid
        for contentid in contentids:
            leftcontent = index_doc_parse[int(contentid)]
            rightcontent = search_doc_parse[int(docid)]
            source = get_content_simsource(leftcontent, rightcontent)

            classname = 'warn'
            if source >= 0.8:
                classname = 'serious'

            right, sim_word_count = mark_same_content(leftcontent, rightcontent, classname,prefix_str='<span class="%s" >%s</span>%s')
            left, sim_word_count = mark_same_content(rightcontent,leftcontent, classname,prefix_str='<span class="%s">%s</span>%s')
            sim_list.update({contentid:[source, int(contentid), left, int(docid), right]})
            break

    for docid, art in sim_list.items():
        docstr = index_doc_parse[art[1]]
        searchstr = search_doc_parse[art[3]]

        # left_doc =  left_doc.replace(docstr,'<a href="javascript:graxySimLine(\''+str(docid)+'\')" id="'+str(docid)+'">'+art[2]+'</a>')
        left_doc = left_doc.replace(docstr, '<a onclick="graxySimLine(this);" href="javascript:void(0);" id="' + str(
            docid) + '">' + art[2] + '</a>')

        right_doc = right_doc.replace(searchstr, '<a href="" line_id="'+str(docid)+'">' + art[4] + '</a>')

    left_doc = left_doc.replace('\n','<br>')
    right_doc = right_doc.replace('\n', '<br>')
    return {'left':left_doc,'right':right_doc}

# if __name__ == '__main__':
#     content = '''但公路等级总体上还不够高，目前还没有高等级进出境公路，严重制约了招商引资和经济发展'''
#     sim = get_content_simvalue(content)
#     print(sim)
#
#     content = '''但公路等级总体上还不够高，目前还没有高等级进出境公路，制约了招商引资和经济发展'''
#     sim = get_content_simvalue(content)
#     print(sim)

    # #03923634771804803035
    # #03942775216250015707
    # data = sim_sets().scan_data_rowprex(str(sim),'YAJYPhase',hase_self=False,len=5,ks=['docId','phase','phaseId'])
    # print json.dumps(data,ensure_ascii=False,indent=1)

if __name__ == '__main__':
    content = "2017年度就业及技工教育专项资金（技工院校及\r\n技能实训基地建设方向）项目申请报告\r\n（省级基础教育师资培训经费（强师工程））\r\n申报单位： 广东省高级技工学校 \r\n          申报项目：    教师资助项目    \r\n          联 系 人：     成百辆         \r\n          联系电话：    13068268627     \r\n          传真电话：    0752-6281992    \r\n目录\r\n\u0013 TOC \\o \"1-2\" \\h \\z \\u \u0014\u0013 HYPERLINK \\l \"_Toc465863473\" \u0001\u0014一、学校简介\t\u0013 PAGEREF _Toc465863473 \\h \u0001\u00141\u0015\u0015\r\n\u0013 HYPERLINK \\l \"_Toc465863474\" \u0001\u0014二、项目概况\t\u0013 PAGEREF _Toc465863474 \\h \u0001\u00142\u0015\u0015\r\n\u0013 HYPERLINK \\l \"_Toc465863475\" \u0001\u0014三、项目基本情况\t\u0013 PAGEREF _Toc465863475 \\h \u0001\u00143\u0015\u0015\r\n\u0013 HYPERLINK \\l \"_Toc465863476\" \u0001\u0014四、项目必要性\t\u0013 PAGEREF _Toc465863476 \\h \u0001\u00145\u0015\u0015\r\n\u0013 HYPERLINK \\l \"_Toc465863477\" \u0001\u0014五、项目可行性\t\u0013 PAGEREF _Toc465863477 \\h \u0001\u00146\u0015\u0015\r\n\u0013 HYPERLINK \\l \"_Toc465863478\" \u0001\u0014六、资金绩效目标及绩效表\t\u0013 PAGEREF _Toc465863478 \\h \u0001\u001410\u0015\u0015\r\n\u0013 HYPERLINK \\l \"_Toc465863479\" \u0001\u0014七、资金预算书\t\u0013 PAGEREF _Toc465863479 \\h \u0001\u001412\u0015\u0015\r\n\u0013 HYPERLINK \\l \"_Toc465863480\" \u0001\u0014八、佐证材料\t\u0013 PAGEREF _Toc465863480 \\h \u0001\u001415\u0015\u0015\r\n\u0013 HYPERLINK \\l \"_Toc465863481\" \u0001\u0014杨文杰教师资助项目申请报告\t\u0013 PAGEREF _Toc465863481 \\h \u0001\u001417\u0015\u0015\r\n\u0013 HYPERLINK \\l \"_Toc465863482\" \u0001\u0014黄磊教师资助项目申请报告\t\u0013 PAGEREF _Toc465863482 \\h \u0001\u001442\u0015\u0015\r\n\u0013 HYPERLINK \\l \"_Toc465863483\" \u0001\u0014温锦文教师资助项目申请报告\t\u0013 PAGEREF _Toc465863483 \\h \u0001\u001475\u0015\u0015\r\n\u0013 HYPERLINK \\l \"_Toc465863484\" \u0001\u0014张小清教师资助项目申请报告\t\u0013 PAGEREF _Toc465863484 \\h \u0001\u0014108\u0015\u0015\r\n\u0013 HYPERLINK \\l \"_Toc465863485\" \u0001\u0014王怀术教师资助项目申请报告\t\u0013 PAGEREF _Toc465863485 \\h \u0001\u0014138\u0015\u0015\r\n省级基础教育师资培训\r\n教师资助项目专项资金的申请报告\r\n一、学校简介\r\n广东省技师学院是广东省人民政府主办，直属广东省人力资源和社会保障厅的副厅级公办的国家级重点技工院校。 现有占地面积335亩，拥有博罗校本部和广州校区两个教学区，建筑面积20万平方米，全日制在册学生14526人，现有11个教学系，共开设65个专业，其中高级工以上专业40个，职业技能鉴定工种44个，年培训量4.7万人次，年鉴定量2.1万多人次。建有院内专业实训教室148间，技能大师工作室16间，是广东省历史最长、规模最大、综合实力最强的国家级重点技工院校。 \r\n学院有高级职称教师139人，双师型教师428人（占教师比例94.9%），其中有1位获全国五一劳动奖章、3位获国务院特殊津贴、6位获全国技术能手、3位全国优秀（模范）教师、1位获全国高技能人才培育突出贡献奖、2位获广东五一劳动奖章、29位获广东省技术能手。近几年，学院获国家级职业技能大赛奖4项，专利16项，获省级职业技能大赛奖22项，正式出版教材54本，公开发表论文293篇，教研成果获奖161个，获第43届世界技能大赛电子技术项目全国唯一参赛资格，荣获第43届世界技能大赛电子技术项目优胜奖。\r\n申请受资助的教师基本情况如下：杨文杰老师是我校数控技术系老师。工作以来，先后获得南粤优秀教师、博罗县优秀教师、广东省数控装调维修竞赛优秀教练。培养的选手获广东省职工组第一名、高技组第一名、中职组第一名,选手获广东省技术能手，广东省“五一劳动奖章”；黄磊老师现任广东省高级技工学校信息技术系计算机综合科科长，科内专职教师18名。曾完成国家中职示范校计算机网络技术专业建设项目，并通过专家组验收。指导学生参加第44届世界技能大赛广东省选拔赛网站设计和网络管理项目并获奖；温锦文老师系我校汽车工程系骨干教师，所带学生获第44届世界技能大赛汽车喷漆项目广东省选拔赛第二名。学校有独立的汽车喷涂实训中心，设备齐全，目前已着手准备水性漆教学；学校于成立了质量技术系，我校产品检测与质量管理专业学生供不应求，至2016年7月为社会和企业输送了近600名素质高的实用型人才。张小清老师是我校产品检测与质量管理专业骨干教师，曾获东部地区广东选拔赛模具制造工职工组（冷冲模）第三名，惠州市技术能手等荣誉称号；我校设有物流专业培养具有物流管理基本能力和在各种类型物流企业及生产企业物流管理部门从事物流系统设计及物流经营、管理、决策工作的技师层次高级应用型技能人才。王怀术老师现为广州校区物流专业组长，多次在广东省物流师大赛中获奖并指导学生获奖，获广东省技术能手称号。\r\n二、项目概况\r\n（一）项目基本情况\r\n项目名称：教师资助项目\r\n项目类别：省级基础教育师资培训经费教师资助项目专项资金\r\n项目实施周期：一年\r\n（二）项目建设内容与任务\r\n1.通过对黄磊老师的资助，资助黄磊教师通过参加相关专业技能培训班、下厂生产实践、教研交流、参加德育、教学管理培训、学术讲座，带领新教师，参加行业专家交流会，学习专业目前的新知识与新技能，提升黄磊教师自身专业技能能力、教研科研能力，指导和带动本专业其他教师的成长并提高世赛网站设计、网络管理项目选拔赛成绩。\r\n2.通过对温锦文老师的资助，资助温锦文到国内外汽车水性漆喷涂技术领域领先的高校及企业学习、进修。学习掌握汽车水性漆的特性、水性漆（单工序、双工序、三工序）喷涂方法、调色技术。同时研究高校与高职院校汽车水性漆喷涂技术专业的课程设置。通过资助对象走访企业，向企业技术员请教汽车水性漆喷涂技术，并分别到广东雅图化工有限公司、珠海龙神有限公司、上海庞贝捷油漆贸易有限公司（美国PPG工业集团）等企业学汽车水性漆的喷涂及调色技术，提升该教师自身专业技能能力。通过邀请世赛专家进校进行培训、指导，提高我校世赛汽车喷漆选拔赛成绩。 \r\n3.通过对杨文杰老师的资助，资助教师通过参加相关专业技能培训班、下厂生产实践、教研交流、参加教学管理培训、学术讲座，发表专业论文，带领新教师，参加行业专家交流会，学习专业目前的新知识与新技能，提升杨文杰教师自身专业技能能力、教研科研能力，指导和带动本专业其他教师的成长并提高全国赛数控维修项目及世赛相关项目成绩。\r\n4.通过对张小清老师的资助，使其掌握产品精密检测技术新技术。针对检测设备的应用，到厂家指定培训中心或其它培训机构进行技能培训，学习掌握检测设备的操作应用；参加企业实践，学习掌握精密检测行业新工艺、新技术知识，不断提高实践教学指导能力，同时到高校学习精密检测专业设置及教学模式，完善产品检测专业建设。；二是完善产品检测与质量管理专业实训课题开发工作，成立课题和试题库开发工作小组，通过三坐标精密测量、影像测量和金属材料性能检测三项实习课题建设和试题库开发工作，培养具有专业能力，具有教科研能力的专业教师，体现资助对象骨干教师带头作用。三是通过与企业合作平台，完成对学生或企业员工三坐标精密测量技术的培训工作。\r\n5.通过资助王怀术老师，主要使该教师掌握利用大数据、交互系统、卫星导引定位等创新物流管理服务模式，为校区物流管理专业教学做好充足的准备；二是完善物流管理专业人才需求调研、工作岗位调研、制定人才培养方案、人才培养课程体系工作，通过课题建设培养具有专业能力，使该教师成为具有教科研能力的专业带头人。\r\n（三）预期目标：通过资助五位教师提升个人自身能力素质，帮助其他教师提升能力素质，产生辐射效应，全面提高师资队伍素质为目标，提升学校在教科研水平、技能竞赛、校企合作方面的影响力。把五位教师打造成各相应专业带头人。\r\n（四）投资规模：该项目总共投资25万元，其中18.9万元用于提升教师个人能力素质；6.1万元用于提升其他教师个人能力素质。\r\n三、项目基本情况\r\n省级基础教育师资培训经费教师资助 项目基本情况表    市（财政省直管理县）财政局（盖章）           市（财政省直管理县）人力资源社会保障局（盖章）项目名称省级基础教育师资培训经费教师资助项目项目依据立项情况正在办理立项前准备工作 《关于做好2017年度就业及技工教育专项资金（技工院校及技能实训基地建设方向）项目库入库项目申报工作的预通知》【粤人社函〔2016〕2020号】。投资总额（万元）25投资结构（万元）项目简介基础建设0结合广东省技工学校师资队伍建设现状，通过对黄磊、温锦文、杨文杰、张小清、王怀术5位教师的资金资助，提升资助教师个人综合能力和帮助其他教师提升教学能力。设置购置及\u000B信息化建设0教学改革25筹资方案（万元）已落实资金0申报省级资金25万元项目情况绩效目标起始时间（年月）2017年1月以全面提高资助教师综合素质为目标，实施教师学历、技能等级提升计划、师资培训计划，师德教育教育计划，着力于把资助教师培养成专业学科带头人，以点带面，全面提高本专业师资队伍素质。1、发表论文3 篇；2、帮扶其他教师12位；3、参加各类培训11次；4、举办各类培训班6次；5、攻关课题一项终止时间（年月）2017年12月项目存续状态新增项目\u000B申报单位： 广东省高级技工学校   填报人：成百辆       手机：13068268627\r\n项目负责人：夏  青       手机：18928389979\r\n四、项目必要性\r\n（一）背景分析\r\n学校高度重视以师资队伍为核心的人才队伍建设，制定了《“十二五”师资队伍建设规划》，确定师资队伍建设目标，以补充数量、改善结构、提高素质为主线，坚持培养和引进并重，使师资数量适度增加，结构明显改善，层次显著提升。高层次、高技能人才数量可观。重点优势专业和新开设专业的师资队伍建设得到进一步加强，学科带头人和骨干教师的作用得到充分发挥，我校的教学科研水平显著提升。\r\n（二）存在问题及影响分析\r\n1.师资队伍能力较单一。学校新引进或补充的教师多来自高校应届毕业生、本校毕业生和企业技术人员。高校应届毕业生掌握了比较前沿的理论知识，但动手能力和教学经验欠缺，而本校毕业生或企业聘请的技术人员动手能力较好，但理论知识和教育教学技能欠缺。由这些高等院校应届毕业生教授理论课，老师傅进行实操指导，往往造成理论和实操之间未能很好衔接，从而影响培养质量。\r\n2.师资队伍结构不合理。专任教师职务结构比例中，高级职称教师偏少，专业带头人、骨干教师缺乏。教师队伍中严重缺乏既熟悉理论教学又能胜任实训课教学的骨干，特别是许多来自学校的教师，缺乏企业工作经验，对生产工艺流程不熟悉，上课只能照搬资料，难以胜任专业课程的教学工作。  \r\n3.一体化教师的比例低于学校实际需求，且内涵要求偏低。由于近几年学校扩招，学生数量猛增，导致学校一体化教师缺乏；此外学校对一体化教师的内涵要求还未能深化到企业实际生产经验的取得与积累上。\r\n4.培训经费保障乏力。缺少师资队伍培训专项资金，培训设施设备、场地等条件难以保证，补贴得不到保障，教师参与培训的积极性受到抑制，导致培训政策成为“空头支票”。\r\n（三）预期效益及持久性分析\r\n1.构建“一体两翼”强师队伍\r\n通过省技工教育强师专项资金教师资助项目建设，以点带面，学校将建设一支能满足学校教学改革与发展需要的、高水平的专兼职教师队伍，造就一批基础理论扎实、教学实践能力突出、专业眼光敏锐的专业带头人和教学骨干，建成由企业专家、技术骨干、能工巧匠组成的高水平外聘教师人才库，形成由行业企业一线技术人员兼职讲授实践技能课程的机制，构建专业带头人为“头”，双师型教师为“体”，骨干教师和兼职教师为“翼”的“一体两翼”强师队伍。\r\n2.更好为我省技工教育的发展提供支持\r\n作为国家级职业培训师资培训基地、全国技工院校师资培训基地，学校建设一支高水平的专职教师队伍，造就一批基础理论扎实、教学实践能力突出的专业带头人和教学骨干，不仅能促进我校整体办学实力和办学水平的提高，也能更好为我省技工教育发展提供支持，作出贡献，发挥长久效益。\r\n五、项目可行性\r\n（一）项目基础\r\n学校制定师资队伍培养相关的制度，如《加快高技能师资队伍建设实施办法》、《专业带头人评定制度》、《教师综合考核办法》、《十佳教师的评选实施办法》等，有效保证了优秀教师在思想品德、职业素养、教育观念、教育教学能力和科研能力等方面脱颖而出，在引进的同时，学校加大现有人才的培养力度，相继制定了《教科研及优秀人才奖励办法》等文件，鼓励教师提高技能水平，对获得各级各类技术能手的教师进行奖励，鼓励教师学历和技能水平提升，对提升学历和技能等级的教师的给予资助。针对年青教师比例大、实践经历少的特点，制定《“以老带新”制度》，加大对青年教师的继续培养，选派优秀青年教师外出培训、出国进修。制定《广东省技师学院教师到企业实践培训的规定》，分批选调各青年教师到市内大中型企业进行实践锻炼，提升其实践教学能力，以加强实践性教学环节，提高应用型人才培养的质量。\r\n（二）预算方案的合理性\r\n省技工教育强师专项资金预算使用情况详见各教师资助项目资金预算表。其资金主要用于：\r\n1.进一步提升教师教育教学水平。通过学习先进的职教理念和教育教学方法，培养教师综合职业能力，开拓教师的眼界，全面提高教师作为专业带头人的能力和素养，实现引领学校计算机网络技术专业发展的目标。 \r\n2.进一步提升教师专业能力和技能水平。通过下企业实践，参加专业学习和高技能培训，掌握本专业新知识、新技术，将新技术、新技能传递给青年教师，并引入到学校教学课堂中，培养符合企业需要的高技能人才。\r\n3.进一步提升教师教研科研能力。通过参加培训学习、技术交流、开展课题研究、编写教材论文等工作，不断解决教学中存在的教育教学问题，找出解决方案，为教育教学提供服务。\r\n4.帮助其他教师提升能力素质。成立以资助人为负责人的网站设计大师工作室，密切联系相关企业，带领青年教师开展各种技术交流、技术研究活动，培训学生参加技能竞赛，邀请专家开展技术讲座，帮助本专业教师提升专业能力。\r\n（三）主要工作思路及设想\r\n1.师资培训途径\r\n（1）请进来\r\n请教学专家：请相关职业高校、职业研究所专家对全校教师进行通用能力培训。请企业专家：请相关企业专家对教师进行本专业新技术、新工艺专业知识培训。请世赛专家：请世赛相关项目专家对我校重点参赛项目进行指导、对教练、骨干教师进行培训。\r\n（2）走出去\r\n校企交流：定期选送专业教师到相关企业、社会进行生产实践，学习企业的新技术、新工艺、企业管理措施等，丰富实践经验，提高教学、生产、实习的指导能力。校际交流：不定期派专业教师到办学理念先进、办学质量高的、办学效益好的同类学校交流学习。国际交流：为学习国际化的教学理念，学院将每年派送一定数量的专业带头人、骨干教师参与到主管部门组织的出国师资培训。旨在进一步了解国际相关学科专业建设和教学科研发展情况，学习借鉴国外同类学校先进的办学理念和管理运行机制，为专业带头人、骨干教师创造国际学习交流条件，开拓专业带头人、骨干教师视野。并充分与主管部门沟通。\r\n 2.师资培训具体规划\r\n我校师资培训具体规划将重点开展“十百千”工程，即开展十项专题活动以提升教师的教育教学能力；派百位教师下厂实践，送百位教师参加专业能力培训，聘百人次行业专家任教、讲座以提升教师的专业技能水平；完成每年千人次师资培训任务以完善教师的知识结构。“十百千”工程将大幅提高教师的德育工作能力、专业教学能力、教学研究能力、实训指导能力。\r\n表1  开展十项专项活动计划表\r\n序号内容措施要求负责部门1提高教师的德育工作能力学校召开一年一度德育工作研讨会（1）全校所有班主任参加德育工作研讨会，与会成员交流德育工作心得；（2）评选德育工作典型案例党办、学生处、各系学生科2开展“三爱”活动营造“三爱教育”氛围党办、校办3提高教师的专业教学能力教师教学基本功竞赛全校教师参加教学基本功竞赛的选拔，各系推荐参加学校组织的决赛，提高教师的说、写能力各系\r\n教务处4工学一体化课程开发与实施培训活动邀请职业院校或职教研究所专家对全校所有专业带头人、骨干教师进行培训教务处5基于工作过程的行动导向教学法培训邀请职业院校或职教研究所专家对全校所有专职教师进行培训教务处6工学一体化教学观摩课四个示范专业带头人、骨干教师各展示一堂高水平示范课供其他教师观摩系、教务处7新教师汇报课学校组织全体来校工作不满一年教师参与汇报课活动，并评奖教务处8提高教师的教学研究能力工学一体化教学论文评选活动全体教师参加该活动，各系初选、学校终选系、教务处9提高教师实训指导能力教师到企业实践活动每年选派教师到与专业相关企业实践、培训系、教务处10提高教师职业生涯规划能力教师职业生涯规划专题讲座邀请职业院校或职教研究所专家对全校所有教师进行职业生涯规划培训教务处3.师资培训保障措施\r\n（1）成立师资培训领导小组\r\n成立以校长为领导小组组长，书记为副组长的师资培训领导小组，为全校师资培训工作保驾护航，全校领导层形成一种合力，全力支持师资培训。\r\n（2）弘扬办学传统，加强教师职业道德培训\r\n——把“崇德尚技，博学精工”的我校精神和优良传统作为师德教育的重要内容，贯穿在教师管理、培养的各个环节，贯穿在教师成长发展的各个阶段，引导广大教师继承扎根技工教育，自觉融入学校建设全国一流、全国高水平技工院校的宏伟事业。\r\n——制定《广东省高级技工学校教风建设实施方案》，突出对全体教师“奉公守法、爱岗敬业、严谨治学、尊重学生、为人师表、廉洁从教、团结协作”等方面的职业道德要求，引导广大教师树立正确的职业理想，模范遵守职业道德规范，自觉履行教书育人的神圣职责。\r\n——加强教师业务培训。建立教师进修学习与日常培训、新聘期培训相结合的专业成长促进机制，引导广大教师自觉更新知识结构和教育理念，主动把握学科发展动态，主动进行科学研究和教学方法创新，以高水平的教学研究支撑高水平的教学。强化对新上岗教师的岗前培训，使他们熟悉学校的发展历史和发展定位，熟悉岗位职责和相关管理制度，缩短适应期。\r\n（3）构建激励约束机制\r\n——建立双师型教师平台汇聚和培养人才、优化资源配置。学校通过制定双师型教师的评定制定，鼓励教师参加评定，学校通过双师型教师评定专家委员会对参评教师进行资料的审核，技能的考核，资格的认定，确定双师型教师人选。双师型教师，采用工资加双师型人才津贴的二元结构工资制度。\r\n——创新教师业绩评价体系，进一步完善校内津贴分配制度。坚持分类指导原则，按照不同教师岗位类型、不同学科类型、不同专业类型，分类设计岗位职责和业绩评价指标，确定相应的校内津贴发放标准；突出教师创造性业绩的权重，加大对高水平科研成果、获奖和应用性成果、技能竞赛的奖励力度。\r\n——充分发挥职称评聘的杠杆作用，按“科学评价为基础、岗位需要为前提、聘约管理为手段”的原则，激励教师努力钻研业务知识，提高教育教学和科学研究能力。\r\n六、资金绩效目标及绩效表\r\n（一）提升专业能力\r\n通过派资助对象到国内外参加专业培训、进修。学习掌握新的专业知识与技术，同时参加企业实践，学习掌握专业领域的新工艺、新材料知识，不断提高实践教学指导能力。\r\n（二）提升教科研能力\r\n以资助对象为组长，成立课程改革课题小组，开展人才需求调研、工作岗位调研、制定人才培养方案、人才培养课程体系工作，通过课题建设培养具有专业能力，具有教科研能力的专业带头人；通过撰写专业论文，提升自己专业理论水平；通过与企业开展技术攻关，为企业提供技术服务、解决企业技术难题，提升自己科研水平。\r\n（三）提升专业教学能力\r\n通过参加教学方法培训、一体化课程构建与实施培训、微格培训、教学实训基本技能和信息化教学培训，提高被资助人的专业教学能力。\r\n（四）提升职业生涯规划能力\r\n通过参加职业生涯规划培训、职业指导培训，提高被资助人的职业生涯规划能力，并指导其他教师提升职业生涯规划能力。\r\n（五）提升德育教育工作能力\r\n通过参加德育培训，提高被资助人的德育教育工作能力，在实际工作中践行“爱岗敬业、爱校如家、爱生如子”。\r\n（六）提升教学教研管理能力\r\n通过参加管理培训，提高被资助人的教科研管理工作能力，在工作中践行精细化、高效管理\r\n（七）承接师资培训\r\n以资助对象为组长，成立专业培训团队，利用现有学校实训室平台，对学校教师开展专业新技术、新工艺技术培训，帮助其他教师提升能力素质。\r\n省级基础教育师资培训经费教师资助 项目绩效目标表预期产出产出计划1.提升个人自身能力素质\r\n2.帮助其他教师提升能力素质总目标：投资25万，在一年建设期内，通过资助五位教师提升个人自身能力素质，帮助其他教师提升能力素质，产生辐射效应，全面提高师资队伍素质；教师综合能力提升资料年度阶段性目标：2016年项目完成率100%，培训教师参培率100%，把资助的5位教师培养成为本专业的专业带头人或骨干教师效率计划 项目实施进度计划项目实施内容开始时间完成时间实施计划、实施过程材料、项目总结材料1.项目启动2017年1月2017年2月2.项目实施2017年2月2017年12月3.项目总结2017年12月2017年12月预期效果预期社会经济效益指标类别个性化指标上年度实际水平本年度计划完成水平指标解释及计算公式说明发表论文、举办培训过程资料社会效益发表论文提升率23发表3篇有影响力的学术论文反映项目实施直接产生的社会、经济、生态效益等，根据项目属性特点，可选择其中一或多项效益，研究设置个性化指标及其目标值。培养新教师811完成11位新教师的培养任务培养世国家集训队赛选手5≥5培养更多选手进入世赛国家集训队校企合作完成技术革新或改造一项12审核意见省级主管部门审核意见\u000B                      审核人：    单位公章       年  月  日第三方机构审核意见\u000B                        审核人：    单位公章       年  月  日省财政厅审核意见\u000B                         审核人：    单位公章       年  月  日注：各申报单位个性化指标可自行根据项目特点设置指标，指标设置应可考核、可量化，能够与项目事后绩效评价相对接。 经济效益和生态效益确实无法设置指标的，可不设置。七、资金预算书\r\n表2  项目资金预算及考核指标\r\n项目\u000B名称建设内容具体项目专项资金预算(万元)考核指标杨文杰老师教师资助项目提升专业能力参加数控维修技术相关专业技能培训2.01.参加专业技能培训学习总结1份；\r\n2.参加企业生产实践证明材料1份；\r\n3.购买书籍、资料及相关软件。专业相关企业参加生产实践学习专业目前新知识、新技术提升教科研能力参加教研交流和学习1.81.参加教研交流学习总结1份；\r\n2.发表学术论文1篇；\r\n3.聘请行业专家证明材料一份。聘请全国技能大赛数控维修项目教练，指导培训参赛选手。发表专业论文1篇聘请世赛行业专家指导交流\r\n指导培训参赛选手提升其他教师能力开展全校或全系范围数控维修学术讲座1.21.学术讲座过程资料1套；\r\n2.带领新教师证明材料1份；\r\n3.专家交流讲座过程资料1套。带领指导本专业新教师1名聘请行业专家来校交流、讲座小计5黄磊老师教师资助项目提升自身专业技能能力参加计算机网络技术相关专业技能培训2.61.参加专业技能培训学习总结1份；\r\n2.参加企业生产实践证明材料1份；\r\n3.购买书籍、资料及相关软件。下与专业相关企业参加生产实践学习专业目前新知识、新技术资料、图书费提升教师本人教研科研能力参加教研交流和学习0.31.参加教研交流学习总结1份。\r\n提升教师本人德育、教学教研管理能力参加德育、教学管理培训0.41.培训结业证书提升其他教师能力开展全校或全系范围计算机网络技术学术讲座1.71.学术讲座过程资料1套；\r\n2.带领新教师证明材料1份；\r\n3.专家交流讲座过程资料1套。带领指导本专业新教师3名聘请行业专家来校交流、讲座小计5温锦文老师教师资助项目提升理论教学能力高校学习、进修；\r\n企业学习与实践3.61.学习结业证明；\r\n2.现场照片及专家资料；\r\n3.专业团队教师、选手花名册。邀请专家教授对水性漆专业团队进行培训邀请世赛专家到校对参赛选手水性漆项目进行指导承接师资培训任务开展师资培训(培养8名骨干教师)1.01.师资培训名册；                       2.培训讲义、PPT；                                 3.师资培训计划。企业、行业调研企业行业调研，了解企业需求0.41.企业评价                 2.企业调查表小计5张小清教师资助项目提升专业能力购买书籍、资料0.61.订阅获购买教学书籍、杂志；\r\n2、培训结业证书。教学方法培训教师职业能力培训提升教科研能力参与主持精密测量专业建设11．专业建设相关资料；              2。专业研讨相关资料；\r\n3．教材资料；\r\n4.发表论文1篇。                  参与并组织精密测量专业教学课题研讨与开发参与并组织精密测量一体化校编教材编写论文撰写提升专业技术及实践培训能力参加精密检测新方法、新技术、新工艺、新标准培训21．培训结业证书；\r\n2．培训方案相关资料；\r\n3．调研与交流相关资料。参加精密测量高级应用培训研究精密测量技术培训方案专业调研及与同行交流提升德育教育工作能力参加德育教育工作培训0.21.培训结业证书。帮助提升其他教师能力参与并组织听专家讲座、参加专业培训1.21．提供学习培训相关资料；\r\n2．提供参观学习相关资料；\r\n3．提供开展培训及竞赛相关资料。组织教师到知名企业、学校参观学习开展精密检测技术相关培训工作指导教师和学生参加竞赛活动小计5王怀术教师资助项目提升专业能力\r\n高等院校学习、进修1.51.学习结业证明；\r\n2.企业实践15天以上过程资料。企业学习与实践提升专业教学及培训能力教学方法培训11.培训结业证书；\r\n2.订阅获购买教学书籍、杂志；\r\n3．校本教材。一体化课程构建与实施培训购买书籍、资料编写一体化教材（校本）提升职业生涯规划能力\r\n参加专业能力师资培训0.51.培训结业证书。提升教科研能力\r\n主持物流管理专业建设11.发表论文1篇以上；              2.专业建设相关资料； \r\n3.攻关课题资料。与企业开展横向课题研究发表论文承接师资培训任务举办培训班11.举办培训班1次以上，提供开展培训相关资料。\r\n开展校内专业培训活动请专家讲座小计5合计25八、佐证材料\r\n1. 杨文杰教师资助项目申请报告及资历附件；\r\n2. 黄磊教师资助项目申请报告及资历附件；\r\n3. 温锦文教师资助项目申请报告及资历附件；\r\n4. 张小清教师资助项目申请报告及资历附件；\r\n5. 王怀术教师资助项目申请报告及资历附件。\r\n广东省高级技工学校\r\n2016年11月\f省级基础教育师资培训经费\r\n杨文杰教师资助项目\r\n申\r\n报\r\n材\r\n料\r\n省级基础教育师资培训经费专项资金\r\n杨文杰教师资助项目申请报告\r\n一、学校简介\r\n广东省技师学院是广东省人民政府主办，直属广东省人力资源和社会保障厅的副厅级公办的国家级重点技工院校。 现有占地面积335亩，拥有博罗校本部和广州校区两个教学区，建筑面积20万平方米，全日制在册学生14526人，现有11个教学系，共开设65个专业，其中高级工以上专业40个，职业技能鉴定工种44个，年培训量4.7万人次，年鉴定量2.1万多人次。建有院内专业实训教室148间，技能大师工作室16间，是广东省历史最长、规模最大、综合实力最强的国家级重点技工院校。 \r\n学院有高级职称教师139人，双师型教师428人（占教师比例94.9%），其中有1位获全国五一劳动奖章、3位获国务院特殊津贴、6位获全国技术能手、3位全国优秀（模范）教师、1位获全国高技能人才培育突出贡献奖、2位获广东五一劳动奖章、29位获广东省技术能手。近几年，学院获国家级职业技能大赛奖4项，专利16项，获省级职业技能大赛奖22项，正式出版教材54本，公开发表论文293篇，教研成果获奖161个，获第43届世界技能大赛电子技术项目全国唯一参赛资格，荣获第43届世界技能大赛电子技术项目优胜奖。\r\n杨文杰老师是我校数控技术系老师，学历本科，维修电工高级技师、电工工艺一级实习指导教师。工作以来，先后获得南粤优秀教师、博罗县优秀教师、广东省数控装调维修竞赛优秀教练、学校十佳教师等称号。除此以外，该教师还担任了全国数控维修大赛教练工作，培养的选手获广东省职工组第一名、高技组第一名、中职组第一名,选手获广东省技术能手，广东省“五一劳动奖章”。\r\n二、项目概况\r\n项目名称：省级基础教育师资培训经费杨文杰教师资助项目\r\n项目内容：结合广东省高级技工学校师资与学校专业建设现状，提升师资队伍建设，资助数控技术系骨干教师杨文杰完成师资培训任务。\r\n主要任务：资助杨文杰教师通过参加相关专业技能培训班、下厂生产实践、教研交流、参加教学管理培训、学术讲座，发表专业论文，带领新教师，参加行业专家交流会，学习专业目前的新知识与新技能，提升杨文杰教师自身专业技能能力、教研科研能力，指导和带动本专业其他教师的成长并并提高全国赛数控维修项目及世赛相关项目成绩。\r\n预期目标：打造一支师德高尚、业务精湛、结构合理、充满活力的高素质专业化教师队伍，将资助对象培养成为一个思想品德高尚、职业素养齐备、教学水平高超、技术水平先进、专业技能精通、教研能力突出的具有现代职教理念、广阔职教视野、能引领我校数控维修专业发展的专业名师。\r\n投资规模：项目总建设预算资金5万元，项目完成时间为一年，并明确资金使用目标、考核指标。\r\n三、项目基本情况表\r\n省级基础教育师资培训经费教师资助项目基本情况表    市（财政省直管理县）财政局（盖章）           市（财政省直管理县）人力资源社会保障局（盖章）项目名称杨文杰教师资助项目项目依据立项情况正在办理立项前准备工作《关于做好2017年度就业及技工教育专项资金（技工院校及技能实训基地建设方向）项目库入库项目申报工作的预通知》【粤人社函〔2016〕2020号】。投资总额（万元）5投资结构（万元）项目简介基础建设0资助杨文杰教师完成师资培训，参加专业培训，购买书籍，下厂实践，参加教研交流、发表学术论文，参加教学管理培训，聘请国、世赛专家，带领提升新教师。设置购置及\u000B信息化建设0教学改革5筹资方案（万元）0已落实资金0申报省级资金5项目情况绩效目标起始时间（年月）2017年1月参加专业培训1次、下厂实践1次、发表论文1篇、参加教研交流1次、带领年轻教师1名。终止时间（年月）2017年12月项目存续状态延续项目申报单位：广东省高级技工学校       填报人：成百辆       手机：13068268627\r\n项目负责人：夏  青       手机：18928389979注：1.“立项情况”指向发改部门提交立项的情况，填写：无需立项、正在办理立项前准备工作、项目建议书已批复、可行性研究报告已批复、已完成所有立项手续。\u000B    2.“项目依据”填写支持项目申报的国家、省、市、县出台的相关政策文件依据及相关文号。\u000B    3.“项目存续状态”填写：延续项目或新增项目。延续项目指上一年度曾申报并获得省级补助资金，本次继续申报的同一项目；新增项目指新申报的项目。\r\n四、项目的必要性\r\n（一）区域经济转型升级需要数控维修专业教学强师\r\n数控机床维修与先进制造技术相辅相成，先进制造技术是国防现代化的重要战略资源；是关系到国家战略地位和体现国家综合国力水平的重要基础性产业，尤其中国正在逐步变成“世界制造中心”。为了增强竞争能力，制造企业已开始广泛使用先进的数控机床。据统计，目前我国数控机床机床维修工短缺。数控机床维修人才尤其是先进数控机床维修方面的人才紧缺,也引起教育部、劳动与社会保障部等政府部门的高度重视。“月薪6000难聘数控维修高级技工”、“花重金买来的先进数控制造设备一旦出现故障需请厂家人员花大额维修费”已成为企业普遍关注的热点问题。在广东，随着广东产业转型升级的进一步发展，高端制造的市场份额将逐步增大，先进机床需求逐步增大，对机床维护方面人才的需求呈逐年上升趋势。但在数控机床维修技术方面的人才还远远不够，归根结底还是尚未形成数控机床维修技术专业人才培养体系，相关教师的层次和数量远远不够。\r\n（二）学校发展需要数控维修类专业教学强师\r\n一个企业和一个学校要想有一个好的发展前景，能在激烈的竞争 中立于不败之地，企业和学校就必须不断提高核心竞争力。我校秉承打造一流技工学校，为社会及企业输送高素质、高技能的技工学子，以助解决我国在经济转型发展中所遇到的瓶颈问题。而前提条件是必须保证我校师资队伍足够雄厚。数控技术是飞速发展的行业，目前数控技术系数控维修专业教师缺乏对新知识，新技术掌握，难以跟上时代的步伐，因此对专业教师进行培训、提高专业技能是势在必行。\r\n我校数控技术系成立了全国技能大赛数控机床装调与维修项目广东选拔赛备战组，为能更加科学和系统的选拔输入人才，杨文杰老师作为该项目的主要负责人，更需要对数控维修技术专业的知识有更深层次的掌握，才能使训练工作事半功倍。\r\n通过省级基础教育师资培训经费教师资助项目，加强学校数控技术系数控维修技术专业师资队伍的建设，促进专业内涵发展，通过培养教学强师，以做到一帮一、传帮带的良性发展。\r\n五、项目可行性\r\n（一）受助对象本人符合项目要求\r\n1、资助人杨文杰符合省级基础教育师资培训经费教师资助项目资助对象的条件，是根据广东省高级技工学校数控维修专业建设的实际需求确定的资助人员。\r\n2、资助人杨文杰使用资助资金的建设项目目标明确，内容具体，联系教育教学实际，具有良好的可操作性，能有效促进教师在教学能力、技术能力、教研能力等方面得到全面提升。\r\n3、省级基础教育师资培训经费教师资助项目将以培养教师教学强师为目标，并以指导和带动其他专业教师在专业水平、职业素养上得到提升。\r\n杨文杰老师个人基本情况及主要工作业绩如下：\r\n受助对象杨文杰,广东博罗县人,2006年毕业于广东省高级技工学校，2006年被学校聘为实习指导教师，2013年获得函授本科学历，同时具备维修电工高级技师、电工工艺一级实习指导教师。\r\n在思想政治方面，该同志忠诚党的教育事业，始终具有明确的政治目标，主动加强思想政治及教育理论学习，不断提高自身理论素质和教学水平，在工作中始终坚持党的基本路线，坚持党的四项基本原则，积极实践“三个代表”，贯彻执行科学发展观，践行十八大会议精神，关心国内国际职业教育的发展动态，注意自身知识更新。\r\n参加工作十年来，始终兢兢业业，任劳任怨，虚心好学，无私奉献，在技工教育的工作岗位上做出了不平凡的业绩。由于成绩突出，先后获得南粤优秀教师、博罗县优秀教师、广东省数控装调维修竞赛优秀教练、学校十佳教师等称号。\r\n除了做好常规的教学工作以外，还担任了全国数控维修大赛教练工作，培养的选手获广东省职工组第一名、高技组第一名、中职组第一名,选手获广东省技术能手，广东省“五一劳动奖章”。 2012年7月作为主教练指导学生参加 “第四届全国技工院校技能大赛广东选拔赛”，荣获数控机床装调维修工个人第五名、团体优秀奖；2012年设计的“多功能教学型数控滑台”参加年度优秀科研成果评比获一等奖；2013年3月，被学校聘为维修电工工种三级双师型“一体化”教师；2013年，被任大师负责成立了“数控机床维修大师工作室”，2014年1月，被学校聘为数控设备应用与维修专业“骨干教师”。 2014年8月，被广东省高级技工学校评为“优秀教师”；2014年度工作评比被学校评为“先进个人”。2014年被评为学校“十佳教师”。 2015年在广东省技师学院第一届科研技能月活动中被学校评为“优秀指导教师”。也担任了惠州德赛电池有限公司员工培训的部分课程，以及校企合作东风日产保全人员培训工作。任班主任工作3年，期间学生操行优良率95%，差生转化率97% 。\r\n个人独立撰写论文《PLC在离子风刀设备改造中的应用》发表于《机电工程技术》2015年7月，论文《基于PLC的水位分歧管分装工位自动化改善》发表于《机电信息》2015年7月，论文《机电一体化人才快速培养教学设备设计》发表于《机电工程技术》2014年6月；2013年合作编写了国家中职示范校建设“校企合作、工学结合”改革教材《数控系统连接、调试与维修》。\r\n（二）受助对象可依托学校实施强师项目\r\n广东省技师学院于2002年升格为技师学校，成为我省发展较快、规模较大、综合实力较强的国家级重点技工院校之一，全日制在校生规模5000人以上，学校占地335亩；总建筑面积20.3万平方米，有教室199间，多媒体教学设备配备率达100%，实训场地 93个，多媒体配置率达91.35%，实训场地、设备总资产达1.2亿元。广东省高级技工学校于2003年就开设了数控维修专业的中级工班，是广东省技工学校中最早开设数控维修专业的，经过十多年的建设和发展，到2016年已累计为社会培养数控维修专业中高级技能人才2000余人。现我校数控专业在校生有1000多人，其中中级工300余人，高级工700余人。\r\n数控技术系有教职工50人，其中高级职称及以上11人，中级职称24人，技师以上职业资格有45人，其中高级技师34人，全国“五一”劳动奖章获得者2人,教师中享受国务院特殊津贴的有2人，全国技术能手3人，广东省数控大赛冠军6人。\r\n数控技术系有数控加工和数控维修两个实训基地。其中，数控维修专业基地包括：数控车床系统维修实训区、数控铣床系统维修实训区、数控机床故障检测维修实训区、电工基础实训室2间、液压\\气压实训室1间、传感器实训室1间、PLC与变频器实训室2间、机床机械装调实训区。\r\n综上，虽然现有的师资力量和实习场地基本能够满足目前的教学要求，但随着专业的进一步发展，数控维修方面的人才明显不足。\r\n为了适应现代制造业的发展，需加大学校师资队伍建设，通过这次项目实施大大提高我院的师资水平，即本项目在此可行。\r\n六、资金绩效目标表\r\n省级基础教育师资培训经费教师资助项目绩效目标表预期产出产出计划三项总目标：（提升杨文杰教师专业能力、教研科研能力、帮助提升其他教师，成为专业带头人。）过程资料年度阶段性目标：2017年1月至2017年12月完成专业培训计划提升自身专业能力、2017年6月至2017年9月完成学术论文发表提升教研科研能力、2017年1月到2017年12月完成带领新教师1名以及提升其他教师。效率计划 项目实施进度计划项目实施内容开始时间完成时间培训、发表论文、以老带新过程资料1. 提升教师本人专业技能能力2017年1月2017年12月2. 提升教师本人教研科研能力2017年6月2017年9月3. 提升其他教师能力2017年1月2017年12月预期效果预期社会经济效益指标类别个性化指标上年度实际水平本年度计划完成水平指标解释及计算公式说明培训、下厂实践、以老带新证明材料社会效益培训计划率0%100%完成专业技能培训1次反映项目实施直接产生的社会、经济、生态效益等，根据项目属性特点，可选择其中一或多项效益，研究设置个性化指标及其目标值。下企业实践率0%100%完成下企业实践1次提升年轻教师率0%100%提升1名年轻教师能力审核意见省级主管部门审核意见\u000B                      审核人：    单位公章       年  月  日第三方机构审核意见\u000B                        审核人：    单位公章       年  月  日省财政厅审核意见\u000B                         审核人：    单位公章       年  月  日注：各申报单位个性化指标可自行根据项目特点设置指标，指标设置应可考核、可量化，能够与项目事后绩效评价相对接。 经济效益和生态效益确实无法设置指标的，可不设置。七、资金预算书\r\n省级基础教育师资培训经费杨文杰教师资助项目资金预算表及考核指标\r\n项目\u000B名称建设内容具体项目专项资金预算(万元)考核指标杨文杰老师教师资助项目提升教师专业技能能力参加数控维修技术相关专业技能培训1参加专业技能培训学习总结1份；\r\n参加企业生产实践证明材料1份；\r\n购买书籍、资料及相关软件。下与专业相关企业参加生产实践0.4学习专业目前新知识、新技术0.4资料、图书费0.2提升教师教科研能力、管理能力参加教研交流和学习0.2参加教研交流学习总结1份；\r\n发表学术论文1篇；\r\n聘请行业专家证明材料1份。聘请全国技能大赛数控维修项目专家指导培训参赛选手0.6发表专业论文1篇0.2聘请世赛行业专家指导培训参赛选手0.8提升其他教师能力开展全校或全系范围数控维修学术讲座0.2学术讲座过程资料1套；\r\n带领新教师证明材料1份；\r\n专家交流讲座过程资料1套。带领指导本专业新教师1名0.4聘请行业专家来校交流、讲座0.6合计5八、主要佐证材料\r\n杨文杰教师资历一览表\r\n序号证书1毕业证2职称证书3技能等级证书资历证明\r\n图1 毕业证书\r\n\u0001\u000B图2 专业职称证书\r\n图3 技能等级证书\r\n杨文杰教师荣誉及教科研成果一览表\r\n序号年度奖项备注12015南粤优秀教师广东省人力资源和社会保障厅22015博罗县优秀教师博罗县教育局32015十佳教师广东省技师学院42015数控维修项目广东省优秀教练广东省职业技能大赛组委会52015广东省技师学院第一届科研技能月活动评为“优秀指导教师”广东省技师学院62014-2015优 秀 教 师广东省技师学院72013-2014优 秀 教 师广东省技师学院820122012年度优秀科研成果一等奖广东省职业培训和技工教育协会92011参加全国第九届技工院校教学考研技术开发优秀成果评审三等奖中国职工教育和职业培训协会102011先 进 个 人广东省技师学院112010先 进 个 人广东省技师学院122014论文：《线圈自动下料机机械机构设计》2014.2 《机电信息》132014论文：《机电一体化人才快速培养教学设备设计》2014.6《机电工程技术》142015论文：《基于PLC的水位分歧管分装工位自动化改善》2015.7《机电信息》152015论文：《PLC在离子风刀设备改造中的应用》2015.7《机电工程技术》162015论文：《实施“三引”策略，共筑“四赢”模式》2015.5《广东技工教育研究》172013教材：《数控系统连接、调试与维修》2013.12国家中职示范校校本教材荣誉及教科研成果证明\r\n图5 南粤优秀教师证书\r\n图6博罗县优秀教师证书\r\n图7 十佳教师证书\r\n图8 广东省优秀教练证书\r\n图9第一届科研技能月活动评为“优秀指导教师”证书\r\n图10优秀教师荣誉证书\r\n图11优秀教师荣誉证书\r\n图12 2012年度优秀科研成果一等奖证书\r\n图13第九届技工院校教学考研技术开发优秀成果评审三等奖证书\r\n图14先进个人证书\r\n图15先进个人证书\r\n图16教材：《数控系统连接、调试与维修》\r\n图17论文：《线圈自动下料机机械机构设计》\r\n图18论文：《机电一体化人才快速培养教学设备设计》\r\n图19论文：《基于PLC的水位分歧管分装工位自动化改善》\r\n图20论文：《PLC在离子风刀设备改造中的应用》\r\n图21论文：《实施“三引”策略，共筑“四赢”模式》\r\n广东省技师学院\r\n二0一六年十一月\r\n省级基础教育师资培训经费\r\n黄磊教师资助项目\r\n申\r\n报\r\n材\r\n料\f省级基础教育师资培训经费专项资金\r\n黄磊教师资助项目申请报告\r\n一、学校简介\r\n广东省高级技工学校于2002年升格为我省技师学校，是国家中等职业教育改革发展示范校、国家级高技能人才培训基地、国家电子技术项目世赛集训基地、全国技工院校师资培训基地、人社部“工学结合一体化”教学试点单位、全国数控设备维修专业师资培训中心、全国优秀职业技能鉴定所、团中央青年就业创业见习基地、广东省“校企双制”办学试点单位、广东省技工院校师资培训中心。\r\n学校占地335亩，总建筑面积20.3万平方米，实训场地、设备总资产达1.2亿元，主要开设有数控技术、工业设计、机械制造、汽车工程、电气工程、信息技术、质量技术、现代服务、经济贸易9大专业群65个专业，其中高级工以上专业40个，开设44个工种的职业技能鉴定。年招收全日制在校生近5000人，有注册全日制在校生近14000人，毕业生“双证书”率达100%，初次就业率达99.8%，专业对口率达90.32%。学校有教职工700余人，其本科以上学历教师占专任教师的97.2%达438人，高级职称教师占专任教师的30.8%达139人，一体化教师占专任教师的95%达428人。\r\n黄磊老师现任广东省高级技工学校信息技术系计算机综合科科长，科内专职教师18名。2012.6-2014.6期间，完成国家中职示范校计算机网络技术专业建设项目，并通过专家组验收。科内教师在政治上严格要求自己，业务上刻苦钻研，爱岗敬业，认真服从学校的各项工作安排，工作积极、负责、任劳任怨，在教研科研能力上大胆改革，勇于创新，取得了不错的成绩。指导的学生在第44届世界技能大赛网站设计项目广东选拔赛上，获得全省第三名；世界技能大赛网络管理项目广东选拔赛中获得全省第二名和第四名。\r\n二、项目概况\r\n项目名称：省级基础教育师资培训经费黄磊教师资助项目\r\n项目内容：结合广东省高级技工学校师资与学校专业建设现状，提升师资队伍建设，资助信息技术系骨干教师黄磊完成师资培训任务。\r\n主要任务：资助黄磊教师通过参加相关专业技能培训班、下厂生产实践、教研交流、参加德育、教学管理培训、学术讲座，带领新教师，参加行业专家交流会，学习专业目前的新知识与新技能，提升黄磊教师自身专业技能能力、教研科研能力，指导和带动本专业其他教师的成长并提高世赛网站设计、网络管理项目选拔赛成绩。\r\n预期目标：打造一支师德高尚、业务精湛、结构合理、充满活力的高素质专业化教师队伍，将资助对象培养成为一个思想品德高尚、职业素养齐备、教学水平高超、技术水平先进、专业技能精通、教研能力突出的具有现代职教理念、广阔职教视野、能引领我校计算机网络专业发展的专业名师。\r\n投资规模：项目总建设预算资金5万元，项目完成时间为一年，并明确资金使用目标、考核指标。\r\n三、项目基本情况表\r\n省级基础教育师资培训经费教师资助项目基本情况表    市（财政省直管理县）财政局（盖章）           市（财政省直管理县）人力资源社会保障局（盖章）项目名称黄磊教师资助项目项目依据立项情况正在办理立项前准备工作《关于做好2017年度就业及技工教育专项资金（技工院校及技能实训基地建设方向）项目库入库项目申报工作的预通知》【粤人社函〔2016〕2020号】。投资总额（万元）5投资结构（万元）项目简介基础建设0资助黄磊教师完成师资培训，参加专业培训、购买书籍、下厂实践、参加教研交流、参加德育、教学管理培训、带领提升新教师。设置购置及\u000B信息化建设0教学改革5筹资方案（万元）0已落实资金0申报省级资金5项目情况绩效目标起始时间（年月）2017年1月参加专业培训1次、下厂实践1次、参加教研交流1次、带领年轻教师3名。终止时间（年月）2017年12月项目存续状态延续项目申报单位：广东省高级技工学校        填报人：成百辆          手机： 13068268627                                                                               \r\n                                项目负责人： 夏青          手机：18928389979四、项目的必要性\r\n（一）区域经济转型升级需要计算网络专业教学强师\r\n区域经济转型升级具有高起点、高标准、高品位特点，目前信息化技术穷出不尽及高技能人才的严重短缺，已成为我国经济转型升级的瓶颈，只有大力发展技工教育，坚持教育创新，打造前端的集技能与理论一身的高技能高素质教师队伍才能从根本上解决发展瓶颈。\r\n信息产业体现着最先进的科学技术发展水平，根据CCID的权威调查与统计，目前我国使用网络用户总数直线上升，越来越多的高新技术企业依托计算机网络从事应用开发和系统集成，计算机网络技术具有极为广阔的发展前景和广泛的就业前景，培养计算网络专业高技能人才已成为客观需要，面临高技能人才短缺问题我们必需打造一支结构合理，技能及理论水平高超的技工教育名师队伍，为企业培养输送优秀并且有高技能的技术工人。\r\n（二）学校发展需要计算机网络类专业教学强师\r\n一个企业和一个学校要想有一个好的发展前景，能在激烈的竞争 中立于不败之地，企业和学校就必须不断提高核心竞争力。我校秉承打造一流技工学校，为社会及企业输送高素质、高技能的技工学子，以助解决我国在经济转型发展中所遇到的瓶颈问题。而前提条件是必须保证我校师资队伍足够雄厚。\r\n计算机网络技术是飞速发展的行业，目前信息技术系计算机网络技术专业教师缺乏对新知识，新技术掌握，难以跟上时代的步伐，因此对专业教师进行培训、提高专业知识、技能是势在必行。\r\n我校信息技术系成立了世界技能大赛网络管理和网站设计两个项目广东选拔赛备战组，为能更加科学和系统的选拔输入人才，黄磊老师作为两个项目的主要负责人，更需要对计算机网络技术专业的知识有更深层次的掌握，才能使训练工作事半功倍。\r\n通过省级基础教育师资培训经费教师资助项目，加强学校信息技术系计算机网络技术专业师资队伍的建设，促进专业内涵发展，通过培养教学强师，以做到一帮一、传帮带的良性发展。\r\n五、项目可行性\r\n（一）受助对象本人符合项目要求\r\n1．资助人黄磊符合省级基础教育师资培训经费教师资助项目资助对象的条件，是根据广东省高级技工学校计算机网络技术专业建设的实际需求确定的资助人员。\r\n2．资助人黄磊使用资助资金的建设项目目标明确，内容具体，联系教育教学实际，具有良好的可操作性，能有效促进教师在教学能力、技术能力、教研能力等方面得到全面提升。\r\n3．省级基础教育师资培训经费教师资助项目将以培养教师教学强师为目标，并以指导和带动其他专业教师在专业水平、职业素养上得到提升。\r\n黄磊老师个人基本情况及主要工作业绩如下：\r\n黄磊，男，1984年7月出生，中共党员，毕业于中国地质大学（武汉）计算机科学与技术专业，硕士研究生学历，现任广东省高级技工学校信息技术系计算机综合科科长。2010年7月就职广东省高级技工学校，2011年转正式编制职工。2014年1月通过广东省人才资源和社会保障厅职业技能鉴定取得计算机网络管理员（二级/技师）职业资格， 2013年8月通过考核认定取得计算机科学与技术中级讲师资格。\r\n在思想政治方面，该同志忠诚党的教育事业，始终具有明确的政治目标，主动加强思想政治及教育理论学习，不断提高自身理论素质和教学水平，在工作中始终坚持党的基本路线，坚持党的四项基本原则，积极实践“三个代表”，贯彻执行科学发展观，践行十八大会议精神，关心国内国际时事和职业教育的发展动态，注意自身知识更新。\r\n在教学、科研和育人工作中该同志都取得了较好的成绩。2010年度、2011年度被学院评为“先进个人”， 2012年度被学院评为“优秀教师”；2013年度被学院评选为“先进教育工作者”；2015年度被学院评选为“优秀个人”、“十佳教师”；2014-2015年度被学院评为“优秀共产党员”；2013-2014年度、2014-2015年度被学院评为“优秀班主任”。\r\n在教学上，着力于对学生独立思考和自学能力的培养，激发学生的兴趣，调动学生学习的积极性，课堂教学生动活泼、扎实有效，深得学生的喜爱。在教学过程中形成了“情知互动，寓教于乐”的教学风格。近年来，主讲过《C++语言程序设计》、《软件工程》、《UML》、《软件测试》、《ASP程序设计》、《ASP.NET程序设计》、《C#语言程序设计》、《计算机程序设计员》等一体化课程，在教学中，因材施教，灵活运用多种现代教育教学方法，所授课程倍受学生的欢迎和同行的好评，历次课堂教学质量评价均为优秀。为更好的将教学理论与实践相结合，黄磊同志多次下企业进行实践，学习软件设计与开发、网络机房维护、计算机综合布线等相关专业知识。\r\n在教研教改上，黄磊同志撰写的《对一体化教学的思考》、《基于车型特征提取的车辆检测程序的实现》、《技工院校班主任师爱智慧》 3篇论文公开发表在《职业》、《电子技术与软件工程》、《课程教育研究》等国家级刊物上。副主编“国家职业教育精品规划教材”《Linux服务器管理项目教程》及《网络操作系统项目教程 Windows Server 2003篇》，以上教材均由国家级出版社出版。2014年5月，在学院举办的“第七届技能节”行动导向教学法教案项目中荣获三等奖；2015年6月，在学院举办的“第一届科研技能月“教学设计竞赛项目中荣获三等奖。2012年至2014年间，参与国家中等职业示范校广东省高级技工学校重点建设专业计算机网络技术专业的《计算机网络安全技术》核心课程建设工作，开发了课程标准及配套教材、学生工作页，并创建了教学资源库，推动了本专业一体化教学，圆满完成各项建设任务。\r\n在技能竞赛上，黄磊同志负责建设了学院世界技能大赛网络管理和网站设计两个项目训练实训室，组织系内骨干教师参与两个项目的培训工作，并在网站设计项目竞赛组中担任教练。全面负责两个项目备赛选手的选拔、训练计划的制定以及日常训练的开展，并取得了不错的成绩。在第44届世界技能大赛广东选拔赛上，网络管理项目学生获得第二名和第四名，网站设计项目学生获得第三名。\r\n黄磊同志具有较高的专业素养和技能水平，为学校拔尖的教学骨干。因此，该老师完全符合教师资助项目资助对象条件要求，通过教师资助项目的实施，一定能达到提升自身能力素质和帮助其他教师提升能力素质的目的。\r\n（二）受助对象可依托学校实施强师项目\r\n广东省技师学院于2002年升格为技师学校，成为我省发展较快、规模较大、综合实力较强的国家级重点技工院校之一，全日制在校生规模5000人以上，学校占地335亩；总建筑面积20.3万平方米，有教室199间，多媒体教学设备配备率达100%，实训场地 93个，多媒体配置率达91.35%，实训场地、设备总资产达1.2亿元。其中信息技术系学生有830人，在职专业教师有50名，其中“双师型”教师有17人，高级职称教师有10人，拥有计算机信息安全实训室、网络攻防实训室、网络设备配置实训室、综合布线实训室、计算机网络存储实训室，电子商务实训室，世赛网站设计项目实训室，世赛网络管理项目实训室等13间多媒体实训室。\r\n通过对资助对象的培养，提升自身专业技能，科研能力，可以引领信息技术系计算机网络技术专业的发展，带领年轻教师提升专业水平，促进学生职业技能朝更高、更精、更快发展，所以受助对象依托学校实施强师项目是可行的。\r\n六、资金绩效目标表\r\n省级基础教育师资培训经费教师资助项目绩效目标表预期产出产出计划三项总目标：（提升黄磊教师专业能力、教研科研能力、帮助提升其他教师，成为专业带头人。）过程资料年度阶段性目标：2017年1月至2017年5月完成专业培训计划提升自身专业能力、2017年6月至2017年9月完成学术论文发表提升教研科研能力、2017年10月到2017年12月完成带领新教师3名以及提升其他教师。效率计划 项目实施进度计划项目实施内容开始时间完成时间培训、参加教研交流、以老带新过程资料1. 提升教师本人专业技能能力2017年1月2017年5月2. 提升教师本人教研科研能力2017年6月2017年9月3. 提升其他教师能力2017年10月2017年12月预期效果预期社会经济效益指标类别个性化指标上年度实际水平本年度计划完成水平指标解释及计算公式说明培训、下厂实践、以老带新证明材料社会效益培训计划率0%100%完成专业技能培训1次反映项目实施直接产生的社会、经济、生态效益等，根据项目属性特点，可选择其中之一或多项效益，研究设置个性化指标及其目标值。下企业实践率0%100%完成下企业实践1次提升年轻教师率0%100%提升3名年轻教师能力审核意见省级主管部门审核意见\u000B                      审核人：    单位公章       年  月  日第三方机构审核意见\u000B                        审核人：    单位公章       年  月  日省财政厅审核意见\u000B                         审核人：    单位公章       年  月  日注：各申报单位个性化指标可自行根据项目特点设置指标，指标设置应可考核、可量化，能够与项目事后绩效评价相对接。 七、资金预算书\r\n省级基础教育师资培训经费黄磊教师资助项目资金预算表及考核指标\r\n项目\u000B名称建设内容具体项目专项资金预算(万元)考核指标黄磊老师教师资助项目提升教师本人专业技能能力参加计算机网络技术相关专业技能培训1参加专业技能培训学习总结1份；\r\n参加企业生产实践证明材料1份；\r\n购买书籍、资料及相关软件。下与专业相关企业参加生产实践1学习专业目前新知识、新技术0.2资料、图书费0.4提升教师本人教研科研能力参加教研交流和学习0.3参加教研交流学习总结1份。提升教师本人德育、教学教研管理能力参加德育、教学管理培训0.4培训结业证书。提升其他教师能力开展全校或全系范围计算机网络技术学术讲座0.2学术讲座过程资料1套；\r\n带领新教师证明材料1份；\r\n专家交流讲座过程资料1套。带领指导本专业新教师3名1.1聘请行业专家来校交流、讲座0.4合计5八、主要佐证材料\r\n黄磊教师资历一览表\r\n序号证书1毕业证2学位证书3职称证书4技能等级证书资历证明\r\n图1 毕业证书\r\n图2 学位证书\r\n图3 专业职称证书\r\n图4 技能等级证书\r\n黄磊教师荣誉及教科研成果一览表\r\n序号年度奖项备注12015十佳教师广东省技师学院22015优秀个人广东省技师学院32015“第一届科研技能月“教学设计竞赛项目三等奖广东省技师学院42014-2015优秀共产党员广东省技师学院52014-2015优秀班主任广东省技师学院62014“第七届技能节”行动导向教学法教案项目三等奖广东省技师学院72013-2014优秀班主任广东省技师学院82013先进教育工作者广东省技师学院92012优秀教师广东省技师学院102011先进个人广东省技师学院112010先进个人广东省技师学院122015十佳教师广东省技师学院132015论文：《对一体化教学的思考》2015.1 《职业》142016论文：《基于车型特征提取的车辆检测程序的实现》2016.5 《电子技术与软件工程》152016论文：《技工院校班主任师爱智慧》2016.7《课程教育研究》162013教材：《计算机网络安全技术》\r\n教材：《计算机网络安全技术-学生工作页》2013.12国家中职示范校校本教材172016《Linux服务器管理项目教程》北京理工大学出版社182016《网络操作系统项目教程 Windows Server 2003篇》北京理工大学出版社荣誉及教科研成果证明\r\n图5 优秀共产党员荣誉证书\r\n图6教学设计竞赛获奖证书\r\n图7 先进教育工作者荣誉证书\r\n图8 优秀班主任荣誉证书\r\n图9 行动导向教学法教案获奖证书\r\n图10先进个人荣誉证书\r\n图11 先进个人荣誉证书\r\n图12 优秀教师荣誉证书\r\n图13 十佳教师教师荣誉证书\r\n图14论文《对一体化教学的思考》\r\n图15论文《基于车型特征提取的车辆检测程序的实现》\r\n图16论文《技工院校班主任师爱智慧》\r\n图17国家中职示范校校本教材\r\n图18 Linux服务器管理项目教程\r\n图19网络操作系统项目教程 Windows Server 2003篇\r\n省级基础教育师资培训经费\r\n温锦文教师资助项目\r\n申\r\n报\r\n材\r\n料\r\n省级基础教育师资培训经费专项资金\r\n温锦文教师资助项目申请报告\r\n一、学校简介\r\n    广东省技师学院是广东省人民政府主办，直属广东省人力资源和社会保障厅的副厅级公办的国家级重点技工院校。 现有占地面积335亩，拥有博罗校本部和广州校区两个教学区，建筑面积20万平方米，全日制在册学生14526人，现有11个教学系，共开设65个专业，其中高级工以上专业40个，职业技能鉴定工种44个，年培训量4.7万人次，年鉴定量2.1万多人次。建有院内专业实训教室148间，技能大师工作室16间，是广东省历史最长、规模最大、综合实力最强的国家级重点技工院校。 \r\n　　学院有高级职称教师139人，双师型教师428人（占教师比例94.9%），其中有1位获全国五一劳动奖章、3位获国务院特殊津贴、6位获全国技术能手、3位全国优秀（模范）教师、1位获全国高技能人才培育突出贡献奖、2位获广东五一劳动奖章、29位获广东省技术能手。近几年，学院获国家级职业技能大赛奖4项，专利16项，获省级职业技能大赛奖22项，正式出版教材54本，公开发表论文293篇，教研成果获奖161个，获第43届世界技能大赛电子技术项目全国唯一参赛资格，荣获第43届世界技能大赛电子技术项目优胜奖。\r\n我校于1998年开始开办汽车专业，2009年8月成立汽车工程系，下设汽车检测维修科、汽车商务科及学生管理科，2008年9月开始开设汽车喷涂专业。历经十多年的发展，现有汽车喷涂专业5个班，学生210人；有汽车喷涂专业教师5人，并且有独立的汽车喷涂实训中心，设备齐全，目前已着手准备水性漆教学。温锦文老师系我校汽车工程系骨干教师，所带学生获第44届世界技能大赛汽车喷漆项目广东省选拔赛第二名。\r\n二、项目概况\r\n项目名称：省级基础教育培训经费温锦文教师资助项目\r\n（一）项目内容及主要任务：\r\n1.专业能力的提升\r\n资助对象到国内外汽车水性漆喷涂技术领域领先的高校及企业学习、进修。学习掌握汽车水性漆的特性、水性漆（单工序、双工序、三工序）喷涂方法、调色技术。同时研究高校与高职院校汽车水性漆喷涂技术专业的课程设置。\r\n资助对象走访企业，向企业技术员请教汽车水性漆喷涂技术，并分别到广东雅图化工有限公司、珠海龙神有限公司、上海庞贝捷油漆贸易有限公司（美国PPG工业集团）等企业学汽车水性漆的喷涂及调色技术。\r\n通过邀请世赛专家进校进行培训、指导，提高我校世赛汽车喷漆选拔赛成绩。 \r\n2.教科研能力的提升\r\n以资助对象为组长，成立广东省高级技工学校汽车维修（汽车水性漆喷涂技术方向）一体化课程改革课题小组，开展人才需求调研、工作岗位调研、制定人才培养方案、人才培养课程体系。通过课题建设培养具有专业能力、教科研能力的专业带头人。\r\n3.承接师资培训\r\n以资助对象为组长，建立以广东省高级技工学校教师为主的汽车水性漆喷涂技术培训团队，利用广东省高级技工学校汽车钣喷实训中心的平台，对广州地区、惠州地区、河源地区技工学校汽车专业骨干教师开展汽车水性漆技术培训，一年内培训8名专业骨干教师。\r\n三、项目基本情况表\r\n省级基础教育培训经费温锦文教师资助项目基本情况表    市（财政省直管理县）财政局（盖章）                       市（财政省直管理县）人力资源社会保障局（盖章）项目名称省级技工教育强师工程专项资金温锦文老师教师资助项目项目依据立项情况正在办理立项前准备工作《关于做好2017年度就业及技工教育专项资金（技工院校及技能实训基地建设方向）项目库入库项目申报工作的预通知》【粤人社函〔2016〕2020号】。投资总额（万元）5投资结构（万元）项目简介基础建设0    被资助人温锦文老师到国内外高校与企业进行汽车水性漆喷涂技术理论与实践学习，邀请国内专家教授到校对汽车喷涂研究小组进行专业培训，并以广东省高级技工学校汽车工程系钣喷实训中心平台开展师资培训。设置购置及\u000B信息化建设0教学改革5万筹资方案（万元）已落实资金0元申报省级资金5万项目情况绩效目标起始时间（年月）2017年1月1.到国内知名水性漆生产企业以及高校参加水性漆喷涂技术培训；\r\n2.邀请国内知名专家教授到校对水性漆专业团队进行培训；\r\n3.邀请世赛专家到校对世界技能大赛参赛选手进行水性漆技术指导；\r\n4.通过开展培训班的形式培养8名省内汽车专业骨干教师；\r\n5.培养优秀的汽车水性漆喷涂技术毕业生。终止时间（年月）2017年12月项目存续状态延续项目申报单位：广东省高级技工学校      填报人：成百辆       手机：13068268627\r\n项目负责人：夏  青       手机：18928389979注：1.“立项情况”指向发改部门提交立项的情况，填写：无需立项、正在办理立项前准备工作、项目建议书已批复、可行性研究报告已批复、已完成所有立项手续。       \r\n    2.“项目依据”填写支持项目申报的国家、省、市、县出台的相关政策文件依据及相关文号。\r\n    3.“项目存续状态”填写：延续项目或新增项目。延续项目指上一年度曾申报并获得省级补助资金，本次继续申报同一项目；新增项目指新申报的项目。四、项目的必要性\r\n （一）区域经济转型升级的需要\r\n1、传统的溶剂型油漆对环境的污染极大，而环保部门对汽车维修企业的排放要求越来越高，很多大城市已开始立法，禁止使用溶剂型油漆，在不久的将来汽车后市场的喷漆将全面使用水性漆对车辆进行维修；\r\n2、；广东的汽车保有量到目前为止已经超过2400万辆，并且呈现逐年快速上升趋势；汽车的喷漆量占整个汽车后市场维修量的百分之六十以上，市场份额大；\r\n3、水性漆喷涂技术人才缺少，以目前的状况来看根本无法满足市场的需求。\r\n（二）学校发展汽车后市场的需要\r\n 我校于1998年开始开办汽车专业，2009年8月成立汽车工程系，下设汽车检测维修科、汽车商务科及学生管理科。历经十多年的发展，从1998年的1个班发展到现有班级37个，学生1835人。汽车工程系设置有：汽车维修专业（高职）、汽车检测专业（高职）、汽车商务专业（高职）、汽车喷涂技术（中职）；其中汽车喷涂技术专业现有1个班，学生45人。\r\n     汽车工程系教学特色显著，多年来坚持职业导向和一体化教学，已先后为社会输送了几千名技能人才。这些技能人才分布于珠三角乃至全国各个企业，已成为各企业的中坚力量。汽车水性涂料产业已经进入高速发展期，而汽车水性漆喷涂技能型人才的缺乏将是制约产业发展及汽车后市场转型升级减排的重要因素，全省职业院校开设汽车水性漆喷涂技术课程非常少，关键的因素是没有师资和设备，另外在技术上水性漆的喷涂技术与传统的油性漆喷涂技术大不相同，传统油性漆喷涂专业教师不经过再学习，很难掌握新型水性漆的喷涂技术。培养汽车水性漆喷涂技术技能型人才是适应广东省乃至国家汽车后市场汽车喷涂技术发展的需要，高素质的师资队伍是培养技能型人才的先决条件，汽车水性漆喷涂技术专业教师资助项目的实施将会提升师资队伍的建设水平，项目的建设非常有必要。\r\n五、项目可行性\r\n（一）受助对象符合项目要求\r\n温锦文，男，1984年11月出生，河北工业大学车辆工程专业本科毕业；汽车制造与维修工艺一级实习指导教师；汽车维修高级技师；汽车维修高级考评员；汽车美容考评员； 2005年8月至今在广东省高级技工学校工作，任汽车维修专业教师，主讲的课程有汽车钣金技术、汽车喷涂技术、汽车油漆调色技术等，在工作过程中不断学习努力提升自已； 2014年被广东省高级技工学校聘为“汽车运用与维修”专业专家指导委员会专家组成员。\r\n1．主要学习经历\r\n（1）2010年11月去珠海市龙神有限公司参加汽车喷涂技术师资培训班学习；\r\n（2）2011年7月至8月去广东雅图化工有限公司学习汽车油漆调色及喷涂技术。\r\n（3）2013年3月参加广东雅图化工有限公司举办的汽车油漆调色技术培训班。\r\n（4）2013年11月在广东省高级技工学校参加教学能力学习。\r\n（5）2014年3月至4月去广州市三项教学仪器有限公司学习汽车新技术。\r\n（6）每年都利用寒暑假的时间到惠州俊峰丰田、惠州永兴汽车修配厂、富华进口汽车修配厂等企企业实践学习。\r\n    2．主要工作成果\r\n（1）2004年第五届校园科技文化周科技作品竞赛中获得二等奖；\r\n（2）2006年参与研究《丰田1G-FE电控发动机实验台》获得校级科研成果三等奖；\r\n（3）主编两本一体化教材：《汽车钣金、喷漆与美容》和《汽车底盘构造与维修》；担任副主编一体化教材一本：《汽车电气构造与维修（下册）》。2013年人民邮电出版社出版了上述三本教材；\r\n（4）2013年参加广东雅图化工有限公司举办的“汽车钣金喷漆”技能竞赛获得一等奖（第一名）；\r\n（5）2013、2014连续两年获得广东省高级技工学校“十佳教师”荣誉称号；\r\n（6）2006-2007学年度、2011-2012学年度、2013年度被评为优秀教师；2007年度被评为先进教育工作者；2009年度被评为先进个人；2006-2007学年度被评为德育先进个人；2005-2006学年度、2008-2009学年度、2010-2011学年度被评为优秀班主任；\r\n（7）在国家级刊物《商情》上发表论文《浅谈空调压缩机再次过早烧坏的一些维修方法》；《中国对外贸易》上发表论文《本田雅阁CD5轿车怠速游动的分析与排除》；《军民两用技术与产品》上发表论文《奔驰空调不制冷的故障诊断与排除》；《中国科技博览》上发表论文《长安铃木轿车发动机怠速抖动的故障诊断与排除》；\r\n（8）承担第43届世界技能大赛广东省选拔赛汽车喷漆项目惠州代表队教练，所带选手方镇坤获得第四名，巫昌龙获得第八名；\r\n（9）承担第44届世界技能大赛广东省选拔赛汽车喷漆项目惠州代表队和广东省高级技工学校代表队（省属学校）教练，所带选手方镇坤获得第二名，蔡泽杰获得第六名；\r\n（二）项目依托的广东省高级技工学校有良好的师资培训平台\r\n广东省技师学院于2000年经人社部评估为国家级高级技工学校，2002年经省政府批准升格为广东省技师学院，短短7年时间学院便完成了从省一类技校到技师学院的发展历程。学院秉承“确保质量、提高层次、突出特色、服务就业”的办学方针，力促学院规模发展、内涵发展、高端发展、创新发展，成为我省发展最快、规模最大、综合实力最强的国家级重点技工院校。学院自2006年起连续四年被评为“广东技工教育竞争力”第一名，2007年获中华职教社首届“黄炎培优秀学校奖”（全国唯一获奖技工院校），每年都荣获广东省技工院校“招生工作突出贡献”奖。学院是国家中等职业教育改革发展示范校、国家级高技能人才培训基地、国家级职业培训师资培训基地、全国技工院校师资培训基地、人社部“工学结合一体化”教学试点单位、团中央“共青团青年就业创业见习基地”；\r\n学校于1998年开始开办汽车专业，2009年8月成立汽车工程系，下设汽车维修科、汽车商务科及学生管理科，有专业教师40人，其中钣喷专业教师4人；拥有450平方米的汽车喷涂实训中心，一个油性漆喷烤漆房，一个水性漆喷烤漆房，五个标准干磨工位，并配备了标准干磨设备，20把SATA顶级喷枪，其中水性漆喷枪8把；2015年还承担了全省汽车喷漆师资培训任务，培训效果得到社会的认可。历经十多年的发展，从1998年的一个班发展到现有班级37个，学生1835人，目前汽车维修（汽车喷涂技术）专业学生有45人。\r\n汽车喷涂技术专业是全省乃至全国的紧缺人才专业，学校也把汽车喷涂技术专业作为重点的建设项目之一；学院还设立有汽车喷涂大师工作室，将能满足水性漆喷涂技术的培训要求，加之汽车保有量的日渐增加，而汽车售后服务当中，车身的喷涂作业是占大部分的，所以当务之急是培养一流的汽车水性漆喷涂人才。\r\n六、资金绩效目标表\r\n省级基础教育培训经费温锦文教师资助项目绩效目标表预期产出产出计划1．到国内知名水性漆生产企业以及高校参加水性漆喷涂技术培训；\r\n2．邀请国内知名专家教授到校对水性漆专业团队进行培训；\r\n3．邀请世赛专家到校对世界技能大赛参赛选手进行水性漆技术指导；\r\n4．通过开展培训班的形式培养8名省内汽车专业骨干教师；\r\n5．培养优秀的汽车水性漆喷涂技术毕业生。总目标：（资助人掌握汽车水性漆喷涂技术，并培养8名汽车喷涂专业骨干教师掌握该项技术，通过教师培养企业急需的技能型人才）1、师资培训名册 2、培训讲义、PPT                                                  3、师资培训计划年度阶段性目标：（通过10个月的学习完全掌握好汽车汽车水性漆喷涂技术，再通过2个月以培训班外加远程技术指导的方法培养8名省内汽车喷涂专业骨干教师。）效率计划 项目实施进度计划项目实施内容开始时间完成时间学习结业证明\r\n下企业实践证明                    3、企业评价1.高校进修2017年1月2017年8月2.企业实践2017年1月2017年8月3、邀请专家2017年1月2017年12月3.开展师资班2017年9月2017年12月预期效果预期社会经济效益指标类别个性化指标上年度实际水平本年度计划完成水平指标解释及计算公式说明培训、下厂实践、以老带新证明材料社会效益\r\n培训计划完成率0%100%完成专业技能培训1次反映项目实施直接产生的社会、经济、生态效益等，根据项目属性特点，可选择其中一或多项效益，研究设置个性化指标及其目标值。下企业实践率0%100%完成下企业实践1次提升年轻教师率0%100%提升8名年轻教师能力审核意见省级主管部门审核意见\u000B                      审核人：    单位公章       年  月  日第三方机构审核意见\u000B                        审核人：    单位公章       年  月  日省财政厅审核意见\u000B                         审核人：    单位公章       年  月  日注：各申报单位个性化指标可自行根据项目特点设置指标，指标设置应可考核、可量化，能够与项目事后绩效评价相对接。 经济效益和生态效益确实无法设置指标的，可不设置。七、资金预算书\r\n温锦文老师教师资助项目资金预算及考核指标\r\n项目\u000B名称建设内容具体项目资金支出项专项资金预算(万元)考核指标温锦文老师教师资助项目提升理论教学能力高校学习、进修；企业学习与实践学费、交通、住宿费1.91.学习结业证明。资料、图书费邀请国内知名专家教授到校对水性漆专业团队进行培训授课费、交通、0.51.现场照片及专家资料；\r\n2.专业团队教师花名册。邀请事赛专家到校对世界技能大赛参赛选手进行水性漆技术指导授课费、交通、1.21.现场照片及专家资料；\r\n2.选手花名册。企业行业调研企业行业调研，了解企业需求交通、住宿费0.41．企业评价；\r\n2.企业调查表。                   承接师资培训任务开展师资培训(培养8名骨干教师)培训资料费11.师资培训名册；                       2.培训讲义、PPT；                                 3.师资培训计划。实训材料费工具费合计5八、主要佐证材料\r\n序  号名  称1本科毕业证书2汽车维修技术等级证书3一级实习指导教师职称证书42014年专家指导委员会聘书5考评员、高级考评员证62004年第五届科技文化周科技作品竞赛中获得二等奖72006年第六届科技文化周教师作品评比获得校级科研成果三等奖8主编教材《汽车钣金、喷漆与美容》；《汽车底盘构造与维修，副主编教材《汽车电气构造与维修（下册）》92013年参加汽车钣金喷漆技能竞赛获得一等奖10十佳教师荣誉证书11优秀教师、先进个人、先进教育工作者、优秀班主任荣誉证书12国家级刊物发表论文材料13第43届世界技能大赛广东省选拔赛汽车喷漆项目排名表14第44届世界技能大赛广东省选拔赛汽车喷漆项目排名表15参加珠海市龙神有限公司汽车喷涂技术师资培训班学习证明16去广东雅图化工有限公司学习汽车油漆调色及喷涂技术的学习证明17参加广东省高级技工学校教学能力学习证明18去广州市三项教学仪器有限公司学习汽车新技术的学习证明19在惠州俊峰丰田、惠州永兴汽车修配厂、富华进口汽车修配厂学习证明1.本科毕业证书\r\n2.汽车维修技术等级证书\r\n3.一级实习指导教师职称证书\r\n4.2014年专家指导委员会聘书\r\n5.考评员证书\r\n6.2004年第五届科技文化周科技作品竞赛中获得二等奖\r\n7．2006年第六届科技文化周教师作品评比获得校级科研成果三等奖\r\n\b8.主编教材《汽车钣金、喷漆与美容》；《汽车底盘构造与维修》；副主编教材《汽车电气构造与维修（下册）》\r\n9.2013年参加汽车钣金喷漆技能竞赛获得一等奖\r\n10.十佳教师荣誉证书\r\n11.优秀教师、先进个人、先进教育工作者、优秀班主任荣誉证书\r\n12.国家级刊物发表论文材料\r\n13.第43届世界技能大赛广东省选拔赛汽车喷漆项目排名表\r\n(网址：http://www.conet.org.cn/skill/form/131-15426537.html）\r\n14.第44届世界技能大赛广东省选拔赛汽车喷漆项目排名表\r\n15.参加珠海市龙神有限公司参加汽车喷涂技术师资培训班学习证明\r\n16.参加广东雅图化工有限公司学习汽车油漆调色及喷涂技术学习证明\r\n17.参加广东省高级技工学校进行教学能力学习证明\r\n18.参加广州市三项教学仪器有限公司学习汽车新技术学习证明\r\n19.在惠州俊峰丰田、惠州永兴汽车修配厂、富华进口汽车修配厂学习证明\r\n省级基础教育师资培训经费\r\n张小清教师专项资金申请报告\r\n申\r\n报\r\n材\r\n料\r\n省级基础教育师资培训经费专项资金\r\n张小清教师资助项目申请报告\r\n一、学校简介\r\n广东省技师学院是广东省人民政府主办，直属广东省人力资源和社会保障厅的副厅级公办的国家级重点技工院校。 现有占地面积335亩，拥有博罗校本部和广州校区两个教学区，建筑面积20万平方米，全日制在册学生14526人，现有11个教学系，共开设65个专业，其中高级工以上专业40个，职业技能鉴定工种44个，年培训量4.7万人次，年鉴定量2.1万多人次。建有院内专业实训教室148间，技能大师工作室16间，是广东省历史最长、规模最大、综合实力最强的国家级重点技工院校。 \r\n学院有高级职称教师139人，双师型教师428人（占教师比例94.9%），其中有1位获全国五一劳动奖章、3位获国务院特殊津贴、6位获全国技术能手、3位全国优秀（模范）教师、1位获全国高技能人才培育突出贡献奖、2位获广东五一劳动奖章、29位获广东省技术能手。近几年，学院获国家级职业技能大赛奖4项，专利16项，获省级职业技能大赛奖22项，正式出版教材54本，公开发表论文293篇，教研成果获奖161个，获第43届世界技能大赛电子技术项目全国唯一参赛资格，荣获第43届世界技能大赛电子技术项目优胜奖。\r\n2010年学校成立了质量技术系，开设了产品检测与质量管理专业。本专业重点培养学生对机械产品和电子元器件的检测操作能力、质量分析和控制能力及品质管理能力。目前，我校产品检测与质量管理专业学生供不应求，至2016年7月为社会和企业输送了近600名素质高的实用型人才。产品检测与质量管理专业不仅是社会经济转型及发展的需要，也是学校模具、数控、电器等机电类专业教学实践和发展的需求。\r\n二、项目概况\r\n项目名称：省级基础教育师资培训经费专项资金张小清教师资助项目\r\n项目内容：通过项目投入，提升张小清老师及其团队的教学业务能力、教科研能力、专业技术能力、实践培训能力和德育教育工作能力。\r\n主要任务：一是掌握产品精密检测技术新技术。针对检测设备的应用，到厂家指定培训中心或其它培训机构进行技能培训，学习掌握检测设备的操作应用；参加企业实践，学习掌握精密检测行业新工艺、新技术知识，不断提高实践教学指导能力，同时到高校学习精密检测专业设置及教学模式，完善产品检测专业建设。二是完善产品检测与质量管理专业实训课题开发工作，成立课题和试题库开发工作小组，通过三坐标精密测量、影像测量和金属材料性能检测三项实习课题建设和试题库开发工作，培养具有专业能力，具有教科研能力的专业教师，体现资助对象骨干教师带头作用。三是通过与企业合作平台，完成对学生或企业员工三坐标精密测量技术的培训工作。\r\n预期目标：能胜任对内对外的师资培训、制定精密检测专业建设发展方案、成立精密检测精英团队，提高学生对精密检测技术的应用能力。\r\n投资规模：本项项目投资总额5万元，项目完成时间为一年,本项目资金投向：自身能力素质提升培训和帮助其他教师能力素质提升培训,并明确资金使用目标、考核指标。\r\n三、项目基本情况表\r\n省级技工教育强师工程专项资金教师资助项目基本情况表      市（财政省直管理县）财政局（盖章）         市（财政省直管理县）人力资源社会保障局（盖章）项目名称张小清教师资助项目项目依据立项情况正在办理立项前准备工作  《关于做好2017年度就业及技工教育专项资金（技工院校及技能实训基地建设方向）项目库入库项目申报工作的预通知》【粤人社函〔2016〕2020号】。投资总额（万元）5投资结构（万元）项目简介基础建设（万元）0通过项目的资助，提升张小清老师及其团队的教学业务能力、专业技术能力、教科研能力、德育教育工作能力和实践培训能力。设置购置及信息\u000B化建设（万元）0改革教学（万元）5筹资方案（万元）0已落实资金（万元）0申报省级资金5项目情况绩效目标起始时间（年月）2017年1月能胜任对内对外的师资培训、制定精密检测专业建设发展方案、成立精密检测精英团队，提高学生对精密检测技术的应用能力。终止时间（年月）2017年12月项目存续状态延续项目申报单位：                      填报人：成百辆       手机：13068268627\r\n项目负责人：夏  青       手机：18928389979注：1.“立项情况”指向发改部门提交立项的情况，填写：无需立项、正在办理立项前准备工作、\r\n       项目建议书已批复、可行性研究报告已批复、已完成所有立项手续。\r\n2.“项目依据”填写支持项目申报的国家、省、市、县出台的相关政策文件依据及相关文号\r\n3.“项目存续状态”填写：延续项目或新增项目。延续项目指上一年度曾申报并获得省级补助资金，本次继续申报的同一项目；新增项目指新申报的项目。四、项目的必要性\r\n（一）区域经济转型升级需要产品检测与质量管理专业教学名师\r\n学校地处惠州市博罗县，毗邻深圳、东莞、广州，各市高新区、工业园区、综合产业园区，以各企业形成了产业体系，在全省乃至全国占有重要地位。\r\n随着社会发展的需要，社会对产品质量的要求也越来越高，质量是企业的发展的源泉。因此，企业需要大量的质量管理与精密检测高技能人才，而技能型人才的缺乏将是制约产业发展的重要因素。我校产品检测与质量管理专业是全省乃至全国技工院校的先河、此专业是我校特色优势专业，产品检测类专业技能人才完全不能满足企业要求，在现有的师资条件下难以满足企业对员工的高新技术要求，培养产品检测类专业技术技能型人才是适应广东省乃至全国质量管理和精密检测技术发展的需要。因此，高素质的师资队伍是培养技能型人才的必要条件。\r\n（二）学校发展需要产品检测与质量管理类专业教学名师\r\n1.学校产品检测教学与专业教师现状\r\n我校质量技术系现开设有初中起点三年制中级和高中起点三年制高级产品检测与质量管理专业，2016年秋季开始将全部招高级班（初中起点五年制和高中起点三年制）。\r\n质量技术系产品检测与质量管理专业每年均有2个中级班和1个高级班，约150人，现有产品检测相关课程专职教师5名，其中：中级职称教师3人，初级2人；高级技师2人、技师1人、高级工2人。\r\n教师普遍缺乏实际操作经验，动手能力不强的问题比较突出，与技能名师要求相差较远；与企业对人才素质的要求不相适应；也与正在推行的工学一体化教学改革的要求不相适应。企业对技能人才的素质要求与教师自身素质的矛盾凸显，所以提升教师自身能力素质迫在眉睫。\r\n专职教师数量与学生数量配比失衡，免强满足教学需要；教师对新的教学理念方法、专业领域新知识新技术新工艺认识不足；教师教学、教科研能力和教改能力有限等。\r\n2.产品检测与质量管理专业教师资助的意义\r\n产品检测专业强师工程教师资助项目的实施将会推动质量技术系师资队伍提升，促进专业建设、有利于提高专业人才培养质量，优化师资队伍结构、提升教师团队的教科研和教改能力、提升学生服务社会的专业能力，培养更多高素质技能人才的需要，满足区域经济转型升级的需要。\r\n五、项目可行性\r\n（一）受助对象本人符合项目要求\r\n1.资助人张小清符合省级基础教育师资培训经费教师资助项目资助对象的条件，是根据广东省高级技工学校特色专业（精密检测专业）建设的实际需求确定的资助人员。\r\n2.资助人张小清使用资助资金的建设项目目标明确，内容具体，联系教育教学实际，具有良好的可操作性，能有效促进教师在教学能力、技术能力、教研能力等方面得到全面提升。\r\n3.省级基础教育师资培训经费教师资助项目将以培养教师教学强师为目标，并以指导和带动其他专业教师在专业水平、职业素养上得到提升。\r\n张小清老师个人基本情况及主要工作业绩如下：\r\n张小清，男，1983年6月生，中共党员，2005年7月毕业于广东省高级技工学校模具设计与制造专业，2010年取得广东工业大学本科学历，2005年8月至今在广东省高级技工学校担任专职教师，从事技工教育至今11年。2005年在东部地区广东选拔赛模具制造工职工组（冷冲模）获第三名；2008年取得模具制工高级技师，2010年获惠州市技术能手称号；2012年被学校聘为三级“一体化教师”；2014年被学校聘为机械工艺一级实习指导教师。\r\n该同志忠诚党的教育事业，对工作兢兢业业，无私奉献，爱岗敬业，爱校如家，刻苦钻研教学业务知识，专业知识厚实，责任感强，在技工教育的工作岗位上取得了较好成绩，学校也给予了肯定。曾获 “惠州市技术能手”称号，先后获得多次校“优秀教师”、“先进个人”和“先进教育工作者”，3次获得校“十佳教师”，1次评为校 “优秀班主任”，1交评为“先进德育工作者”，2次评为“优秀共产党员”等荣誉称号。\r\n在教学上，重视对学生综合素质的培养，精益求精地做好每一教学环节的工作。十一年来，主讲过《机械制图》、《机械识图》、《模塑工艺与模具结构》、《机修钳工工艺》、《钳工工艺学》、《互换性与公差配合》、《机械产品检验》等专业理论课程；担任《模具设计》毕业设计指导工作及《综合模具设计与制造》、《钳工》、《电火花与线切割》、《铣工与磨工》、《零件测绘》、《CAD》、《Pro/E》等实习指导工作；从2011年9月开始在质量技术系一直担任《平台测量》、《精密测量》、《金属材料性能检测》等一体化课程教学工作。所授课程均受学生的欢迎和同行的好评，教学质量评价均为优秀，在2014年全校“十佳教师”示范课中表现突出，得到了各位领导和老师的好评。\r\n在教科研方面公开发表专业论文1篇，主编校本教材或指导书2本，参与编写教材1本。完成了《精密测量》和《平台测量》一体化课程标准的开发工作；撰写的一体化教学论文获校一等奖，在广东教育研究优秀论文评选中获三等奖。2015年全校教学设计获一等；省教研室德育论文评先三等奖。2016年科研技能月活动中各类教学业务能力竞赛成绩优异。\r\n张小清同志具有较高的专业素养和技能水平，为学校拔尖的教学骨干。因此，该老师完全符合教师资助项目资助对象条件要求，通过教师资助项目的实施，一定能达到提升自身能力素质和帮助其他教师提升能力素质的目的。\r\n（二）受助对象可依托学校实施强师项目\r\n广东省高级技工学校依托广东制造业这个坚实平台，凭借毗邻惠州、深圳、东莞和广州的地理优势，于2009年建立质量技术系，开设了产品检测与质量管理专业。现有本专业在籍学生400多人，拥有中、高级9个班级，发展速度快。质量技术系产品检测与质量控制专业是学校重点打造的“特色优势专业”。目前，我院产品检测与质量管理专业已辐射到广州和粤东地区。\r\n质量技术系产品检测与质量管理专业现有产品质量检测实训基地，拥有精密测量实训室、电子元器件检测和电子产品装配实训室、基本量测实训室、金相实训室、金属材料性能检测实训室、CAD实训室等。\r\n有了学校和系部强有力的支持，现又与海克斯康有限公司建立了合作关系，受助对象本人具有一定的专业优势和教学经验，有先进的实训设备和企业技术服务支持，通过教师资助项目的实施，一定能打造出业务更精湛、专业更深厚、技能更高强的专业教师。\r\n为了使产品检测专业能适应社会用人需求的发展，需加大学校师资队伍建设，通过这次项目实施能提高我院的师资水平，促进学生职业技能更精、更强发展，所以受助对象依托学校实施强师项目是可行的。\r\n六、资金绩效目标表\r\n    张小清教师资助   项目绩效目标表预期产出产出计划培训结业证书\r\n校编教材1本\r\n论文1篇\r\n企业实践或调研材料\r\n培训与竞赛材料总目标：能胜任对内对外的师资培训、制定精密检测专业建设发展方案、成立精密检测精英团队，提高学生对精密检测技术的应用能力。提交相关资料和证书年度阶段性目标：上半年主要提升自身或教师团队教科研能力和德育工作能力（1.8万元左右）；下半年自身或教师团队主要参加专业技术培训、下厂调研学习并开展相关培训竞赛工作（3.2万左右）效率计划 项目实施进度计划项目实施内容开始时间完成时间学习、培训、教研过程材料1. 提升教研科研能力2017年1月2017年12月2. 提升专业技能能力2017年6月2017年12月2.帮助提升其他教师能力2017年10月2017年12月预期效果预期社会经济效益指标类别个性化指标上年度实际水平本年度计划完成水平指标解释及计算公式说明提供相关证明材料社会效益校编教材编写1本1本为学生提供实用性强的教材，为社会培养出三坐标精密检测高级应用型人才，能给单位及系部带来社会或经济效益精密测量高级应用培训020人审核意见省级主管部门审核意见\u000B                      审核人：    单位公章       年  月  日第三方机构审核意见\u000B                        审核人：    单位公章       年  月  日省财政厅审核意见\u000B                         审核人：    单位公章       年  月  日注：各申报单位个性化指标可不局限于表中示例，可自行根据项目特点设置指标，指标设置应可考核、可量化，能够与项目事后绩效评价相对接。 经济效益和生态效益确实无法设置指标的，可不设置。七、资金预算书\r\n   张小清教师资助项目  资金预算及考核指标\r\n项目\r\n序号教师资助项目具体项目专项资金预算(万元)考核指标1提升教学业务能力购买书籍、资料0.61.订阅获购买教学书籍、杂志;\r\n2.培训结业证书。教学方法培训教师职业能力培训2提升教科研能力参与主持精密测量专业建设11.专业建设相关资料；              2.专业研讨相关资料；\r\n3.教材资料；\r\n4.发表论文1篇。                  参与并组织精密测量专业教学课题研讨与开发参与并组织精密测量一体化校编教材编写论文撰写3提升专业技术及实践培训能力参加精密检测新方法、新技术、新工艺、新标准培训21.培训结业证书；\r\n2.培训方案相关资料；\r\n3.调研与交流相关资料。参加精密测量高级应用培训研究精密测量技术培训方案专业调研及与同行交流4提升德育教育工作能力参加德育教育工作培训0.21.培训结业证书。5帮助提升其他教师能力参与并组织听专家讲座、参加专业培训1.21.提供学习培训相关资料；\r\n2.提供参观学习相关资料；\r\n3.提供开展培训及竞赛相关资料。组织教师到知名企业、学校参观学习开展精密检测技术相关培训工作指导教师和学生参加竞赛活动6合计5八、主要佐证材料\r\n张小清老师资历一览表\r\n序号证书1毕业证2教师上岗证书3职称证书4技能等级证书5模具设计师考评员证6钳工高级考评员证7一体化教师聘书张小清老师资历证明\r\n图1——毕业证书\r\n图2——教师上岗证书                  图3——职称证书\r\n      图4——技能等级证书\r\n图5——模具设计师考评员证            图6——钳工高级考评员证\r\n图7——三级一体化教师聘书\r\n张小清老师荣誉及教科研成果一览表\r\n序号年度奖项颁发单位12005广东选拔赛模具制造工第三名广东省劳动和社会保障厅22006～2007优秀教师广东省高级技工学校32007先进教育工作者广东省高级技工学校42008先进教育工作者广东省高级技工学校52008模具综合技能团体三等奖广东省职业技术教研室62008～2009机械常识比赛三等奖广东省高级技工学校72008技能节教具制作三等奖广东省高级技工学校82009先进个人广东省高级技工学校92010先进个人广东省高级技工学校102010.9惠州市技术能手惠州市人力资源和社会保障局112010十佳教师广东省高级技工学校122011-2012优秀班主任广东省高级技工学校132012十佳教师广东省高级技工学校142012优秀教师广东省高级技工学校152012-2013优秀教师广东省高级技工学校162012-2013德育优进个人广东省高级技工学校172013一体化教学论文一等奖广东省高级技工学校182013优进教育工作者广东省高级技工学校192013十佳教师广东省高级技工学校202014说课比赛三等奖广东省高级技工学校212014-2015年度优秀共产党员广东省高级技工学校222014优秀论文评选三等奖广东省职业技术教研室232015行动导向教学设计一等奖广东省高级技工学校242014-2015优秀教师广东省高级技工学校252015德育论文三等奖广东省职业培训和技工教育协会262016多媒体课件一等奖广东省高级技工学校272007、2012校编教材、指导书、习题册广东省高级技工学校282007参编教材中国劳动出版社292014公开发表论文模具制造杂志社张小清老师荣誉及教科研成果证明\r\n图8——职业技能广东选拔赛模具制造工第三名\r\n图9——06～07学年度优秀教师\r\n图10——07年度先进教育工作者\r\n图11——08年度先进教育工作者\r\n图12——08年广州地区省属技工学校教师模具综合技能团体三等奖\r\n图13——08～09学年机械常识比赛三等奖\r\n图14——08年第四届技能节科技作品教具制作三等奖\r\n图15——09年度先进个人\r\n图16——10年度先进个人\r\n图17——惠州市技术能手\r\n图18——10年度十佳教师\r\n图19——11～12学年度优秀班主任\r\n图20——12年度十佳教师\r\n图21——12学年度优秀教师\r\n图22——12～13学年度优秀教师\r\n图23——12～13学年度德育先进个人\r\n图24——13年一体化论文一等奖\r\n图25——13年度先进教育工作者\r\n图26——13年度十佳教师\r\n图27——14年系部说课比赛三等奖\r\n图28——14～15年度优秀共产党员\r\n图29——14年论文评选三等奖\r\n图30——15年教学设计一等奖\r\n图31——14～15年度优秀教师\r\n图32——15年德育论文三等奖\r\n图33——16年多煤体课件一等奖\r\n图34——校编教材\r\n图35——校编习题册\r\n图36——中国劳动出版社参编教材\r\n图37——公开发表论文\r\n          广东省技师学院\r\n                                  二0一六年十月\r\n省级基础教育强师工程\r\n王怀术教师资助项目\r\n申\r\n报\r\n材\r\n料\r\n省级基础教育师资培训经费\r\n王怀术教师资助项目申请报告\r\n一、学校简介\r\n广东省技师学院是广东省人民政府主办，直属广东省人力资源和社会保障厅的副厅级公办的国家级重点技工院校。 现有占地面积335亩，拥有博罗校本部和广州校区两个教学区，建筑面积20万平方米，全日制在册学生14526人，现有11个教学系，共开设65个专业，其中高级工以上专业40个，职业技能鉴定工种44个，年培训量4.7万人次，年鉴定量2.1万多人次。建有院内专业实训教室148间，技能大师工作室16间，是广东省历史最长、规模最大、综合实力最强的国家级重点技工院校。 \r\n学院有高级职称教师139人，双师型教师428人（占教师比例94.9%），其中有1位获全国五一劳动奖章、3位获国务院特殊津贴、6位获全国技术能手、3位全国优秀（模范）教师、1位获全国高技能人才培育突出贡献奖、2位获广东五一劳动奖章、29位获广东省技术能手。近几年，学院获国家级职业技能大赛奖4项，专利16项，获省级职业技能大赛奖22项，正式出版教材54本，公开发表论文293篇，教研成果获奖161个，获第43届世界技能大赛电子技术项目全国唯一参赛资格，荣获第43届世界技能大赛电子技术项目优胜奖。\r\n学院下属的物流专业依托学校健全的内部教学质量监控与保障体系，深化人才培养模式改革，培养具有物流管理基本能力的人才，掌握物流管理的最新动态，掌握物质资料在生产、流通、消费各环节的流通规律及现代化物流企业管理基本理论，通晓物流学基本原理，掌握物流现代化趋势以及相关的物流技术，掌握物流中的运输、搬运、包装、仓储、配送等技能，能够在各种类型物流企业及生产企业物流管理部门从事物流系统设计及物流经营、管理、决策工作的技师层次高级应用型技能人才。\r\n二、项目概况\r\n项目名称：省级基础教育师资培训经费王怀术教师资助项目\r\n项目内容及投资规模：通过项目投入，提升王怀术老师的专业能力、教科研能力、专业教学及培训能力、职业生涯规划能力、德育教育工作能力、教学教研管理能力、提升师资培训能力。本项项目投资总额5万元，本项目资金投向：自身能力素质提升培训4万元，帮助其他教师能力素质提升培训1万元。\r\n主要任务：一是通过校外深造学习掌握物联网、大数据物流、物流金融、北斗卫星应用等大数据应用技术在物流中的应用，掌握利用大数据、交互系统、卫星导引定位等创新物流管理服务模式，为校区物流管理专业教学做好充足的准备；二是完善物流管理专业人才需求调研、工作岗位调研、制定人才培养方案、人才培养课程体系工作，通过课题建设培养具有专业能力，具有教科研能力的专业带头人。 \r\n预期目标：参加专业培训1次、参与实践1次、发表论文1篇、参加教研交流1次、开展项目开发1个、能胜任校内外培师资培训、制定物流专业发展方向。\r\n三、项目基本情况表\r\n省级基础教育师资培训经费教师资助项目基本情况表    市（财政省直管理县）财政局（盖章）           市（财政省直管理县）人力资源社会保障局（盖章）项目名称王怀术教师资助项目项目依据立项情况正在办理立项前准备工作支持项目申报国家、省、市县出台的相关政策文件依据以及相关文号投资总额（万元）5投资结构（万元）项目简介基础建设0通过项目投入，提升王怀术老师的专业能力、参加专业培训、购买专业领域的参考用书、参与企业实践、参加教研交流、发表学术论文、提升教学教研能力、带领提升新教师。设置购置及\u000B信息化建设0教学改革5筹资方案（万元）0已落实资金0申报省级资金5项目情况绩效目标起始时间（年月）2017年1月能胜任校内外培师资培训、制定物流专业发展方向、编写教改教材、撰写专业论文、完成物流专业教师的转型培训。终止时间（年月）2017年12月项目存续状态延续项目申报单位：广东省高级技工学校       填报人：成百辆       手机：13068268627\r\n项目负责人：夏  青       手机：18928389979注：1.“立项情况”指向发改部门提交立项的情况，填写：无需立项、正在办理立项前准备工作、项目建议书已批复、可行性研究报告已批复、已完成所有立项手续。\u000B    2.“项目依据”填写支持项目申报的国家、省、市、县出台的相关政策文件依据及相关文号。\u000B    3.“项目存续状态”填写：延续项目或新增项目。延续项目指上一年度曾申报并获得省级补助资金，本次继续申报的同一项目；新增项目指新申报的项目。\r\n四、项目必要性\r\n（一）物流管理发展前景分析：国家大力支持物流行业发展。\r\n物流业是融合运输、仓储、货代、信息等产业的复合型服务业，是支撑国民经济发展的基础性、战略性产业。加快发展现代物流业，对于促进产业结构调整、转变发展方式、提高国民经济竞争力和建设生态文明具有重要意义。\r\n1．大力提升物流社会化、专业化水平。\u000B　　鼓励制造企业分离外包物流业务，促进企业内部物流需求社会化。优化制造业、商贸业集聚区物流资源配置，构建中小微企业公共物流服务平台，提供社会化物流服务。\u000B　　2．进一步加强物流信息化建设。\u000B　　加强北斗导航、物联网、云计算、大数据、移动互联等先进信息技术在物流领域的应用。促进物流信息与公共服务信息有效对接，鼓励区域间和行业内的物流平台信息共享，实现互联互通。\u000B　　3．推进物流技术装备现代化。\u000B　　加强物流核心技术和装备研发，推动关键技术装备产业化，鼓励物流企业采用先进适用技术和装备。\u000B　　4．加强物流标准化建设。\u000B　　加紧编制并组织实施物流标准中长期规划，完善物流标准体系。按照重点突出、结构合理、层次分明、科学适用、基本满足发展需要的要求，完善国家物流标准体系框架，加强通用基础类、公共类、服务类及专业类物流标准的制定工作，形成一批对全国物流业发展和服务水平提升有重大促进作用的物流标准.\u000B　　5．推进区域物流协调发展。\u000B　　落实国家区域发展整体战略和产业布局调整优化的要求，继续发挥全国性物流节点城市和区域性物流节点城市的辐射带动作用，推动区域物流协调发展。\u000B　　6．积极推动国际物流发展。\u000B　　加强枢纽港口、机场、铁路、公路等各类口岸物流基础设施建设。以重点开发开放试验区为先导，结合发展边境贸易，加强与周边国家和地区的跨境物流体系和走廊建设，加快物流基础设施互联互通，形成一批国际货运枢纽，增强进出口货物集散能力。加强境内外口岸、内陆与沿海、沿边口岸的战略合作，推动海关特殊监管区域、国际陆港、口岸等协调发展，提高国际物流便利化水平。建立口岸物流联检联动机制，进一步提高通关效率。积极构建服务于全球贸易和营销网络、跨境电子商务的物流支撑体系，为国内企业“走出去”和开展全球业务提供物流服务保障。支持优势物流企业加强联合，构建国际物流服务网络，打造具有国际竞争力的跨国物流企业。\u000B　　7．大力发展绿色物流。\u000B　　优化运输结构，合理配置各类运输方式，提高铁路和水路运输比重，促进节能减排。大力发展甩挂运输、共同配送、统一配送等先进的物流组织模式，提高储运工具的信息化水平，减少返空、迂回运输。\r\n（二）专业人才社会需求分析 \r\n物流业已经被大多数企业重视和依重，物流管理的经济价值已经被社会广泛认可并产生极大的市场需求。作为一个传统产业的一次重要转型，正逐渐地改变着中国的方方面面。据有关资料显示，2008年物流管理人才跃居人才需求第一位；2010年上半年有报告显示物流管理人才需求已成热门；2013年，物流以及相关行业的人才需求一直保持全年行业需求的最高，招聘始终维持在20%左右的市场份额。在各大招聘网站的排行榜上招聘最多的行业是物流以及相关行业的职业。物流管理行业除了呈现薪资起点高、增长速度快的特点外，报告同时发现，中国物流管理从业人员人才缺口将持续走高，仅2008年中国企业新增物流以及相关行业用人需要超过230万，预示着物流管理专业人才就业市场宽广。特别是国发〔2015〕32号 国务院关于大力推进大众创业万众创新若干政策措施的意见中提到依托“互联网+”、大数据等，推动各行业创新商业模式，建立和完善线上与线下、境内与境外、政府与市场开放合作等创业创新机制。这些都需要大量的物流专业人才。\r\n（三）学校专业建设发展分析——需要物流管理专业教学名师\r\n1.学校物流管理教学与专业教师现状\r\n广东省技师学院广州校区在校学生4300人，其中物流管理专业学生270人，物流管理实训室2间，是学院重点建设的专业，广州校区的物流管理专业经过几年发展已经从传统教学，向一体化教学模式转变，目前广州校区尝试以赛促教，校企合作等多种方式培养物流管理专业人才，以往培养的物流管理人才深受企业好评，人才供不应求，校区现有专业教师5人，其中大学本科5人，物流管理技师5人，从事物流管理教学5人，从人才结构上来看，广州校区从事物流管理专业的教师，全部科班，有两名在读硕士研究生，教师的学历水平还有很大的提升空间，从专业能力上来看，大多数教师从校门到校门普遍缺乏实际操作经验，突出表现在物流管理实战能力不强，与技能名师要求相差较远、与企业对人才素质的要求不相匹配；也与正在推行的工学一体化教学改革的要求不相适应，所以提升物流管理专业教师的能力迫在眉捷。\r\n2.学校内涵发展的需要\r\n自2014年省厅提出内涵发展年以来，广东省技师学院也从原来的扩规模，转到控制规模，内涵发展上来。学院在十二五发展规划中把实现学校的内涵发展作为主要目标。学校从内涵发展的需要，一个是提升学生的内涵，学校现在控制招生的人数，通过设置招生“门槛”来提升学生的内涵。在教师队伍的内涵建设上，学院也采措了很多措施也来提升教师的专业能力和专业水平，现在省级技工教育强师工程的实施将会推动师资队伍提升，有利于提高专业人才培养质量，提升学生服务社会的专业能力，培养更多高素质技能人才的需要，满足区域经济转型升级的需要，项目的建设必要。\r\n五、项目可行性\r\n（一）受助对象本人符合项目要求\r\n王怀术，物流管理中级讲师，物流师，采购师，中级经济师，1983年出生，2008年毕业于北京师范大学珠海分校物流管理专业，获管理学学士学位，在读北京物资学院物流工程硕士研究生，现为广州校区物流专业组长。该同志忠诚党的教育事业，热爱本职工作，爱岗敬业，刻苦钻研业务，专业知识厚实。有事业心和使命感，一直承担大负荷的工作量。在教学、科研和育人工作中都取得了较好的成绩。\r\n在教学上，十分注重对学生综合素质的培养，精益求精地做好每一教学环节的工作。近年来，主讲过《物流学与管理学》、《营销学》、《物流技术学》、中、高职《仓储学》、《运输与包装》等一体化课程，所授课程倍受学生的欢迎和同行的好评，连续教学评议第一，历次课堂教学质量评价均为优秀。2013年以来被学校任为物流专业组长。在教科研方面发表论文4篇，主编教材2本，参与编写教材4本，习题册2本。\r\n在广东省物流师技能大赛中，2013年荣获团体二等奖、学生个人一等奖、二等奖、王怀术荣获教师个人二等奖、王怀术荣获优秀指导老师称号；2014年荣获团体一等奖，学生个人一等奖、二等奖、参赛教师名列教职组第三名荣获经济创新能手称号，王怀术荣获优秀指导老师称号；2015年团体二等奖，参赛教师荣获广东省劳动技术能手称号；其次，包含手动叉车比赛、包装比赛、特殊物品包装比赛、分拣竞赛等等校内教学竞赛紧锣密布的开展起来，使得学生兴趣一度达到狂热的境界；接着，在深入解读国家、广东省物流师考证要点、经过对历年考试知识点的总结和研究，改版校本教材，针对不同级别编写校本习题册——《物流员考证习题集》和《助理物流师考证习题集》；随后，2013年开展了物流专业的营销学全省示范课——王怀术老师担主讲老师，获得广泛好评；2014年正式开启了每年一度的校内展销活动，学生热血沸腾，积极响应和参与；2015年开展了物流专业叉车方向的全省师资培训，获得参与老师的一致好评；最后，根据一体化教学改革的探索进行，2014年第一本物流专业的校本教材——《物流学与管理学》顺利应用于教学中，对一体化教学的顺利展开铺垫了基础。\r\n从教八年来，本人牢记“学为人师，行为世范”的校训，为学校拔尖的教学骨干。因此，该老师完全符合教师资助项目资助对象条件要求，通过教师资助项目的实施，一定能达到提升自身能力素质和帮助其他教师提升能力素质的目的。\r\n（二）受助对象所在教学系的实习场地满足强师计划的实施\r\n校区物流管理类实训室有：物流实训室1间，模拟销售终端1间，叉车训练场地1块。\r\n综上，受助对象本人具有一定的专业优势和教学经验，有学校深厚的专业底蕴和文化积淀，有强大的师资支持，有一流的实训设备保障，本项目在此可行。\r\n六、资金绩效目标表\r\n        王怀术教师资助        项目绩效目标表预期产出产出计划培训结业证书\r\n论文1篇\r\n企业实践材料\r\n举办培训班1次\r\n以老带新总目标：胜任对内对外的师资培训、制定物流管理专业建设发展方案、成立物流管理精英团队。 提交相关资料及证书年度阶段性目标：前六个月参加专业技能培训、教学方面培训（2.5万元左右）；后六个月举办校内培训班及参与企业实践、制定新的专业规划、编写一体化计划教材和撰写专业论文（2.5万左右）效率计划 项目实施进度计划项目实施内容开始时间完成时间取得相关结业证书并提供相关资料\r\n专业技能培训2017.12017.6专业教学培训2017.32017.6编写教材2017.82017.12制定专业规划和撰写专业论文2017.72017.12校内专业培训班2017.82017.12参与企业实践2017.72017.8预期效果预期社会经济效益指标类别个性化指标上年度实际水平本年度计划完成水平指标解释及计算公式说明提供相关证明材料社会效益校内专业培训100% 0人1次以上校内培训合格反映项目实施直接产生的社会、经济、生态效益等，根据项目属性特点，可选择其中一或多项效益，研究设置个性化指标及其目标值。参与实践完成率100%0天15天以上寒假1-2周,暑假4-6周。审核意见省级主管部门审核意见\u000B                      审核人：    单位公章       年  月  日第三方机构审核意见\u000B                      审核人：    单位公章       年  月  日省财政厅审核意见\u000B                      审核人：    单位公章       年  月  日注：各申报单位个性化指标可自行根据项目特点设置指标，指标设置应可考核、可量化，能够与项目事后绩效评价相对接。 经济效益和生态效益确实无法设置指标的，可不设置。七、资金预算书\r\n   王怀术教师资助项目  资金预算及考核指标\r\n项目\u000B名称建设内容具体项目专项资金预算(万元)考核指标王怀术教师资助项目提升专业能力高等院校学习、进修1.51.学习结业证明\r\n2.企业实践15天以上过程资料企业学习与实践提升教科研能力主持物流管理专业建设11.发表论文1篇以上              2.专业建设相关资料 \r\n3.攻关课题资料                  与企业开展横向课题研究发表论文提升专业教学及培训能力教学方法培训11.培训结业证书\r\n2.订阅获购买教学书籍、杂志\r\n3．校本教材一体化课程构建与实施培训购买书籍、资料编写一体化教材（校本）提升职业生涯规划能力参加专业能力师资培训0.5培训结业证书承接师资培训\r\n任务举办培训班1举办培训班1次以上，提供开展培训相关资料；\r\n开展校内专业培训活动请专家讲座合计5八、主要佐证材料\r\n（一）资历一览表（附件如下）\r\n序号证书1毕业证2学位证书3职称证书4技能等级证书5其他培训证书资历证明\r\n（二）王怀术老师荣誉一览表\r\n序号年度奖项颁发单位12009年多媒体课件制作 三等奖广东省高级技工学校22010年全国说课大赛优等奖中国技术教育委员会物流教育协会32012年广东省物流师技能大赛教师组三等奖广东省物流大赛组委会42013年中国职工教育和职业培训协会优秀科研成果中国职工教育和职业培训协会52013年广东省物流师技能大赛团体二等奖\r\n个人二等奖、优秀指导教师广东省物流大赛组委会62013年一体化教学论文评比广东省技师学院72014年广东省物流师技能大赛\r\n优秀指导教师广东省物流大赛组委会荣誉及教科研成果证明\r\n（三）王怀术老师教科研成果一览表\r\n序号年度奖项颁发单位12009年多媒体课件制作 三等奖广东省高级技工学校22010年全国说课大赛优等奖中国技术教育委员会物流教育协会32012年广东省物流师技能大赛教师组三等奖广东省物流大赛组委会42013年中国职工教育和职业培训协会优秀科研成果中国职工教育和职业培训协会52013年广东省物流师技能大赛团体二等奖\r\n个人二等奖、优秀指导教师广东省物流大赛组委会62013年一体化教学论文评比广东省技师学院72014年广东省物流师技能大赛\r\n优秀指导教师广东省物流大赛组委会广东省技师学院\r\n二0一六年十月\r\n"

    print json.dumps(art_get_phase(content),ensure_ascii=False,indent=1)
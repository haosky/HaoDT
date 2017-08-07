# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

#查找某个公司的法人对应的父母
'''MATCH p=(c)-[r1:MotherOf|FatherOF]-(a)-[r:FRForQY]->(e { NAME: "广东道生科技股份有限公司"}) return  p limit 25'''

#查找某个公司的股东对应的父母
'''MATCH p=(c)-[r1:MotherOf|FatherOF]-(a)-[r:GuDonOf]->(e { NAME : "海能达通信股份有限公司"}) return p limit 25'''
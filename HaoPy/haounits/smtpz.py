# -*- coding: utf-8 -*-
from smtplib import SMTP
from smtplib import SMTPRecipientsRefused
from poplib import POP3_SSL
import time

__author__ = 'hao'
smtpserver = 'smtp.zoho.com.cn'
pop3server = 'pop.zoho.com.cn'
username ='aho@zoho.com.cn'
#: smtp.zoho.com.cn, 端口: 465, SSL
password = '*********'

# 开始接收邮件

# 收信服务器: imap.zoho.com.cn, 端口: 993, SSL
# 发送服务器: smtp.zoho.com.cn, 端口: 465, SSL

M = POP3_SSL(pop3server,port=995)
M.user(username)
M.pass_(password)

print M.retr(1)







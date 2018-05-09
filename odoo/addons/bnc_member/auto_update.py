# -*- coding: utf-8 -*-
import xmlrpclib

# 本地环境
HOST = '192.168.168.169'
PORT = 8069
DB = 'bnc'
USER = 'admin'
PASS = '..'

# HOST='127.0.0.1'
# PORT = 8069
# DB = 'bnc'
# USER = 'admin'
# PASS = '..'


url = 'http://%s:%d/xmlrpc/common' % (HOST, PORT)

sock = xmlrpclib.ServerProxy(url)
uid = sock.login(DB, USER, PASS)

print "UID=%d" % (uid)

urlx = 'http://%s:%d/xmlrpc/object' % (HOST, PORT)
sock = xmlrpclib.ServerProxy(urlx)
# sock.execute(DB,uid,PASS,'proc.sync.bnc.member','procure_sync_bnc',False)
# sock.execute(DB,uid,PASS,'proc.sync.jsport','procure_sync_jsport',False)
# sock.execute(DB,uid,PASS,'proc.sync.buynow','proc_sync_buynow_all', False)
# sock.execute(DB,uid,PASS,'proc.sync.eservices','sync_eservices_sales', False)

sock.execute(DB, uid, PASS, 'proc.sync.2dfire', 'proc_sync_2dfire_all', False)

# sock.execute(DB,uid,PASS,'proc.sync.2dfire','sync_2dfire_sales', False)
# sock.execute(DB,uid,PASS,'proc.sync.2dfire','sync_2dfire_product', False)
# sock.execute(DB,uid,PASS,'proc.sync.2dfire','interface_2dfire_to_bnc_category', False)
# sock.execute(DB,uid,PASS,'proc.sync.2dfire','interface_2dfire_to_bnc_product', False)
# sock.execute(DB,uid,PASS,'proc.sync.2dfire','interface_2dfire_to_bnc_sales', False)


# sock.execute(DB,uid,PASS,'proc.sync.yinbao','sync_yinbao', False)
# sock.execute(DB,uid,PASS,'proc.sync.yinbao','interface_yinbao_to_bnc_category', False)
# sock.execute(DB,uid,PASS,'proc.sync.yinbao','interface_yinbao_to_bnc_product', False)
# sock.execute(DB,uid,PASS,'proc.sync.yinbao','interface_yinbao_to_bnc_sales', False)


# print day1job

# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#http://www.pospal.cn/openplatform/productapi.html
import json
import time
import datetime
import requests
import sys
from odoo import api, fields, models
import hashlib
import types
from bn_2dfire_common import *
from bn_2dfire_tools import *

class bn_2dfire_menu(models.Model):
    _name = 'bn.2dfire.menu'
    code=fields.Char(string=u'商品唯一标识')
    name=fields.Char(string=u'商品名称')    
    entityId=fields.Char(string=u'店entity号码')
    Price=fields.Float(string=u'零售价') 
    soldout=fields.Char(string=u'soldout') 
    hot=fields.Char(string=u'hot') 
    sort=fields.Char(string=u'库存')     
    reserve=fields.Char(string=u'会员价格')
    isInclude=fields.Char(string=u'isInclude')
    store_code=fields.Char(string=u'门店代号') 
    store_name=fields.Char(string=u'门店名称')  
     
    @api.model
    def search_bycode(self, code): 
        res =self.search([('code', '=',code)])
        return res

class bn_2dfire_menu_kind(models.Model):
    _name = 'bn.2dfire.menu.kind'
    code = fields.Char(string=u'分类编码')
    name = fields.Char(string=u'分类名称')
    lastver = fields.Integer(string=u'版本号')
    kindid = fields.Char(string=u'分类ID')
    parentid = fields.Char(string=u'上级分类')
    store_code=fields.Char(string=u'门店代号')
    store_name=fields.Char(string=u'门店名称')


    @api.model
    def search_bycode(self, code):
        res = self.search([('code', '=', code)])
        return res

    def get_2dfire_shop_from_api(self):
        print('get_2dfire_shop_from_api')
        # _logger.info('get_2dfire_product_from_api')
        # MY_URL = self.env['bn.2dfire.url'].search([('code', '=', 'shoplistv20')])
        # MY_URL ={
        #      # "bn_2dfire_function_method" : 'com.dfire.open.item.menu.kind.query',
        #      "bn_2dfire_function_method" : 'com.dfire.open.item.menu.query',
        #      "bn_2dfire_function_api" : 'http://gateway.2dfire.com',
        #  }

        MY_URL ={
             "bn_2dfire_function_method" : 'dfire.total.menu.query',
             "bn_2dfire_function_api" : 'http://open.2dfire.com/router',
         }
        #
        #
        # MY_URL = {
        #     "bn_2dfire_function_method": 'dfire.shop.order.list',
        #     "bn_2dfire_function_api": 'http://open.2dfire.com/router',
        # }

        # MY_URL ={
        #      "bn_2dfire_function_method" : 'com.dfire.open.shop.order.query',
        #      "bn_2dfire_function_api" : 'http://gateway.2dfire.com',
        #  }




        MY_APPID = self.env['bn.2dfire.appid'].search([('code', '=', 'shanghai')])

        ewh_request = bn_2dfire_connect_Request()
        MY_DATA = {
            "method": str(MY_URL['bn_2dfire_function_method']),
            # "appKey": MY_APPID['bn_2dfire_app_key'],
            "appKey": MY_APPID['bn_2dfire_app_key'],
            "entityId":str('131363'),
            "v": "1.0",
            "timestamp": str(int(time.time() * 1000)),
            # "currDate": '20200101',
            "lang": '',
        }

        recordset = ewh_request.get_json(MY_URL['bn_2dfire_function_api'], MY_APPID, MY_DATA)
        if recordset is not None:
            if 'data' in recordset:
                # _logger.info(recordset)
                print("hello")
                # self.insert_2dfire_shops(recordset['data']['data'])

        return True



    # def get_2dfire_menu_kind_from_api(self, procdate):
    #     print 'get_2dfire_menu_kind_from_api'
    #     print procdate
    #     MY_URL = self.env['bn.2dfire.url'].search([('code', '=', 'orderlist')])
    #
    #     #        procdate= datetime.datetime.now() - datetime.timedelta(days=1)
    #     stores = self.env['bn.2dfire.branchs'].get_vaild_branchs()
    #
    #
    #
    #     for store in stores:
    #         appid = store['appids']
    #         para = {
    #             'para_my_url': MY_URL,
    #             'para_my_appid': appid,
    #             'para_my_store': store,
    #             'para_connection': self,
    #         }
    #
    #         data = {
    #             "currdate": procdate,
    #             "orderids": None
    #         }
    #
    #         recordset = bn_2dfire_connect_api(para).Get_ResultAll(data)
    #         if recordset is not None and recordset.has_key('model'):
    #             print('hello')
    #             # insert_2dfire_order(self, recordset['model'], store)
    #
    #     return True




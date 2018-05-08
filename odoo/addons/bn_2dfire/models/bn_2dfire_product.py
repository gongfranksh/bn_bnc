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

class bn_2dfire_product(models.Model):
    _name = 'bn.2dfire.product'
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
         
         
         

         
def get_2dfire_product_from_api(self):
        return True  
      
def get_2dfire_product_from_orderdetail(self,procdate):
        print 'get_2dfire_product_from_orderdetail'
        currdate= procdate.strftime("%Y-%m-%d").replace('-', '')
        ordervos=self.env['bn.2dfire.order.ordervo'].search([('innerCode', 'like',currdate+'____')])
        range_vo=[]
        for vo in ordervos:
            range_vo.append(str(vo['orderId']))
        orderdetails=self.env['bn.2dfire.order.orderlist'].search([('orderId', 'in',range_vo)])
        for ord in orderdetails:
            print ord
            vals={
                'code':ord['menuId'],
                'name':ord['name'],
                'Price':ord['price'],
                'entityId':ord['entityId'],
                'store_code':ord['entityId'],                
                }
            c01=self.env['bn.2dfire.product'].search([('code', '=',ord['menuId'])])
            if not c01 :
                self.env['bn.2dfire.product'].create(vals)
        
        

        print procdate
        return True  


    
def insert_2dfire_product(self,recordsets,certifate):
        return True  
    

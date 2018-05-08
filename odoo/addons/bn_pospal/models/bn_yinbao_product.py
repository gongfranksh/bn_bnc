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
from bn_yinbao_comm import *
import logging

_logger = logging.getLogger(__name__)


class bn_yinbao_category(models.Model):
    _name = 'bn.yinbao.category'
    code=fields.Char(string=u'商品分类唯一标识')
    name=fields.Char(string=u'商品分类名称')    
    parentuid=fields.Char(string=u'当前商品分类的父分类的唯一标识' , default=None)
    store_code=fields.Char(string=u'门店代号') 
    store_name=fields.Char(string=u'门店名称')   
  
    @api.model
    def search_bystore(self, code): 
        res =self.search([('store_code', '=',code)])
        return res
    
    def get_update_records(self): 
        res =self.search([])
        return res    

    def get_1st_level_category_records(self): 
        res =self.search([('parentuid','=',None)])
        return res  

    def get_end_level_category_records(self): 
        res =self.search([('parentuid','<>',None)])
        return res  

class bn_yinbao_product(models.Model):
    _name = 'bn.yinbao.product'
    code=fields.Char(string=u'商品分类唯一标识')
    name=fields.Char(string=u'商品分类名称')    
    categoryUid=fields.Char(string=u'当前商品分类的父分类的唯一标识')
    barcode=fields.Char(string=u'条形码')     
    buyPrice=fields.Float(string=u'买入价')   
    sellPrice=fields.Float(string=u'零售价') 
    supplierUid=fields.Char(string=u'供应商') 
    productionDate=fields.Char(string=u'发布日期') 
    stock=fields.Float(string=u'库存')     
    pinyin=fields.Char(string=u'拼音')
    enable=fields.Char(string=u'使用状态') 
    customerPrice=fields.Float(string=u'会员价格')
    isCustomerDiscount=fields.Char(string=u'是否会员折扣')
    description=fields.Char(string=u'描述')   
    store_code=fields.Char(string=u'门店代号') 
    store_name=fields.Char(string=u'门店名称')  
     
    @api.model
    def search_bycode(self, code): 
        res =self.search([('code', '=',code)])
        return res   
         
         
         

         
def get_yinbao_catagory_from_api(self):
        MY_URL=self.env['bn.yinbao.url'].search([('code', '=','queryProductCategoryPages')])
        certifate=self.env['bn.yinbao.appid'].get_vaild_appid()
        for appid in certifate:
            maxid=self.env['bn.yinbao.log'].get_maxid(appid['code'],MY_URL)
            if maxid is  None:
                maxid_key=0
            else :
                maxid_key=maxid['bn_parameterValue']
            para={
                'para_my_url':MY_URL,
                'para_connection':self,
                }
                
            recordset=bn_yinbao_connect_api(para).Get_ResultAll(appid, {'appId': str(appid['bn_yinbao_appid']),
                                            'postBackParameter':
                                                {'parameterType': 'LAST_RESULT_MAX_ID',
                                                 'parameterValue': maxid_key}
                                            })
            if recordset is not None :     
                insert_yinbao_catagory(self,recordset,appid)

        return True    


def get_yinbao_product_from_api(self):
        MY_URL=self.env['bn.yinbao.url'].search([('code', '=','queryProductPages')])
        certifate=self.env['bn.yinbao.appid'].get_vaild_appid()
        for appid in  certifate:
                    maxid=self.env['bn.yinbao.log'].get_maxid(appid['code'],MY_URL)
                    if maxid is  None:
                            maxid_key=0
                    else :
                            maxid_key=maxid['bn_parameterValue']
                    para={
                                        'para_my_url':MY_URL,
                                        'para_connection':self,
                                        }
                
                    recordset=bn_yinbao_connect_api(para).Get_ResultAll(appid, {'appId': str(appid['bn_yinbao_appid']),
                                            'postBackParameter':
                                                {'parameterType': 'LAST_RESULT_MAX_ID',
                                                 'parameterValue': maxid_key}
                                            })        
                    if recordset is not None :                    
                        insert_yinbao_product(self,recordset,appid)

        return True    

    
def insert_yinbao_catagory(self,recordsets,certifate):
        if (len(recordsets) == 0):
            return
            
        for rec in recordsets:
            res={
                'code' :rec['uid'],
                'name' :rec['name'],
                'parentuid':  rec['parentUid'], 
                'store_code':  certifate['code'], 
                'store_name':  certifate['name'],              
                }
            #检查是插入还是更新            
            r01=self.env['bn.yinbao.category'].search_bystore(rec['uid'])
            if not r01:            
                self.env['bn.yinbao.category'].create(res)
            else:
                r01.write(res)
        return True  
    
def insert_yinbao_product(self,recordsets,certifate):
        if (len(recordsets) == 0):
            return
            
        for rec in recordsets:
            res={
                'code' :rec['uid'],                              
                'name' :rec['name'],
                'isCustomerDiscount' :rec['isCustomerDiscount'],                
                'buyPrice' :rec['buyPrice'],    
                'pinyin' :rec['pinyin'],                    
                'barcode' :rec['barcode'],  
                'categoryUid' :rec['categoryUid'],
                'supplierUid' :rec['supplierUid'],
                'enable' :rec['enable'], 
#                'productionDate' :rec['productionDate'],
                'sellPrice' :rec['sellPrice'],
                'stock' :rec['stock'], 
                'customerPrice' :rec['customerPrice'],                                                                                                                          
                'store_code':  certifate['code'], 
                'store_name':  certifate['name'],              
                }
            #检查是插入还是更新            
            r01=self.env['bn.yinbao.product'].search_bycode(rec['uid'])
            if not r01:            
                self.env['bn.yinbao.product'].create(res)
            else:
                r01.env['bn.yinbao.product'].write(res)
        return True        

        

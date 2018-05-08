# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import time
import datetime
import requests
import sys
from odoo import api, fields, models
import hashlib
import types

class bn_yinbao_appid(models.Model):
    _name = 'bn.yinbao.appid'
    code=fields.Char(string=u'编号',size=200 )
    name=fields.Char(string=u'名称')    
    bn_yinbao_appid=fields.Char(string=u'银豹appid',size=200 )
    bn_yinbao_appkey=fields.Char(string=u'银豹appkey',size=200 )    
    state = fields.Selection([('open', 'New'), ('confirm', 'Validated')], string='Status', required=True, readonly=True, copy=False, default='open')
    company_id = fields.Many2one('res.company',u'公司') 
        
    @api.model
    def search_bycode(self, code): 
        res =self.search([('code', '=',code)])
        return res
        
    @api.model
    def get_vaild_appid(self): 
        res =self.search([('state', '=','confirm')])
        return res

class bn_yinbao_url(models.Model):
    _name = 'bn.yinbao.url'
    code=fields.Char(string=u'编号',size=200 )
    name=fields.Char(string=u'名称')    
    bn_yinbao_function_api=fields.Char(string=u'调用地址',size=500 )
    bn_yinbao_api_type = fields.Selection([('bn_api_yinbao_sales_by_product', 'sales by product '),('bn_api_yinbao_sales_by_payment', 'sales by payment'),('bn_api_yinbao_member', 'Member'),('bn_api_yinbao_Category', 'Category'),('bn_api_yinbao_product', 'product')], string=u'接口类型', required=True,default='bn_api_yinbao_sales_by_product')

    state = fields.Selection([('open', 'New'), ('confirm', 'Validated')], string='Status', required=True, readonly=True, copy=False, default='open')
        
    @api.model
    def search_bycode(self, code): 
        res =self.search([('code', '=',code)])
        return res
    

class bn_yinbao_log(models.Model):
    _name = 'bn.yinbao.log'
    bn_yinbao_appid     = fields.Many2one('bn.yinbao.appid',u'appid')
    bn_yinbao_url       = fields.Many2one('bn.yinbao.url',u'调用地址')
    bn_yinbao_second_id = fields.Char(string=u'第二参数') 
    bn_postBackParameter=fields.Char(string=u'回传参数')
    bn_parameterValue   =fields.Integer(string=u'参数值')    
    @api.model
    def search_bycode(self, code): 
        res =self.search([('code', '=',code)])
        return res   
    
    @api.model
    def get_maxid(self, store_code,query_type): 
        store_id=self.env['bn.yinbao.appid'].search_bycode(store_code).id
        sql=""" 
                        select * 
                        FROM bn_yinbao_log
                        WHERE bn_yinbao_appid = {0}
                            AND bn_yinbao_url = {1}
                            AND "bn_parameterValue" IN (
                            select max("bn_parameterValue") from bn_yinbao_log  
                            where bn_yinbao_appid = {0} and bn_yinbao_url={1} )
                              """
        sql=sql.format(store_id,query_type.id) 
        cr = self._cr         
        cr.execute(sql)
        res=cr.fetchall()
        
        if len(res) <>0:
         return self.env['bn.yinbao.log'].search([('id', '=',res[0][0])])
        else :
          return None
 

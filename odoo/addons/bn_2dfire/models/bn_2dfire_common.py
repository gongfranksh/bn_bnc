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

class bn_2dfire_appid(models.Model):
    _name = 'bn.2dfire.appid'
    code=fields.Char(string=u'编号' )
    name=fields.Char(string=u'名称')    
    bn_2dfire_app_secret=fields.Char(string=u'二维火app_secret' )
    bn_2dfire_app_key=fields.Char(string=u'二维火app_key')    
    state = fields.Selection([('open', 'New'), ('confirm', 'Validated')], string='Status', required=True, readonly=True, copy=False, default='open')
        
    @api.model
    def search_bycode(self, code): 
        res =self.search([('code', '=',code)])
        return res

    def search_byid(self, code): 
        res =self.search([('id', '=',code)])
        return res
            
    @api.model
    def get_vaild_appid(self): 
        res =self.search([('state', '=','confirm')])
        return res


class bn_2dfire_branchs(models.Model):
    _name = 'bn.2dfire.branchs'
    code=fields.Char(string=u'编号')
    name=fields.Char(string=u'名称')  
    appids = fields.Many2one('bn.2dfire.appid',u'使用的appid')  
    state = fields.Selection([('open', 'New'), ('confirm', 'Validated')], string='Status', required=True, readonly=True, copy=False, default='open')
    company_id = fields.Many2one('res.company',u'公司') 
        
    @api.model
    def search_bycode(self, code): 
        res =self.search([('code', '=',code)])
        return res
        
    @api.model
    def get_vaild_branchs(self): 
        res =self.search([('state', '=','confirm')])
        return res




class bn_2dfire_url(models.Model):
    _name = 'bn.2dfire.url'
    code=fields.Char(string=u'编号' )
    name=fields.Char(string=u'名称')    
    bn_2dfire_function_api=fields.Char(string=u'调用地址' )
    bn_2dfire_function_method=fields.Char(string=u'调用方法' )
    bn_2dfire_api_type = fields.Selection([('bn_api_2dfire_order', 'order '),('bn_api_2dfire_order_instance_list', 'order detail'),('bn_api_2dfire_menu_query', 'product')], string=u'接口类型', required=True,default='bn_api_2dfire_order')

    state = fields.Selection([('open', 'New'), ('confirm', 'Validated')], string='Status', required=True, readonly=True, copy=False, default='open')
        
    @api.model
    def search_bycode(self, code): 
        res =self.search([('code', '=',code)])
        return res
    

class bn_2dfire_log(models.Model):
    _name = 'bn.2dfire.log'
    bn_2dfire_appid     = fields.Many2one('bn.2dfire.appid',u'appid')
    bn_2dfire_url       = fields.Many2one('bn.2dfire.url',u'调用地址')
    bn_postBackParameter=fields.Char(string=u'回传参数')
    bn_parameterValue   =fields.Integer(string=u'参数值')    
    @api.model
    def search_bycode(self, code): 
        res =self.search([('code', '=',code)])
        return res   
    
    @api.model
    def get_maxid(self, store_code,query_type): 
        store_id=self.env['bn.2dfire.appid'].search_bycode(store_code).id
        sql=""" 
                        select * 
                        FROM bn_2dfire_log
                        WHERE bn_2dfire_appid = {0}
                            AND bn_2dfire_url = {1}
                            AND "bn_parameterValue" IN (
                            select max("bn_parameterValue") from bn_2dfire_log  
                            where bn_2dfire_appid = {0} and bn_2dfire_url={1} )
                              """
        sql=sql.format(store_id,query_type.id) 
        cr = self._cr         
        cr.execute(sql)
        res=cr.fetchall()
        
        if len(res) <>0:
         return self.env['bn.2dfire.log'].search([('id', '=',res[0][0])])
        else :
          return None
 

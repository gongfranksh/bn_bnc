# -*- coding: utf-8 -*-
# refer by 
# http://www.pospal.cn/openplatform/customerapi.html
# http://host:port/pospal-api2/openapi/v1/customerOpenApi/queryCustomerPages
import json
import time
import datetime
import requests
import sys
from odoo import api, fields, models
import hashlib
import types
import logging

from bn_yinbao_comm import *
_logger = logging.getLogger(__name__)

class bn_yinbao_member(models.Model):
    _name = 'bn.yinbao.member'
    code=fields.Char(string=u'会员唯一标识')
    name=fields.Char(string=u'名称') 
    phone=fields.Char(string=u'电话')    
    birthday=fields.Char(string=u'生日')  
    qq=fields.Char(string=u'qq账号')  
    email=fields.Char(string=u'邮箱') 
    address=fields.Char(string=u'地址') 
    remarks=fields.Char(string=u'备注')     
    store_code=fields.Char(string=u'门店代号') 
    store_name=fields.Char(string=u'门店名称')

    

def get_yinbao_member_from_api(para_self):
        _logger.info("bn =>get_yinbao_member_from_api")    
        MY_URL=para_self.env['bn.yinbao.url'].search([('code', '=','queryCustomerPages')])
        certifate=para_self.env['bn.yinbao.appid'].get_vaild_appid()

        for appid in certifate:
            _logger.info("bn =>get_yinbao_member_from_api %s" % appid['code'] )  
            maxid=para_self.env['bn.yinbao.log'].get_maxid(appid['code'],MY_URL)
            
            if maxid is  None:
                maxid_key=0
            else :
                maxid_key=maxid['bn_parameterValue']
            para={
                'para_my_url':MY_URL,
                'para_connection':para_self,
                }
                
            recordset=bn_yinbao_connect_api(para).Get_ResultAll(appid, {'appId': str(appid['bn_yinbao_appid']),
                                            'postBackParameter':
                                                {'parameterType': 'LAST_RESULT_MAX_ID',
                                                 'parameterValue': maxid_key}
                                            })
            
            if recordset is not None :
                insert(para_self,appid,recordset)
        
        
        
        
        
def insert(para_self,APPID,objs):
        if (len(objs) == 0):
            return
        company = APPID['code']
        company_name = APPID['name']
        for result in objs:
            vals = {
                        'store_code':           company,
                        'store_name':           company_name,
                        'code':            result['customerUid'],
                        'name':            result['name'],
                        'phone':            result['phone'],
                        'birthday':           result['birthday'] if result.has_key('birthday') else '',
                        'email':            result['email'],
                        'address':           result['address'],
                    }
            para_self.env['bn.yinbao.member'].create(vals)


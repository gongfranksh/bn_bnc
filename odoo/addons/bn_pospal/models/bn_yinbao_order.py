# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#http://www.pospal.cn/openplatform/ticketapi.html
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


class bn_yinbao_order(models.Model):
    _name = 'bn.yinbao.order'
    _description = 'bn.yinbao.order'
    store_code=fields.Char(string=u'门店代号') 
    store_name=fields.Char(string=u'门店名称')       
    sn=fields.Char(string=u'编号')
    customerUid=fields.Char(string=u'会员编号')
    sale_datetime=fields.Datetime(string=u'销售日期')      
    totalAmount=fields.Float(string=u'销售金额')        
    totalProfit=fields.Float(string=u'销售毛利')  
    discount=fields.Float(string=u'折扣')      
    rounding=fields.Integer(string=u'小数位数')            
    ticketType=fields.Char(string=u'交易类型')
    invalid=fields.Char(string=u'有效状态')
    payments=fields.One2many('bn.yinbao.order.payment','order_id',u'付款') 
    items=fields.One2many('bn.yinbao.order.detail','order_id',u'商品明细') 
    
class bn_yinbao_order_payment(models.Model):
    _name = 'bn.yinbao.order.payment'
    _description = 'bn.yinbao.order.payment'
    
    code=fields.Char(string=u'编号')
    order_amount=fields.Float(string=u'金额')    
    order_id=fields.Many2one('bn.yinbao.order',u'订单', ondelete='cascade') 


class bn_yinbao_order_detail(models.Model):
    _name = 'bn.yinbao.order.detail'
    _description = 'bn.yinbao.order.detail'
    name=fields.Char(string=u's商品名称')
    buyPrice=fields.Float(string=u'买入价')  
    sellPrice=fields.Float(string=u'卖价')    
    customerPrice=fields.Float(string=u'成交价')    
    quantity=fields.Float(string=u'数量')   
    discount=fields.Float(string=u'折扣') 
    customerDiscount=fields.Float(string=u'客户折扣') 
    totalAmount=fields.Float(string=u'销售金额')          
    totalProfit=fields.Float(string=u'销售毛利')  
    isCustomerDiscount=fields.Integer(string=u'是否为客户折扣')
    productUid=fields.Char(string=u's商品编号')                    
    order_id=fields.Many2one('bn.yinbao.order',u'订单',ondelete='cascade') 

def get_yinbao_sales_from_api(self,period):
    
        MY_URL=self.env['bn.yinbao.url'].search([('code', '=','queryTicketPages')])
        certifate=self.env['bn.yinbao.appid'].get_vaild_appid()
        
        for i in range((period['end']-period['begin']).days+1):
            procdate=period['begin'] +datetime.timedelta(days=i)
            _logger.info("bn=>get_yinbao_sales_from_api %s"  %  str(procdate) )    
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
                                
                
                recordset=bn_yinbao_connect_api(para).Get_ResultAll(
                    appid, {'appId': str(appid['bn_yinbao_appid']),
                            "startTime": procdate.strftime('%Y-%m-%d') +' 0:0:0.0',
                            "endTime":  procdate.strftime('%Y-%m-%d') +' 23:59:59.999',
                            'postBackParameter':
                                                {'parameterType': 'LAST_RESULT_MAX_ID',
                                                 'parameterValue': maxid_key}
                                            })
                if recordset is not None :
                    insert_yinbao_order(self,recordset,appid)

        return True    


def insert_yinbao_order(self,recordsets,certifate):
        if (len(recordsets) == 0):
            return
        for rec in recordsets:
            paratime=datetime.datetime.strptime(rec['datetime'],'%Y-%m-%d %H:%M:%S') - datetime.timedelta(hours=8)
            res={
                'sn' :rec['sn'],
                'customerUid' :rec['customerUid'],
                'sale_datetime' :paratime,                                
                'totalAmount' :rec['totalAmount'],   
                'totalProfit' :rec['totalProfit'], 
                'discount' :rec['discount'], 
                'rounding' :rec['rounding'],
                'ticketType' :rec['ticketType'], 
                'invalid' :rec['invalid'],  
                'store_code':  certifate['code'], 
                'store_name':  certifate['name'],              
                }
            
            for item in rec['items']:
                vals_item=[]
                vals_item.append((0,0,{
                    'name':item['name'],
                    'buyPrice':item['buyPrice'],   
                    'sellPrice':item['sellPrice'],
                    'customerPrice':item['customerPrice'],      
                    'discount':item['discount'],  
                    'totalAmount':item['totalAmount'],                      
                    'totalProfit':item['totalProfit'],                         
                    'isCustomerDiscount':item['isCustomerDiscount'],  
                    'quantity':item['quantity'],                    
                    'productUid':item['productUid'],                    
                    }))

            res['items'] = vals_item
            
            for payment in rec['payments']:
                vals_payment=[]
                vals_payment.append((0,0,{
                    'code':payment['code'],
                    'order_amount':payment['amount'],   
                    }))

            res['payments'] = vals_payment
            
            self.env['bn.yinbao.order'].create(res)
        return True 
    
    
def check_yinbao_order(self,day,certifate):
        sql = """ 
                 delete from  bn_yinbao_order
                 where  to_char(sale_datetime,'yyyy-mm-dd') = '{0}' and store_code='{1}'
                  """
        sql = sql.format(day.strftime('%Y-%m-%d'),certifate['code'])
        cr = self._cr 
        cr.execute(sql)
        return True    
       


       

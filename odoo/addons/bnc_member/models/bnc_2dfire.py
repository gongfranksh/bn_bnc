# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.addons.bn_2dfire.models.bn_2dfire_order import *
from odoo.addons.bn_2dfire.models.bn_2dfire_product import *
from bnc_common import *
import logging

_logger = logging.getLogger(__name__)

TOTAL_DAY=10 
def _get_business(self):
    res=self.env['bnc.business'].get_bnc_business_bycode('cof')  

    return res  
    

def sync_category_to_bnc(self):
    res=self.env['bnc.business'].get_bnc_business_bycode('btw')      
    bnc_root_category(self,res)

    res=self.env['bnc.business'].get_bnc_business_bycode('cof')      
    bnc_root_category(self,res)
        
    return True

def sync_product_to_bnc(self):
#    bnc_root_category(self,self._get_business())
    bnc_insert_product(self)
    return True

def sync_sales_from_api(self,period):
    begin=period['begin']
    end=period['end']
    
    for i in range((end - begin).days+1):
        procday = begin + datetime.timedelta(days=i)
        get_2dfire_order_from_api(self,procday)
    return True

def sync_order_detail_from_api(self,period):
    begin=period['begin']
    end=period['end']
    
    for i in range((end - begin).days+1):
        procday = begin + datetime.timedelta(days=i)    
        get_2dfire_order_detail_from_api(self,procday)

    return True


def sync_product_from_orderlist(self,period):
    begin=period['begin']
    end=period['end']
    
    for i in range((end - begin).days+1):
        procday = begin + datetime.timedelta(days=i)
        get_2dfire_product_from_orderdetail(self,procday)
    return True



def sync_sales_to_bnc(self):
#    bnc_root_category(self,self._get_business())
#    bnc_insert_sales(self)
    return True


def bnc_setparent_category(self):
        return True
    
def bnc_insert_product(self):
#    buids=self.env['bnc.business'].search([('strBuscode','in',['btw'])])
    buids=self.env['bnc.business'].search([('strBuscode','in',['btw','cof'])])
    for buid in buids:
    
        productids=bnc_get_NeedUpdateProduct_byBussinessUnit(self,buid)
        i=0
        for pids in productids:
                i=i+1
                print i,len(productids)
                res= {
                    'code' : pids['code'],
                    'name' : pids['name'],
    #                'spec':spec,
    #                'brand_id':b01,
                    'list_price':pids['Price'],
                    'price':pids['Price'],
    #                'bn_barcode':tmp_code,
                    'sale_ok':True,
                    'default_code': pids['code'],
                    'categ_id':self.env['product.category'].search_bycode(pids['store_code']).id,
    #                'b_category':self.env['product.category'].search_bycode(store_code+'-'+classid[0:4]).id,
    #                'm_category':self.env['product.category'].search_bycode(store_code+'-'+classid[0:6]).id,
    #                'b_sup_id':s01.id,
    #                'timestamp': timestamp,
                    'buid':buid['id'],
                    'store_id':self.env['res.company'].search_bycode(pids['store_code']).id,             
                    }
                #检查是插入还是更新            
                r01=self.env['product.template'].search_bycode(pids['code'])
                if r01:            
                    r01.write(res)
    #                print 'update'
    #                print res            
                else:
                    self.env['product.template'].create(res)
    #                print 'create'
    #                print res
    #        self.set_jsport_category_parent()  

    
    return True
def bnc_insert_sales(self):  
        print 'bnc_insert_sales'
            #proc_days 往前处理几天
        proc_days=TOTAL_DAY
        buids=self.env['bnc.business'].search([('strBuscode','in',['btw','cof'])])
        for buid in buids:

            proc_date_task=check_pos_data_daily(self,proc_days,buid)
#            if db['store_code'] =='02002':
            for d in proc_date_task:
                    if (d['local_records_count'] <> d['remote_records_count']) or (d['local_records_count']==0):                
                       _logger.info("bnc=>2dfire bnc_insert_sales"+d['proc_date']+'====>'+'local have====>'+str(d['local_records_count'])+'     remote have====>'+str(d['remote_records_count'])+'==>need to sync')          

                       print d['proc_date']+'====>'+'local have====>'+str(d['local_records_count'])+'     remote have====>'+str(d['remote_records_count'])+'==>need to sync'
                       delete_pos_data_daily(self,d['proc_date'],buid)
                       insert_pos_data_daily(self,d['proc_date'],buid) 
                    else :
                       _logger.info("bnc=>2dfire bnc_insert_sales"+d['proc_date'] +'====>'+'already done!!!')                                    
                       print d['proc_date'] +'====>'+'already done!!!'
    
        return 
    
    
def delete_pos_data_daily(self,ymd,business):
            exec_sql=""" 
                        delete from pos_order 
                        where to_char(date_order,'yyyy-mm-dd')='{0}' and buid ={1}
                    """
            exec_sql=exec_sql.format(ymd,business.id)  
            cr = self._cr 
            cr.execute(exec_sql)
            return True
                
 
def insert_pos_data_daily(self,procdate,business):
    
        stores=bnc_get_storescode_byBussinessUnit(self,business)    
        currdate=procdate.replace('-','')
        order_vo_list = self.env['bn.2dfire.order.ordervo'].search([('innerCode', 'like',currdate+'____'),('entityId','in',stores)])
        i=0
        for  ov in order_vo_list:
            i=i+1
            print  i,len(order_vo_list) 

            vals=[]
            res=[]
#            para_time =datetime.datetime.strptime(yb['sale_datetime'],'%Y-%m-%d %H:%M:%S') - datetime.timedelta(hours=8)
            
        
            br01=self.env['res.company'].search_bycode(ov['entityId']).id
                
            if  ov['memo'] :
                phone=ov['memo'][1:12]
                rs01=self.env['bnc.member'].get_mem_by_phone(phone)
                if rs01 :
                    m01=self.env['res.partner'].search_bycardid(rs01['strBncCardid']).id
                    
                else:
                    m01=None
            else :
                m01=None
            
            print  ov['entityId']
            print ov['innerCode'][0:8]+ ov['endTime'][0:4]
            saledate= bnc_char_to_date(ov['endTime'])
              
            pos_order_line = self.env['bn.2dfire.order.orderlist'].search([('orderId','=',ov['orderId'])])   
            for pl in pos_order_line:
                
                inter_pcode= pl['menuId']
                res.append((0,0,{
                    'product_id':self.env['product.product'].search([('default_code', '=',inter_pcode)]).id,
                    'price_unit':pl['price'],
                    'qty':pl['num'], 
                    }))
                

            vals={
                'date_order': saledate,
                'company_id': br01,
                'user_id':None,
                'note':ov['orderId'],
                'partner_id':m01,
                'pos_reference':ov['orderId'],
                'lines':res,
                'state':'done',
                'buid':business.id,
                'strstoreid':ov['entityId'], 
                }
            
            if business['strBuscode']=='btw':
                vals.update({'user_id':self.env['res.users'].search([('login', '=','btws-users')]).id })
                
            if business['strBuscode']=='cof':
                vals.update({'user_id':self.env['res.users'].search([('login', '=','caf-users')]).id })

            master=self.env['pos.order'].create(vals)
        
        return True

      
def check_pos_data_daily(self,para_interval,business):
        vals=[]           
        end_date= datetime.datetime.now()        
        for i in range(1,para_interval+1):
            servercnt=0
            localcnt=0
            day= end_date - datetime.timedelta(days=i)
            currdate=day.strftime('%Y-%m-%d').replace('-','')
            print day              
            exec_sql=""" 
                        select count(*)  from pos_order 
                        where to_char(date_order,'yyyy-mm-dd')='{0}' and buid ={1} 
                    """
            exec_sql=exec_sql.format(day.strftime('%Y-%m-%d'),business.id)  
            cr = self._cr 
            cr.execute(exec_sql)
            
            for local_count  in cr.fetchall():
                localcnt=local_count[0]
            stores=bnc_get_storescode_byBussinessUnit(self,business)            
            orderlist=self.env['bn.2dfire.order.ordervo'].search([('innerCode', 'like',currdate+'____'),('entityId','in',stores)])
            remote_cnt = len(orderlist)
            vals.append({'proc_date':day.strftime('%Y-%m-%d'),'local_records_count':localcnt,'remote_records_count':remote_cnt})       

        return vals
    

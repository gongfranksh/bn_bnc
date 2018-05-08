# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from bnc_common import *
from bn_eservice_tools import *

import logging
import threading

_logger = logging.getLogger(__name__)


   
def _get_business(self):
    res=self.env['bnc.business'].get_bnc_business_bycode('hos')  
    return res  
    

def sync_category_to_bnc(self):
    bnc_root_category(self,res)

    res=self.env['bnc.business'].get_bnc_business_bycode('cof')      
    bnc_root_category(self,res)
        
    return True

def sync_product_to_bnc(self):
#    bnc_root_category(self,self._get_business())
    return True

def sync_sales_from_api(self,period):
    begin=period['begin']
    end=period['end']
    
    for i in range((end - begin).days+1):
        procday = begin + datetime.timedelta(days=i)
    return True

def sync_order_detail_from_api(self,period):
    begin=period['begin']
    end=period['end']
    for i in range((end - begin).days+1):
        procday = begin + datetime.timedelta(days=i)    
    return True


def sync_product_from_orderlist(self,period):
    begin=period['begin']
    end=period['end']
    
    for i in range((end - begin).days+1):
        procday = begin + datetime.timedelta(days=i)
    return True

def sync_sales_to_bnc(self,period):
    begin=period['begin']
    end=period['end']
    _logger.info("bnc=>computer_repaire sync_sales_to_bnc")          
    
    proc_date_task=check_pos_data_daily(self,period,self._get_business())  

    for d in proc_date_task:
        if (d['local_records_count'] <> d['remote_records_count']) or (d['local_records_count']==0):                
                        print d['proc_date'].strftime('%Y-%m-%d')+'====>'+'local have====>'+str(d['local_records_count'])+'     remote have====>'+str(d['remote_records_count'])+'==>need to sync'
                        _logger.info("bnc=>computer_repaire sync_sales_to_bnc"+ d['proc_date'].strftime('%Y-%m-%d')+'====>'+'local have====>'+str(d['local_records_count'])+'     remote have====>'+str(d['remote_records_count'])+'==>need to sync')          

                        delete_pos_data_daily(self,d['proc_date'],self._get_business())
                        records=get_sales_record(d['proc_date'])
                        proc_sales_record(self,records)
        else :                                  
                       _logger.info("bnc=>computer_repaire sync_sales_to_bnc"+d['proc_date'].strftime('%Y-%m-%d') +'====>'+'already done!!!')
                       print d['proc_date'].strftime('%Y-%m-%d') +'====>'+'already done!!!'
        

        
        
        
    return True


def bnc_setparent_category(self):
        return True
    
def get_sales_record(procday): 
        print    'get_sales_record'
        print procday
        sql="""
          SELECT rc.shop_id,
                e.id,
                rc.name,
                e.closed_date::date,
                e.incident_number,
                esc.phone_number1,
                COUNT(DISTINCT e.id),
                sum(e.charge_amt),
                v.lookup_code,
                v.meaning
            FROM eservice_sr_incidents e
            LEFT JOIN res_company rc ON e.company_id=rc.id
            LEFT JOIN eservice_sr_customers esc ON e.customer_id=esc.id
            LEFT JOIN eservice_lookup_values v ON e.sr_prod_type_id=v.id
            WHERE e.closed_date::date BETWEEN '{0}' AND '{1}' AND e.state in ('done','reopen')
            GROUP BY rc.id,v.id,e.id,e.closed_date::DATE,e.incident_number,esc.phone_number1;
            """
        sql=sql.format(procday.strftime('%Y-%m-%d')+' 00:00:00' , procday.strftime('%Y-%m-%d')+ ' 23:59:59')
        con1=bn_eservice_connect()
        records=con1.exec_return(sql)
        return records
    
def proc_sales_record(self,salerecords):
        print 'proc_sales_record'

        bus01=self.env['bnc.business'].get_bnc_business_bycode('hos')
        
        
        if not self.env['product.category'].search_bycode(bus01['strBuscode']):
            res= {
                'code' : bus01['strBuscode'],
                'name' : bus01['strBusName'],
                'buid':bus01['id'],

                }
            pd=self.env['product.category'].create(res).id
            pc=self.env['pos.category'].create(res).id
        else:
            pd=self.env['product.category'].search_bycode(bus01['strBuscode']).id
            pc=self.env['pos.category'].search_bycode(bus01['strBuscode']).id  
                   
                   
        i=0  
        
                
        for (storeid,eid,storname,closedate,code,phone,count,amount,productcode,productname) in salerecords:
            i=i+1
            print i ,len(salerecords)
            
            com01=self.env['res.company'].search([('bncode','=',bus01['strBuscode']+storeid)]).id
            
            m01=None
            if len(phone)>=11:
                phoneid=phone[0:11]
                member=self.env['bnc.member'].search([['strPhone','=',phoneid]])
                if   member:
                    m01=self.env['res.partner'].search_bycardid(member['strBncCardid']).id 
                else:
                    m01=None
            
            res= {
                    'code' : bus01['strBuscode']+'-'+productcode,
                    'name' : bus01['strBuscode']+'-'+productcode+'-'+productname,
                    'sale_ok':True,
                    'default_code': bus01['strBuscode']+'-'+productcode,
                    'categ_id':pd,
                    'buid':bus01['id'],
                    'store_id':com01,             
                    }
            
            #检查是插入还是更新  
            inter_pcode=bus01['strBuscode']+'-'+productcode 
                     
            r01=self.env['product.template'].search_bycode(inter_pcode)  
            if not r01:
                val={
                    'product_tmpl_id':self.env['product.template'].create(res).id
                    }
                
                prod_tmp=self.env['product.product'].create(val).id
            else :
                prod_tmp=self.env['product.product'].search([('default_code', '=',inter_pcode)]).id
                
            orerlines=[]    
            orerlines.append((0,0,{
                    'product_id':prod_tmp,
                    'price_unit':amount,
                    'qty':count, 

                }))
            vals={
                'date_order': closedate,
                'company_id': com01,
                'user_id':self.env['res.users'].search([('login', '=','hos-users')]).id,
                'note':code,
                'partner_id':m01,
                'pos_reference':code,
                'lines':orerlines,
                'state':'done',
                'buid':bus01.id,
                'strstoreid':bus01['strBuscode']+'-'+storeid, 
                }
            master=self.env['pos.order'].create(vals)   
        
        return True

def delete_pos_data_daily(self,ymd,business):
            exec_sql=""" 
                        delete from pos_order 
                        where to_char(date_order,'yyyy-mm-dd')='{0}' and buid ={1}
                    """
            exec_sql=exec_sql.format(ymd.strftime('%Y-%m-%d'),business.id)  
            cr = self._cr 
            cr.execute(exec_sql)
            return True


def check_pos_data_daily(self,period,business):
    begin=period['begin']
    end=period['end']
    vals=[]           
    for i in range((end - begin).days+1):
            procday = begin + datetime.timedelta(days=i)        
            servercnt=0
            localcnt=0
            currdate=procday.strftime('%Y-%m-%d').replace('-','')
            
            
            
            print procday              
            exec_sql=""" 
                        select count(*)  from pos_order 
                        where to_char(date_order,'yyyymmdd')='{0}' and buid ={1} 
                    """
            exec_sql=exec_sql.format(currdate,business.id)  
            cr = self._cr 
            cr.execute(exec_sql)
            for local_count  in cr.fetchall():
                localcnt=local_count[0]


            sql="""
                SELECT count(*)
                FROM eservice_sr_incidents e
                LEFT JOIN res_company rc ON e.company_id=rc.id
                LEFT JOIN eservice_sr_customers esc ON e.customer_id=esc.id
                LEFT JOIN eservice_lookup_values v ON e.sr_prod_type_id=v.id
                WHERE e.closed_date::date BETWEEN '{0}' AND '{1}' AND e.state in ('done','reopen');
                """
            sql=sql.format(procday.strftime('%Y-%m-%d')+' 00:00:00' , procday.strftime('%Y-%m-%d')+ ' 23:59:59')
            con1=bn_eservice_connect()
            records=con1.exec_return(sql)
            for rcnt in records:   
                servercnt= rcnt[0]
                
            remote_cnt=servercnt
            vals.append({'proc_date':procday,'local_records_count':localcnt,'remote_records_count':remote_cnt})       

    return vals
    
def proc_branch(self):
        print 'proc_branch'

        bus01=self.env['bnc.business'].get_bnc_business_bycode('hos')
        sql="""
                select shop_id,"name" from res_company where shop_id is not null
                """
        sql=sql.format()
        con1=bn_eservice_connect()
        records=con1.exec_return(sql)
        for (storeid,storname) in records:   
        
            cp=self.env['res.company'].search([('bncode','=',bus01['strBuscode']+storeid)])
            if not cp:
                res={
                        'name':bus01['strBusName']+storname,
                        'bncode':bus01['strBuscode']+str(storeid),
                        'buid':bus01.id,
                        }
                self.env['res.company'].create(res)
        return True

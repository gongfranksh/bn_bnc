# -*- coding: utf-8 -*-
import logging
import threading
import datetime

from odoo import api, models, tools, registry
from odoo.addons.bnc_member.models.bnc_2dfire import *

#from odoo.addons.bn_pospal.models import  *


#from idlelib.SearchEngine import get

_logger = logging.getLogger(__name__)

# begin_day = 7
begin_day = 2
end_day = 1

class proc_sync_2dfire(models.TransientModel):
    _name = 'proc.sync.2dfire'
    _description = 'proc.sync.2dfire'

    #获取事业部代码
    @api.model    
    def _get_business(self):
        res=self.env['bnc.business'].get_bnc_business_bycode('cof')  
        return res  
    
    
    def sync_2dfire_sales(self):
        
        
        print 'sync_2dfire_sales'

        # bg = '2019-01-17 00:00:00'
        # beg=datetime.datetime.strptime(bg, "%Y-%m-%d %H:%M:%S")
        #
        # ed = '2019-01-17 23:59:59'
        # end = datetime.datetime.strptime(bg, "%Y-%m-%d %H:%M:%S")


        period ={
            'begin':datetime.datetime.now()- datetime.timedelta(days=begin_day),
            'end':datetime.datetime.now()-datetime.timedelta(days=end_day),
            }
        
        # period ={
        #     'begin':beg,
        #     'end':end,
        #     }

        sync_sales_from_api(self,period)
        sync_order_detail_from_api(self,period)            
        return True           
    
    
    def sync_2dfire_category(self):
        print 'sync_2dfire_category'
#        get_2dfire_catagory_from_api(self)
        return True  


    def sync_2dfire_product(self):
        print 'sync_2dfire_product'
        period ={
            'begin':datetime.datetime.now()- datetime.timedelta(days=begin_day),
            'end':datetime.datetime.now()-datetime.timedelta(days=end_day),
            }
        
        
        sync_product_from_orderlist(self,period)
         
        return True  

    def sync_2dfire_member(self):
        print 'sync_2dfire_member'
 #       get_2dfire_member_from_api(self)            
        return True  
    
    
    def sync_2dfire(self):
        print 'sync_2dfire_all'
  #      self.sync_2dfire_category()
  #      self.sync_2dfire_product()
  #      self.sync_2dfire_member()
  #      self.sync_2dfire_sales()          
        return True  
    
    
    def interface_2dfire_to_bnc_category(self):
        print 'interface_2dfire_to_bnc_category'
        sync_category_to_bnc(self)        
        return True      
        
    
    def interface_2dfire_to_bnc_product(self):
        print 'interface_2dfire_to_bnc_product'
        sync_product_to_bnc(self)        
        return True      
                      
    def interface_2dfire_to_bnc_sales(self):
        print 'interface_2dfire_to_bnc_sales'
        bnc_insert_sales(self)        
        return True      
 
    def proc_sync_2dfire_all(self):
        self.env['proc.sync.2dfire'].sync_2dfire_sales()
        self.env['proc.sync.2dfire'].sync_2dfire_product()        
        self.env['proc.sync.2dfire'].interface_2dfire_to_bnc_category() 
        self.env['proc.sync.2dfire'].interface_2dfire_to_bnc_product()        
        self.env['proc.sync.2dfire'].interface_2dfire_to_bnc_sales()          
        
        return True


    def proc_sync_2dfire_batch(self,start,end):



        period = {
            'begin':datetime.datetime.strptime(start,'%Y-%m-%d') ,
            'end': datetime.datetime.strptime(end,'%Y-%m-%d')
        }
        sync_sales_from_api(self, period)
        sync_order_detail_from_api(self, period)
        self.env['proc.sync.2dfire'].interface_2dfire_to_bnc_category()
        self.env['proc.sync.2dfire'].interface_2dfire_to_bnc_product()
        return True

    def proc_sync_2dfire_batch_sales(self,start,end):
        period = {
            'begin': datetime.datetime.strptime(start, '%Y-%m-%d'),
            'end': datetime.datetime.strptime(end, '%Y-%m-%d')
        }
        # self.env['proc.sync.2dfire'].interface_2dfire_to_bnc_product()
        bnc_insert_sales_batch(self,period)

        return True

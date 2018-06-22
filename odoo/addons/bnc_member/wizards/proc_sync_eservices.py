# -*- coding: utf-8 -*-
import logging
import threading
import datetime

from odoo import api, models, tools, registry
from odoo.addons.bnc_member.models.bnc_computer_repaire import *

#from odoo.addons.bn_pospal.models import  *


#from idlelib.SearchEngine import get

_logger = logging.getLogger(__name__)


begin_day = 7
end_day = 0
class proc_sync_eservices(models.TransientModel):
    _name = 'proc.sync.eservices'
    _description = 'proc.sync.eservices'
    
    #获取事业部代码
    @api.model    
    def _get_business(self):
        res=self.env['bnc.business'].get_bnc_business_bycode('hos')  
        return res  
    
    
    def sync_eservices_sales(self):
        
        
        print 'sync_eservices_sales'
        period ={
            'begin':datetime.datetime.now()- datetime.timedelta(days=begin_day),
            'end':datetime.datetime.now()-datetime.timedelta(days=end_day),
            }
        sync_sales_to_bnc(self,period)
        
#        sync_sales_from_api(self,period)
#        sync_order_detail_from_api(self,period)            
        return True           
    
    
    def sync_eservices_branch(self):
        print 'sync_eservices_branch'
        proc_branch(self)
        return True  


    def sync_eservices_product(self):
        print 'sync_eservices_product'
        period ={
            'begin':datetime.datetime.now()- datetime.timedelta(days=begin_day),
            'end':datetime.datetime.now()-datetime.timedelta(days=end_day),
            }
        
        
#        sync_product_from_orderlist(self,period)
         
        return True  

    def sync_eservices_member(self):
        print 'sync_eservices_member'
 #       get_eservices_member_from_api(self)            
        return True  
    
    
    def sync_eservices(self):
        print 'sync_eservices_all'
  #      self.sync_eservices_category()
  #      self.sync_eservices_product()
  #      self.sync_eservices_member()
  #      self.sync_eservices_sales()          
        return True  
    
    
    def interface_eservices_to_bnc_category(self):
        print 'interface_eservices_to_bnc_category'
#        sync_category_to_bnc(self)        
        return True      
        
    
    def interface_eservices_to_bnc_product(self):
        print 'interface_eservices_to_bnc_product'
 #       sync_product_to_bnc(self)        
        return True      
                      
    def interface_eservices_to_bnc_sales(self):
        print 'interface_eservices_to_bnc_sales'
  #      bnc_insert_sales(self)        
        return True      
        
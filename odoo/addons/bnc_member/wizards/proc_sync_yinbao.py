# -*- coding: utf-8 -*-
import logging
import threading
import datetime
import time
from odoo import api, models, tools, registry
from BNmssql import  bn_SQLCa
from odoo.addons.bn_pospal.models.bn_yinbao_product import  *
from odoo.addons.bn_pospal.models.bn_yinbao import  *
from odoo.addons.bn_pospal.models.bn_yinbao_member import  *
from odoo.addons.bn_pospal.models.bn_yinbao_order import  *
from odoo.addons.bn_pospal.models.bn_yinbao import  *
from odoo.addons.bnc_member.models.bnc_yinbao import *
#from odoo.addons.bn_pospal.models import  *


#from idlelib.SearchEngine import get

_logger = logging.getLogger(__name__)

class proc_sync_yinbao(models.TransientModel):
    _name = 'proc.sync.yinbao'
    _description = 'proc.sync.yinbao'
    
    #获取事业部代码
    @api.model    
    def _get_business(self):
        res=self.env['bnc.business'].get_bnc_business_bycode('gam')  
        return res  
    
    
    def sync_yinbao_sales(self):
        
        
        print 'sync_yinbao_sales'
        proc_task_list=bnc_split_by_date()
        
        for proc in proc_task_list:
            period ={
                'begin':datetime.datetime.now()- datetime.timedelta(days=proc['max']),
                'end':datetime.datetime.now()-datetime.timedelta(days=proc['min']),            
                }
            _logger.info("bnc=>sync_yinbao_sales %s"  % str(period) )          

            get_yinbao_sales_from_api(self,period)
            time.sleep(5)  # 休眠1秒
        return True           
    
    
    def sync_yinbao_category(self):
        print 'sync_yinbao_category'
        get_yinbao_catagory_from_api(self)
        return True  


    def sync_yinbao_product(self):
        print 'sync_yinbao_product'
        get_yinbao_product_from_api(self)            
        return True  

    def sync_yinbao_member(self):
        print 'sync_yinbao_member'
        get_yinbao_member_from_api(self)            
        return True  
    
    
    def sync_yinbao(self):
        print 'sync_yinbao_all'
        self.env['proc.sync.yinbao'].sync_yinbao_category()
        self.env['proc.sync.yinbao'].sync_yinbao_product()
        self.env['proc.sync.yinbao'].sync_yinbao_member()
        self.env['proc.sync.yinbao'].sync_yinbao_sales()  
        self.env['proc.sync.yinbao'].interface_yinbao_to_bnc_category()  
        self.env['proc.sync.yinbao'].interface_yinbao_to_bnc_product()          
        self.env['proc.sync.yinbao'].interface_yinbao_to_bnc_sales()                  
        return True  
    
    
    def interface_yinbao_to_bnc_category(self):
        print 'interface_yinbao_to_bnc_category'
        sync_category_to_bnc(self)        
        return True      
        
    
    def interface_yinbao_to_bnc_product(self):
        print 'interface_yinbao_to_bnc_product'
        sync_product_to_bnc(self)        
        return True      
                      
    def interface_yinbao_to_bnc_sales(self):
        print 'interface_yinbao_to_bnc_sales'
        sync_sales_to_bnc(self)        
        return True      
        
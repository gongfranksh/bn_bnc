# -*- coding: utf-8 -*-
import logging
import threading
import datetime

from odoo import api, models, tools, registry,fields
from odoo.addons.bnc_member.wizards.BNmssql import  bn_SQLCa


class proc_bnc_lead(models.TransientModel):
    _name ="proc.bnc.lead"
    
    
    def create_lead(self):
        print 'create_lead'
        buid=[]
        buids=self.env['bnc.business'].get_bnc_business_bycode('jsp')
        for b in buids:
            buid.append(b.id)
        sales_startdate=datetime.datetime.now()- datetime.timedelta(days=85)
        sales_enddate=datetime.datetime.now()- datetime.timedelta(days=2)
        
        para_start=   sales_startdate.strftime('%Y-%m-%d')    +' 00:00:00'
        para_end=   sales_enddate.strftime('%Y-%m-%d')    +' 23:59:59'
        records=self.env['pos.order'].search([('buid','in',buid),('partner_id','<>',None),('date_order','>=',para_start),('date_order','<=',para_end)])
        
        memlist=[]
        for rec in records:
            memlist.append(rec['partner_id'].id)
            
        members= list(set(memlist))
        print members
        
        
        lead=self.env['bnc.lead'].search([('id','=',6)])
        
        lead_mem=[]
        
        for mem in members:
            vals={
                'name':lead['name']+str(mem),
                'partner_id':mem,  
                'date_action': lead['start'],
                'date_deadline':lead['end']
#                'type':'Opportunity',                                
                }
            lead_mem.append((0,0,vals))
            
        lead.write({'crmleadid':lead_mem})
            


    def create_lead_buynow(self):
        print 'create_lead_buynow'
        buid=[]
        buids=self.env['bnc.business'].get_bnc_business_bycode('bn')
        for b in buids:
            buid.append(b.id)
        sales_startdate=datetime.datetime.now()- datetime.timedelta(days=85)
        sales_enddate=datetime.datetime.now()- datetime.timedelta(days=2)
        
        para_start=   sales_startdate.strftime('%Y-%m-%d')    +' 00:00:00'
        para_end=   sales_enddate.strftime('%Y-%m-%d')    +' 23:59:59'
#        records=self.env['pos.order'].search(['&',('buid','in',buid),('partner_id','<>',None),('date_order','>=',para_start),('date_order','<=',para_end),('amount_total','=', 1000)])
        records=self.env['pos.order'].search(['&',('buid','in',buid),('partner_id','<>',None),('date_order','>=',para_start),('date_order','<=',para_end)])
        memlist=[]        
        for rec in records:
            
            if  rec['amount_total'] >=6000 :
                print rec['pos_reference']
                print rec['amount_total']
                print rec['date_order']
                memlist.append(rec['partner_id'].id)

#            memlist.append(rec['partner_id'].id)
        members= list(set(memlist))
        lead=self.env['bnc.lead'].search([('id','=',7)])
        
        lead_mem=[]
        
        for mem in members:
            vals={
                'name':lead['name']+str(mem),
                'partner_id':mem,  
                'date_action': lead['start'],
                'date_deadline':lead['end']
#                'type':'Opportunity',                                
                }
            lead_mem.append((0,0,vals))
            
        lead.write({'crmleadid':lead_mem})        
        
    

                    

            
            
            
        
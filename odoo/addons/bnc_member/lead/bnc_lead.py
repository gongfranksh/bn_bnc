# -*- coding: utf-8 -*-
import logging
import threading
import datetime

from odoo import api, models, tools, registry,fields
from odoo.addons.bnc_member.wizards.BNmssql import  bn_SQLCa


class bnc_lead(models.Model):
    _name ="bnc.lead"
    
    buid = fields.Many2one('bnc.business',u'事业部')
    code = fields.Char(string=u'编号')
    name = fields.Char(string=u'名称')
    crmleadid = fields.One2many('crm.lead','bnc_lead_id',u'活动明细') 
    start = fields.Datetime(string=u'开始日期')    
    end  = fields.Datetime(string=u'结束日期')    
    memo= fields.Text(string=u'备注说明') 
    state=  fields.Selection([('new', 'open'), ('doing', 'doing'),('', 'Done')], string=u'状态') 
    color = fields.Integer('Color Index')
    def name_get(self):
        res=[]
        for r in self:
            res.append((r.id,r.code+'---'+r.name))
        return res

    
    
                    
class crm_lead(models.Model):
    _inherit = 'crm.lead'     
    bnc_lead_id = fields.Many2one('bnc.lead', string='Order Ref', ondelete='cascade')            
            
            
        
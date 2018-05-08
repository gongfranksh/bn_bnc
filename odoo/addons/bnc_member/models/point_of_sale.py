
# -*- coding: utf-8 -*-
from odoo import api, fields, models

class pos_order(models.Model):
    _inherit = 'pos.order' 
    buid = fields.Many2one('bnc.business',u'事业部')
    lngcasherid=fields.Many2one('hr.employee', u'收银员')   
    strstoreid=fields.Char(string=u'storeid',size=20)
     
class pos_order_line(models.Model):
    _inherit = 'pos.order.line'
    lngsaleid=fields.Many2one('hr.employee', u'导购')
    

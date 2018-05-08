# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP


class res_partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    
    strbncardid=fields.Char(string=u'会员编号',size=20 )
    strsupid   =fields.Char(string=u'供应商代码',size=20 )
    strbnctype =fields.Char(string=u'ms类型',size=20 )
    
        
    @api.model
    def search_bycardid(self, cardno): 
        res =self.search([('strbncardid', '=',cardno)])
        return res

    @api.model
    def search_bysupid(self, supid): 
        res =self.search([('strsupid', '=',supid)])
        return res
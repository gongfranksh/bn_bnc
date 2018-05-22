# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP

class res_company(models.Model):
    _name = 'res.company'
    _inherit = 'res.company'
    bncode=fields.Char(string='bncode' )
    buid=fields.Many2one('bnc.business',string=u'事业部' )
    mp_bucode=fields.Char(string=u'微信公众号code' )
    mp_buname=fields.Char(string=u'微信公众号名称' )




    @api.model
    def search_bycode(self, code):    
        res =self.search([('bncode', '=',code)])
        return res
    
    @api.model
    def get_bussiness_stores(self, busids):    
        res =self.search([('buid', '=',busids.id)])
        return res
    
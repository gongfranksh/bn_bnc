# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class bn_db_connect(models.Model):
    _name='bn.db.connect'
    db_password=fields.Char(u'密码')
    db_name=fields.Char(u'数据库名称')
    db_user=fields.Char(u'账户')
    db_ip=fields.Char(u'服务器')    
    bu_code=fields.Char(u'事业部代码') 
    store_code=fields.Char(u'分店代码')     
    
               
class product_category(models.Model):
    _inherit = 'product.category'
    store_id = fields.Many2one('res.company',u'分店')
    @api.model
    def search_bycode(self, code): 
        res =self.search([('code', '=',code)])
        return res

class product_brand(models.Model):
    _inherit = 'product.brand'
    store_id = fields.Many2one('res.company',u'分店')
    @api.model
    def search_bycode(self, code): 
        res =self.search([('code', '=',code)])
        return res
    

class pos_category(models.Model):
    _inherit = 'pos.category'
    store_id = fields.Many2one('res.company',u'分店')   
    
    
class product_template(models.Model):
    _inherit = 'product.template'
    b_sup_id = fields.Many2one('buynow.supplier',u'供应商')
    store_id = fields.Many2one('res.company',u'分店')
    @api.model
    def search_bycode(self, code): 
        res =self.search([('code', '=',code)])
        return res
    
    

class buynow_supplier(models.Model):
    _name = 'buynow.supplier'
       
    supid=fields.Char(string=u'供应商编码',size=200 )
    name=fields.Char(string=u'供应商名称')
    address=fields.Char(string=u'供应商联系地址')
    telephone=fields.Char(string=u'联系电话')
    email=fields.Char(string=u'邮件')
    fax=fields.Char(string=u'传真')
    zip=fields.Char(string=u'邮编')
    timestamp= fields.Integer(string=u'更新时间戳')
    resid = fields.Many2one('res.partner',u'合作伙伴',required=True, ondelete='cascade')
    buid = fields.Many2one('bnc.business',u'事业部') 
    store_id = fields.Many2one('res.company',u'分店')   
    
    @api.model
    def search_bycode(self, supid): 
        res =self.search([('supid', '=',supid)])
        return res    

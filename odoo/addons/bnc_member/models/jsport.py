# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class product_brand(models.Model):
    _name = 'product.brand'
    code=fields.Char(string=u'品牌代码' )
    name=fields.Char(string=u'品牌名称')    
    buid = fields.Many2one('bnc.business',u'事业部')
    timestamp= fields.Integer(string=u'更新时间戳') 
        
    @api.model
    def search_bycode(self, code): 
        res =self.search([('code', '=',code)])
        return res

class product_category(models.Model):
    _inherit = 'product.category'
    code=fields.Char(string=u'代码')
    buid = fields.Many2one('bnc.business',u'事业部')
    timestamp= fields.Integer(string=u'更新时间戳')
        
    @api.model
    def search_bycode(self, code): 
        res =self.search([('code', '=',code)])
        return res


class pos_category(models.Model):
    _inherit = 'pos.category'
    code=fields.Char(string=u'代码')
    buid = fields.Many2one('bnc.business',u'事业部')
    timestamp= fields.Integer(string=u'更新时间戳')
        
    @api.model
    def search_bycode(self, code): 
        res =self.search([('code', '=',code)])
        return res
    
        
class product_template(models.Model):
    _inherit = 'product.template'
    buid = fields.Many2one('bnc.business',u'事业部')
    code=fields.Char(string=u'商品代码') 
    bn_barcode=fields.Char(string=u'条形码' ) 
    m_category = fields.Many2one('product.category',u'中类')   
    b_category = fields.Many2one('product.category',u'大类') 
    brand_id = fields.Many2one('product.brand',u'品牌') 
    sup_id = fields.Many2one('jsport.supplier',u'供应商') 

    spec=fields.Char(string=u'规格型号')
    timestamp= fields.Integer(string=u'更新时间戳')      
        
    @api.model
    def search_bycode(self, code): 
        res =self.search([('code', '=',code)])
        return res
    
    
class hr_employee(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee' 
       
    code=fields.Char(string=u'员工编号' )
    timestamp= fields.Integer(string=u'更新时间戳')
    buid = fields.Many2one('bnc.business',u'事业部')    
    
    @api.model
    def search_bycode(self, code): 
        res =self.search([('code', '=',code)])
        return res    
        
class jsport_supplier(models.Model):
    _name = 'jsport.supplier'
       
    supid=fields.Char(string=u'供应商编码' )
    name=fields.Char(string=u'供应商名称')
    address=fields.Char(string=u'供应商联系地址')
    telephone=fields.Char(string=u'联系电话')
    email=fields.Char(string=u'邮件')
    fax=fields.Char(string=u'传真')
    zip=fields.Char(string=u'邮编')
    timestamp= fields.Integer(string=u'更新时间戳')
    resid = fields.Many2one('res.partner',u'合作伙伴',required=True, ondelete='cascade')
    buid = fields.Many2one('bnc.business',u'事业部')    
    
    @api.model
    def search_bycode(self, supid): 
        res =self.search([('supid', '=',supid)])
        return res    

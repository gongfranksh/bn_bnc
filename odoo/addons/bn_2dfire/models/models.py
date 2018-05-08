# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class bn_2dfire(models.Model):
#     _name = 'bn_2dfire.bn_2dfire'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
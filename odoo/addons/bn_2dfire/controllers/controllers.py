# -*- coding: utf-8 -*-
from odoo import http

# class Bn2dfire(http.Controller):
#     @http.route('/bn_2dfire/bn_2dfire/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bn_2dfire/bn_2dfire/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bn_2dfire.listing', {
#             'root': '/bn_2dfire/bn_2dfire',
#             'objects': http.request.env['bn_2dfire.bn_2dfire'].search([]),
#         })

#     @http.route('/bn_2dfire/bn_2dfire/objects/<model("bn_2dfire.bn_2dfire"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bn_2dfire.object', {
#             'object': obj
#         })
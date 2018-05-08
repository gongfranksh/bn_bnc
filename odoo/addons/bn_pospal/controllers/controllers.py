# -*- coding: utf-8 -*-
from odoo import http

# class BnPospal(http.Controller):
#     @http.route('/bn_pospal/bn_pospal/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bn_pospal/bn_pospal/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bn_pospal.listing', {
#             'root': '/bn_pospal/bn_pospal',
#             'objects': http.request.env['bn_pospal.bn_pospal'].search([]),
#         })

#     @http.route('/bn_pospal/bn_pospal/objects/<model("bn_pospal.bn_pospal"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bn_pospal.object', {
#             'object': obj
#         })
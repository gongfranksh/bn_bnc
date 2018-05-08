# -*- coding: utf-8 -*-
from odoo import http

# class BncMember(http.Controller):
#     @http.route('/bnc_member/bnc_member/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bnc_member/bnc_member/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bnc_member.listing', {
#             'root': '/bnc_member/bnc_member',
#             'objects': http.request.env['bnc_member.bnc_member'].search([]),
#         })

#     @http.route('/bnc_member/bnc_member/objects/<model("bnc_member.bnc_member"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bnc_member.object', {
#             'object': obj
#         })
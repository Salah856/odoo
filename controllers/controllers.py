# -*- coding: utf-8 -*-
from odoo import http

# class Hospitalms(http.Controller):
#     @http.route('/hospitalms/hospitalms/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hospitalms/hospitalms/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hospitalms.listing', {
#             'root': '/hospitalms/hospitalms',
#             'objects': http.request.env['hospitalms.hospitalms'].search([]),
#         })

#     @http.route('/hospitalms/hospitalms/objects/<model("hospitalms.hospitalms"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hospitalms.object', {
#             'object': obj
#         })
# -*- coding: utf-8 -*-
# from odoo import http


# class AccountCloseBox(http.Controller):
#     @http.route('/account_close_box/account_close_box/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_close_box/account_close_box/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_close_box.listing', {
#             'root': '/account_close_box/account_close_box',
#             'objects': http.request.env['account_close_box.account_close_box'].search([]),
#         })

#     @http.route('/account_close_box/account_close_box/objects/<model("account_close_box.account_close_box"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_close_box.object', {
#             'object': obj
#         })

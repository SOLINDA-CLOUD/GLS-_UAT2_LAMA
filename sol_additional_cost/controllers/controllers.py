# -*- coding: utf-8 -*-
# from odoo import http


# class SolAdditionalCost(http.Controller):
#     @http.route('/sol_additional_cost/sol_additional_cost', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sol_additional_cost/sol_additional_cost/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sol_additional_cost.listing', {
#             'root': '/sol_additional_cost/sol_additional_cost',
#             'objects': http.request.env['sol_additional_cost.sol_additional_cost'].search([]),
#         })

#     @http.route('/sol_additional_cost/sol_additional_cost/objects/<model("sol_additional_cost.sol_additional_cost"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sol_additional_cost.object', {
#             'object': obj
#         })

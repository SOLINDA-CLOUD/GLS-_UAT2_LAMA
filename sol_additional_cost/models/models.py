from odoo import models, fields, api

class PaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    is_additional_cost = fields.Boolean('Add Aditional Cost')
    additional_cost_account = fields.Many2one('account.account', string='Additional Cost Account')
    additional_cost = fields.Float(string='Additional Cost')
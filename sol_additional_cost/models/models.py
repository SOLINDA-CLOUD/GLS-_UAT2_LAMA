from odoo import models, fields, api

class PaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    is_additional_cost = fields.Boolean('Add Aditional Cost')
    additional_cost_account = fields.Many2one('account.account', string='Additional Cost Account')
    additional_cost = fields.Float(string='Additional Cost')

    def _create_payment_vals_from_wizard(self):
        payment_vals = {
            'date': self.payment_date,
            'amount': self.amount,
            'payment_type': self.payment_type,
            'partner_type': self.partner_type,
            'ref': self.communication,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_bank_id': self.partner_bank_id.id,
            'payment_method_line_id': self.payment_method_line_id.id,
            'destination_account_id': self.line_ids[0].account_id.id,
            'is_bank_charges': self.is_bank_charges,
            'bank_charges_account': self.bank_charges_account.id or False,
            'bank_charges': self.bank_charges or False,
            'is_bank_tax_applicable': self.is_bank_tax_applicable,
            'bank_tax_id': self.bank_tax_id.id or False,
            'bank_tax_amount': self.bank_tax_amount,
            'is_additional_cost': self.is_additional_cost,
            'additional_cost_account': self.additional_cost_account,
            'additional_cost': self.additional_cost,
        }

        if not self.currency_id.is_zero(self.payment_difference) and self.payment_difference_handling == 'reconcile':
            payment_vals['write_off_line_vals'] = {
                'name': self.writeoff_label,
                'amount': self.payment_difference,
                'account_id': self.writeoff_account_id.id,
            }
        return payment_vals

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    is_additional_cost = fields.Boolean('Add Aditional Cost')
    additional_cost_account = fields.Many2one(
        'account.account', string='Additional Cost Account')
    additional_cost = fields.Float(string='Additional Cost')

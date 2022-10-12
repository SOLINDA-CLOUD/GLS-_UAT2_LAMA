from odoo import models, fields, api

# class HrExpense(models.Model):
#     _inherit = 'hr.expense'


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    ref = fields.Char(string='Bill Reference')
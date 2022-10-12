from odoo import models, fields, api

class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    ref = fields.Char(string='Bill Reference')
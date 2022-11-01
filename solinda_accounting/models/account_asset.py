from email.policy import default
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountAsset(models.Model):
    _inherit = 'account.asset'

    pause_dep_check = fields.Boolean("Pause Depreciation", default=False)

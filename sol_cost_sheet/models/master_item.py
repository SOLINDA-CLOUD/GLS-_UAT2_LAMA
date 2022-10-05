from odoo import _, api, fields, models

class MasterItem(models.Model):
    _name = 'master.item'
    _description = 'Master Data Item'
    _rec_name = "product_id"
    _sql_constraints = [
        ("product_id_check", "UNIQUE(product_id)", "Duplicate Component"),
    ]
    
    # component_id = fields.Many2one('component.component',required=True)
    product_id = fields.Many2one('product.product', string='Component',required=True)
    item_line_ids = fields.One2many('master.item.line', 'master_item_id', string='Item Line')
    
class MasterItemLine(models.Model):
    _name = 'master.item.line'
    _description = 'Master Item Line'
    
    master_item_id = fields.Many2one('master.item', string='Master Item',ondelete="cascade")
    product_id = fields.Many2one('product.product',required=True)

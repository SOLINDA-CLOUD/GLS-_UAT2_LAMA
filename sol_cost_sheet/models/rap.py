from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_round

class CsRAP(models.Model):
    _name = 'rap.rap'
    _description = 'RAP'
    _inherit = ['portal.mixin','mail.thread', 'mail.activity.mixin']
    
    name = fields.Char('Name',tracking=True)
    crm_id = fields.Many2one('crm.lead', string='CRM',tracking=True)
    project_id = fields.Many2one('project.project', string='Project')
    date_document = fields.Date('Request Date',tracking=True,default=fields.Date.today)
    user_id = fields.Many2one('res.users', string='Responsible',default=lambda self:self.env.user.id)
    note = fields.Text('Term and condition')
    approval_id = fields.Many2one('approval.approval', string='Approval')
    approver_id = fields.Many2one('approver.line', string='Approver')
    partner_id = fields.Many2one('res.partner', string='Customer')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submited'),
        ('waiting', 'Waiting Approval'),
        ('done', 'Approved'),
        ('close', 'Closed'),
        ('revisied', 'Revisied'),
        ('cancel', 'Rejected'),
    ], string='Status',tracking=True, default="draft")
    category_line_ids = fields.One2many('rap.category', 'rap_id', string='Category Line')
    ga_project_line_ids = fields.One2many('ga.project', 'rap_id', string='GA Project Line')
    waranty_line_ids = fields.One2many('waranty.waranty', 'rap_id', string='Waranty Line')

    total_amount = fields.Float(compute='_compute_total_amount', string='Total Amount',store=True)
    total_amount_rab = fields.Float(compute='_compute_total_amount', string='Total RAB Amount',store=True)

    currency_id = fields.Many2one('res.currency', string='currency',default=lambda self:self.env.company.currency_id.id)
    is_approver = fields.Boolean(compute='_compute_is_approver', string='Is Approver')
    reason = fields.Text('Note')
    project_code = fields.Char('Project Code', related="project_id.code")
    project_manager = fields.Many2one('res.users', string='Project Manager', related='project_id.user_id', required=True)
    revision_on = fields.Boolean(string='Revision',default=False)

    # Non Project
    ga_project = fields.Float('GA Project', compute = "_compute_ga_project", store=True, copy=True)
    project_hse = fields.Float('Project HSE')
    car = fields.Float('Construction All Risk')
    financial_cost = fields.Float('Financial Cost During Constructio')
    bank_guarantee = fields.Float('Bank Guarantee')
    contigency = fields.Float('Contigency')
    waranty = fields.Float('Waranty',compute="_compute_waranty",store=True,copy=True)
    other_price = fields.Float('Other')    


    @api.model
    def create(self, vals):
        res = super(CsRAP, self).create(vals)
        res.name = self.env["ir.sequence"].next_by_code("rap.rap")
        # res.crm_id.rab_id = res.id
        return res 
    
    @api.depends('category_line_ids.price_unit','category_line_ids.rab_price')
    def _compute_total_amount(self):
        for this in self:
            this.total_amount = sum(this.category_line_ids.mapped('price_unit'))
            this.total_amount_rab = sum(this.category_line_ids.mapped('rab_price'))
    
    def action_submit(self):
        self.write({'state':'submit'})
        self.waiting_approval()
    def action_to_draft(self):
        self.write({'state':'draft','approval_id':False,'approver_id':False})
    def action_cancel(self):
        self.write({'state':'cancel'})
    def action_revision(self):
        self.write({'state':'revisied','approval_id':False,'approver_id':False,'revision_on':True})
        

    
    def view_component_rap(self):
        return {
                'name': 'Component RAP',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree',
                'res_model': 'item.item',
                'view_id' : self.env.ref('sol_cost_sheet.rap_component_view_tree').id,
                'search_view_id': self.env.ref('sol_cost_sheet.item_item_view_search').id,
                'domain': [('rap_id','=',self.id)],
                'context': {
                    'search_default_group_by_rap':1,
                    'search_default_group_by_category':2,
                    'search_default_group_by_component':3
                    }
                # 'domain': [('rap_id','=',self.id),('can_be_purchased','=',True)]
        }
    
    @api.model
    def create(self, vals):
        res = super(CsRAP, self).create(vals)
        res.name = self.env["ir.sequence"].next_by_code("rap.rap")
        # res.crm_id.rab_id = res.id
        return res 
    
    # @api.depends('approver_id','approval_id')
    def _compute_is_approver(self):
        for this in self:
            if this.approval_id or this.approver_id:
                if this.approval_id.approval_type == 'user':
                    this.is_approver = this.env.user.id in this.approver_id.user_ids.ids
                else:
                    this.is_approver = this.env.user.id in this.approver_id.group_ids.users.ids
            else:
                this.is_approver = False

    def waiting_approval(self):
        for request in self:
            request.approval_id = request.env['approval.approval'].search([('active', '=', True)],limit=1)
            if bool(request.approver_id):
                approver_id = request.approval_id.approver_line_ids.search([("amount", "<=", request.total_amount),('sequence','>',request.approver_id.sequence)],limit=1)
                if approver_id:
                    request.write({"approver_id": approver_id.id})
                else:
                    request.write({"state": "done","approver_id":False })

            else:
                approver_id = request.approval_id.approver_line_ids.search([("amount", "<=", request.total_amount)],order="sequence ASC",limit=1)
                if approver_id:
                    request.write({
                            "approver_id": approver_id.id,
                            "state": "waiting",
                        })
                else:
                    request.write({
                            "state": "done",
                            "approver_id":False
                        })
                    

    def action_rap_view_list(self):
        
        return {
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": "project.rap",
            "domain": [('rap_id', '=', self.id)],
            "context": {'default_rap_id':self.id},
        }

    @api.onchange('product_id')
    def _onchange_existing(self):
        if self.product_id:
            existing_price = ''
            if self.product_id.last_purchase_price:
                existing_price = self.product_id.last_purchase_price
            self.existing_price = existing_price
    
    @api.onchange('product_id')
    def _onchange_rfq_price(self):
        if self.product_id:
            rfq_price = ''
            if self.product_id.last_purchase_price:
                rfq_price = self.product_id.last_purchase_price
            self.rfq_price = rfq_price

    @api.depends('ga_project_line_ids.total_price')
    def _compute_ga_project(self):
        for this in self:
            this.ga_project = sum(this.ga_project_line_ids.mapped('total_price'))
    
    # @api.depends('ga_project','project_hse_percent')
    # def _compute_project_hse(self):
    #     for this in self:
    #         this.project_hse = this.ga_project * this.project_hse_percent
            
    # @api.depends('subtotal','car_percent')
    # def _compute_car(self):
    #     for this in self:
    #         this.car = this.subtotal * this.car_percent
            
    # @api.depends('project_value','financial_cost')
    # def _compute_fin_cost_percent(self):
    #     for this in self:
    #         this.financial_cost_percent = this.financial_cost / this.project_value if this.financial_cost >0 and this.project_value > 0 else 0.0
    # @api.depends('project_value','bank_guarantee')
    # def _compute_bank_guarantee_percent(self):
    #     for this in self:
    #         this.bank_guarantee_percent = this.bank_guarantee / this.project_value if this.bank_guarantee >0 and this.project_value > 0 else 0.0

    # @api.depends('subtotal','contigency_percent')
    # def _compute_contigency(self):
    #     for this in self:
    #         this.contigency = this.subtotal * this.contigency_percent
            
    
    @api.depends('waranty_line_ids.total_price','project_value')
    def _compute_waranty(self):
        for this in self:
            this.waranty = sum(this.waranty_line_ids.mapped('total_price'))
    


class RapCategory(models.Model):
    _name = 'rap.category'
    _description = 'Rap Category'
    _rec_name = 'product_id'
    _order = 'sequence'
    
    sequence = fields.Integer('Sequence')
    rap_id = fields.Many2one('rap.rap', string='RAP',ondelete="cascade")
    project_id = fields.Many2one('project.project', string='Project', related='rap_id.project_id', store=True)
    cost_sheet_id = fields.Many2one('cost.sheet', string='Cost Sheet',ondelete="cascade")
    product_id = fields.Many2one('product.product',required=True)
    rab_category_id = fields.Many2one('rab.category', string='Rab Category')
    parent_component_line_ids = fields.One2many('component.component', 'rap_category_id', string='Parent Component Line')
    rab_price = fields.Float('RAB Price')
    price_unit = fields.Float('Price',compute="_compute_price_unit")
    rap_state = fields.Selection(related='rap_id.state',store=True)
    rap_price = fields.Float(compute='_compute_rap_price', string='RAP Price')
    
    @api.depends('parent_component_line_ids.item_ids.price_po')
    def _compute_rap_price(self):
        for i in self:
            i.rap_price = sum(i.parent_component_line_ids.mapped('item_ids.total_price'))

    @api.depends('parent_component_line_ids.item_ids.price_po')
    def _compute_price_unit(self):
        for this in self:
            this.price_unit = sum(this.parent_component_line_ids.mapped('item_ids.price_po'))
    
    def action_view_detail_rap(self):
        return {
                'name': 'Component RAP',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'rap.category',
                'target':'new',
                'res_id': self.id,
            }
  
    
    
    @api.constrains('product_id')
    def _constrains_product_id(self):
        for this in self:
            data = this.env['rab.category'].search([('cost_sheet_id', '=', this.cost_sheet_id.id),('product_id', '=', this.product_id.id)])
            if len(data) > 1:
                raise ValidationError('Cannot create same product in one cost sheet')
            
    
    def action_view_detail(self):
        return {
                'name': 'Component RAB',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'rab.category',
                'target':'new',
                'res_id': self.id,
                }
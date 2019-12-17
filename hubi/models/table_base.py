# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HubiDepartement(models.Model):
    _name = 'hubi.department'
    _description = "Départment"
    _order = 'name'
    
    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Name', required=True)
    
    _sql_constraints = [
    ('uniq_id', 'unique(code)', 'A department already exists with this code. It must be unique !'),
    ]
    
class HubiFamily(models.Model):
    _name = 'hubi.family'
    _description = "Partner family"
    _order = 'name'
    
    def _get_level(self):
        level_vals = [("Type", "Type"), ("Job", "Job"),("Family", "Family"),("Caliber", "Caliber"),("Packaging", "Packaging")]
        return level_vals
    
    def _get_level_partner(self):
        level_vals = [("Type", "Type"), ("Job", "Job"),("Family", "Family")]
        return level_vals
    
    def _get_level_product(self):
        level_vals = [("Caliber", "Caliber"),("Packaging", "Packaging")]
        return level_vals
    
    #def _get_default_company_id(self):
    #    return self._context.get('force_company', self.env.user.company_id.id)

    
    #@api.multi
    @api.onchange('level_partner', 'level_product')
    @api.depends('main_level')
    def change_level(self):
        if self.level_partner and self.main_level == 'Partner':
            self.level = self.level_partner
        if self.level_product and self.main_level == 'Product':
            self.level = self.level_product

 
    #@api.multi
    @api.depends('main_level')
    def _return_level(self):
        if not self.main_level:
            return
        if self.main_level == 'Partner':
            self.level = self.level_partner
        elif self.main_level == 'Product':
            self.level = self.level_product   

    def _get_company_domain(self):    
        domain = [] 
        companies = self.env.user.company_ids  
        domain.append(('id', 'in', companies.ids))    
        return domain
    
    #@api.model
    def _get_company(self):
        return self.env.user.company_id
    
    reference = fields.Char(string='Reference')
    name = fields.Char(string='Name', required=True)
    main_level = fields.Selection([("Partner", "Partner"), ("Product", "Product")],
                              string="Main Level", Required=True, track_visibility=True)
    #level = fields.Selection([("Type", "Type"), ("Job", "Job"),("Family", "Family"),
    #                          ("Caliber", "Caliber"),("Packaging", "Packaging")],
    #                          string="Level", Required=True, track_visibility=True, compute='_return_level', store=True)
    level = fields.Selection('_get_level', string="Level", Required=True, track_visibility=True, compute='_return_level', store=True )
    level_partner = fields.Selection('_get_level_partner', string="Level", Required=True, track_visibility=True)
    level_product = fields.Selection('_get_level_product', string="Level", Required=True, track_visibility=True)
                              
                              
    default_value = fields.Boolean(string='Default Value', default=False)
    sale_ok = fields.Boolean(string='For Sale', default=True)
    purchase_ok = fields.Boolean(string='For Purchase', default=True)
    weight = fields.Float('Weight')
    company_id = fields.Many2one('res.company', string='Company', default=_get_company, domain=lambda self: self._get_company_domain(), required=True)

    #@api.multi
    @api.constrains('company_id')
    def _check_company(self):
        if (self.company_id not in self.env.user.company_ids): 
            raise ValidationError(_('The chosen company is not in the allowed companies for this family'))
       
 
 
    #@api.model
    #def fields_view_get(self, view_id=None, view_type='form',
    #                    toolbar=False, submenu=False):
    #    companies = self.env.user.company_id + self.env.user.company_ids
    #    company_domain = [('id', 'in', companies.ids)]
    #    return {'domain': {'company_id': company_domain}}
    




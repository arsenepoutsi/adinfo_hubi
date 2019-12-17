# -*- coding: utf-8 -*-

from odoo import models, fields, api
    
class HubiModule_option(models.Model):
    _name = 'hubi.module_option'
    _description = "Modules - Options"
    _order = 'name'
    
    def _get_company_domain(self):    
        domain = [] 
        companies = self.env.user.company_ids  
        domain.append(('id', 'in', companies.ids))    
        return domain
    
    @api.model
    def _get_company(self):
        return self.env.user.company_id

        
    name = fields.Char(string='Name', required=True)
    state = fields.Boolean(string="State", default=True)
    description = fields.Char(string='Description')
    description_other = fields.Char(string='Other description')
    company_id = fields.Many2one('res.company', string='Company', default=_get_company, domain=lambda self: self._get_company_domain(), required=True)

    _sql_constraints = [
    ('uniq_id', 'unique(name, company_id)', 'A module_option already exists with this code in this company. It must be unique !'),
    ]
    
    @api.multi
    @api.constrains('company_id')
    def _check_company(self):
        if (self.company_id not in self.env.user.company_ids): 
            raise ValidationError(_('The chosen company is not in the allowed companies for this module option'))

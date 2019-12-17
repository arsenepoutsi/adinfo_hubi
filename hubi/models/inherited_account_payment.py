# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
   
class HubiAccountPaymentMode(models.Model):
    _name = "hubi.payment_mode"
    _description = "Payment Mode"  

    #@api.model
    def _get_company(self):
        return self.env.user.company_id
    
    def _get_company_domain(self):    
        domain = [] 
        companies = self.env.user.company_ids  
        domain.append(('id', 'in', companies.ids))    
        return domain
    
    name = fields.Char(string='Name', required=True) 
    company_id = fields.Many2one('res.company', string='Company', default=_get_company, domain=lambda self: self._get_company_domain(), required=True)
 

class HubiAccountPaymentTermLine(models.Model):
    _inherit = "account.payment.term.line"

    def _get_payment_mode_domain(self):    
        domain = [] 
        #domain.append(('company_id', '=', self.payment_id.company_id.id))
        companies = self.env.user.company_ids  
        domain.append(('company_id', 'in', companies.ids))        
        return domain
    
    payment_mode_id = fields.Many2one('hubi.payment_mode', string='Payment Mode', domain=lambda self: self._get_payment_mode_domain())
 
class HubiAccountPayment(models.Model):
    _inherit = "account.payment"

    payment_mode_id = fields.Many2one('hubi.payment_mode', string='Payment Mode')
    
    
    def _compute_journal_domain_and_types(self):
        journal_type = ['bank', 'cash']
        domain = []
        if self.currency_id.is_zero(self.amount):
            # In case of payment with 0 amount, allow to select a journal of type 'general' like
            # 'Miscellaneous Operations' and set this journal by default.
            journal_type = ['bank', 'cash', 'general']
            self.payment_difference_handling = 'reconcile'
        else:
            if self.payment_type == 'inbound':
                domain.append(('at_least_one_inbound', '=', True))
            elif self.payment_type == 'outbound':
                domain.append(('at_least_one_outbound', '=', True))
        return {'domain': domain, 'journal_types': set(journal_type)}

    
class HubiRegisterPayments(models.TransientModel):
    _inherit = "account.register.payments"

    payment_mode_id = fields.Many2one('hubi.payment_mode', string='Payment Mode')

    def _prepare_payment_vals(self, invoices):
        res = super(HubiRegisterPayments, self)._prepare_payment_vals(invoices)
        
        res.update({
                'payment_mode_id': self.payment_mode_id.id,
        })
        return res
    
 
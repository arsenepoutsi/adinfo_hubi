# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class HubiGeneralSettings(models.Model):
    _name = 'hubi.general_settings'
    _description = "General Settings"
    _order = 'name'
 
    def _get_default_company_id(self):
        return self._context.get('force_company', self.env.user.company_id.id)

    
    name= fields.Char(string='name', default='General Settings')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('hubi.general_settings'))
    auxiliary_accounting = fields.Boolean(string='Auxiliary Accounting', default=False)
    root_account_auxiliary_customer = fields.Char(string='Root Account Auxiliary Customer', default='C')
    root_account_auxiliary_supplier = fields.Char(string='Root Account Auxiliary Supplier', default='F')
    path_account_transfer = fields.Char(string='Path For Account Transfer')
    length_account_auxiliary = fields.Integer(string='Length for Account Auxiliary')
    length_account_general = fields.Integer(string='Length for Account General')
    complete_0_account_auxiliary = fields.Boolean(string='Complete right with 0 Account Auxiliary')
    complete_0_account_general = fields.Boolean(string='Complete right with 0 Account General')
    account_file_transfer = fields.Char(string='File For Account Transfer')
    writing_file_transfer = fields.Char(string='File For Writing Transfer')
    type_accounting = fields.Selection([('EBP', 'EBP')], string="Type of accounting", default='EBP')
    calcul_lot = fields.Selection([('M', 'Manual'), ('AMJ', 'Auto AAAAMMJJ'), ('AQ', 'Auto AAAAQQQ')], string="Batch Number Calculation", default='M')
    mail_accounting = fields.Boolean(string="Send Email", default=True)

    _sql_constraints = [
        ('unique_name_company', 'unique(name, company_id)', 'Name must be unique for the company'),
    ]
  

class Wizard_GeneralSettings(models.TransientModel):
    _name = 'wiz.general_settings'
    _description = "General Settings"
    _order = 'name'
    
    name= fields.Char(string='name', default=lambda self: self._get_values('name'))
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self._get_values('company_id'))
    auxiliary_accounting = fields.Boolean(string='Auxiliary Accounting', default=lambda self: self._get_values('auxiliary_accounting'))
    root_account_auxiliary_customer = fields.Char(string='Root Account Auxiliary Customer', default=lambda self: self._get_values('root_account_auxiliary_customer'))
    root_account_auxiliary_supplier = fields.Char(string='Root Account Auxiliary Supplier', default=lambda self: self._get_values('root_account_auxiliary_supplier'))
    path_account_transfer = fields.Char(string='Path For Account Transfer', default=lambda self: self._get_values('path_account_transfer'))
    length_account_auxiliary = fields.Integer(string='Length for Account Auxiliary', default=lambda self: self._get_values('length_account_auxiliary'))
    length_account_general = fields.Integer(string='Length for Account General', default=lambda self: self._get_values('length_account_general'))
    complete_0_account_auxiliary = fields.Boolean(string='Complete right with 0 Account Auxiliary', default=lambda self: self._get_values('complete_0_account_auxiliary'))
    complete_0_account_general = fields.Boolean(string='Complete right with 0 Account General', default=lambda self: self._get_values('complete_0_account_general'))
    account_file_transfer = fields.Char(string='File For Account Transfer', default=lambda self: self._get_values('account_file_transfer'))
    writing_file_transfer = fields.Char(string='File For Writing Transfer', default=lambda self: self._get_values('writing_file_transfer'))
    type_accounting = fields.Selection([('EBP', 'EBP')], string="Type of accounting", default=lambda self: self._get_values('type_accounting'))
    calcul_lot = fields.Selection([('M', 'Manual'), ('AMJ', 'Auto AAAAMMJJ'), ('AQ', 'Auto AAAAQQQ')], string="Batch Number Calculation", default=lambda self: self._get_values('calcul_lot'))
    mail_accounting = fields.Boolean(string="Send Email", default=lambda self: self._get_values('mail_accounting'))

    @api.model
    def _get_values(self, valeur):
        """
        Return values for the fields 
        """
        
        val_auxiliary_accounting = False
        val_root_account_auxiliary_customer = 'C'
        val_root_account_auxiliary_supplier = 'F'
        val_length_account_auxiliary = 0
        val_length_account_general = 0
        val_complete_0_account_auxiliary = False
        val_complete_0_account_general = False
        
        val_path_account_transfer = ''
        val_account_file_transfer = ''
        val_writing_file_transfer = ''
        val_type_accounting = 'EBP'
        val_calcul_lot = 'M'
        val_mail_accounting = False
        
        company_id = self.env['res.company']._company_default_get('hubi.general_settings')
        val_company_id =company_id.id 
        val_name = 'General Settings'
        
        settings = self.env['hubi.general_settings'].search([('name','=', val_name), ('company_id','=', val_company_id)])
        for settings_vals in settings:
            val_name = settings_vals.name
            val_company_id =settings_vals.company_id
            
            val_auxiliary_accounting = settings_vals.auxiliary_accounting or False
            val_root_account_auxiliary_customer = settings_vals.root_account_auxiliary_customer
            val_root_account_auxiliary_supplier = settings_vals.root_account_auxiliary_supplier
             
            val_length_account_auxiliary = settings_vals.length_account_auxiliary or 0
            val_length_account_general = settings_vals.length_account_general or 0
            val_complete_0_account_auxiliary = settings_vals.complete_0_account_auxiliary or False
            val_complete_0_account_general = settings_vals.complete_0_account_general or False
            
            val_path_account_transfer = settings_vals.path_account_transfer
            val_account_file_transfer = settings_vals.account_file_transfer
            val_writing_file_transfer = settings_vals.writing_file_transfer
            val_type_accounting = settings_vals.type_accounting
            val_calcul_lot = settings_vals.calcul_lot
            val_mail_accounting = settings_vals.mail_accounting or False
            
        if valeur == 'name':
            retour = val_name   
        
        if valeur == 'company_id':
            retour = val_company_id 
                    
        if valeur == 'auxiliary_accounting':
            retour = val_auxiliary_accounting 
            
        if valeur == 'root_account_auxiliary_customer':
            retour = val_root_account_auxiliary_customer 
            
        if valeur == 'root_account_auxiliary_supplier':
            retour = val_root_account_auxiliary_supplier   
              
        if valeur == 'length_account_auxiliary':
            retour = val_length_account_auxiliary 
                        
        if valeur == 'length_account_general':
            retour = val_length_account_general
            
        if valeur == 'complete_0_account_auxiliary':
            retour = val_complete_0_account_auxiliary  
            
        if valeur == 'complete_0_account_general':
            retour = val_complete_0_account_general     

        if valeur == 'path_account_transfer':
            retour = val_path_account_transfer   
                    
        if valeur == 'account_file_transfer':
            retour = val_account_file_transfer  
                    
        if valeur == 'writing_file_transfer':
            retour = val_writing_file_transfer  
        
        if valeur == 'type_accounting':
            retour = val_type_accounting
            
        if valeur == 'calcul_lot':
            retour = val_calcul_lot
                     
        if valeur == 'mail_accounting':
            retour = val_mail_accounting
                                    
        return retour

    @api.multi
    def execute_update(self):
        #self.ensure_one()
        
        _vals = {'name': self.name,
                'company_id' : self.company_id,
                'auxiliary_accounting': self.auxiliary_accounting,
                'root_account_auxiliary_customer': self.root_account_auxiliary_customer,
                'root_account_auxiliary_supplier': self.root_account_auxiliary_supplier,
                'length_account_auxiliary' : self.length_account_auxiliary,
                'length_account_general' : self.length_account_general,
                'complete_0_account_auxiliary' : self.complete_0_account_auxiliary,
                'complete_0_account_general' : self.complete_0_account_general,
                'path_account_transfer' : self.path_account_transfer,
                'account_file_transfer' : self.account_file_transfer,
                'writing_file_transfer' : self.writing_file_transfer,
                'type_accounting' : self.type_accounting,
                'calcul_lot' : self.calcul_lot,
                'mail_accounting' : self.mail_accounting
                }
        #prepare_setting = self.env['hubi.general_settings'].write(_vals)
        #self.env.cr.commit()
        
        settings = self.env['hubi.general_settings'].search([('name','=', self.name), ('company_id','=', self.company_id.id)])
        if settings:
            query = """UPDATE hubi_general_settings SET 
                    
                    auxiliary_accounting = %s , 
                    root_account_auxiliary_customer = %s , 
                    root_account_auxiliary_supplier = %s ,
                    length_account_auxiliary = %s,
                    length_account_general = %s,
                    complete_0_account_auxiliary = %s,
                    complete_0_account_general = %s,
                    path_account_transfer = %s,
                    account_file_transfer = %s,
                    writing_file_transfer = %s,
                    type_accounting = %s,
                    calcul_lot = %s,
                    mail_accounting = %s  
                    WHERE name = %s AND company_id = %s
                           """
            
        else:
            company =self.env['res.company']._company_default_get('hubi.general_settings')    
            query = """INSERT INTO hubi_general_settings 
                    ( auxiliary_accounting, root_account_auxiliary_customer, root_account_auxiliary_supplier, length_account_auxiliary, length_account_general, complete_0_account_auxiliary, complete_0_account_general, path_account_transfer, account_file_transfer, writing_file_transfer, type_accounting, calcul_lot, name, company_id) 
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        
        #try:                   
        self.env.cr.execute(query,  (self.auxiliary_accounting, self.root_account_auxiliary_customer, self.root_account_auxiliary_supplier, self.length_account_auxiliary, self.length_account_general, self.complete_0_account_auxiliary, self.complete_0_account_general, self.path_account_transfer, self.account_file_transfer, self.writing_file_transfer,self.type_accounting, self.calcul_lot, self.mail_accounting, self.name, self.company_id.id))
        self.env.cr.commit()
        #except Exception as e:
        #    _logger.warning(
        #            _("Can't update-insert general settings (%s). Failed: <%s>") %
        #            (query, str(e)))    
                    
        
        #return {'type': 'ir.actions.act_window_close'} 
        
    @api.multi
    def cancel_old(self):
        # ignore the current record, and send the action to reopen the view
        actions = self.env['ir.actions.act_window'].search([('res_model', '=', self._name)], limit=1)
        if actions:
            return actions.read()[0]
        return {}
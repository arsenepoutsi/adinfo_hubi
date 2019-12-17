# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from . import tools_hubi

class HubiInheritedResPartner(models.Model):
    _inherit = "res.partner"
   
    def _is_Visible(self):
        return tools_hubi._is_Visible_class(self, 'Partner')

    def _default_is_Visible(self, valeur):
        return tools_hubi._default_is_Visible_class(self, valeur) 
    
    def _default_family(self, valeur): 
        retour = 0
        option=self.env['hubi.family']

        check_opt=option.search([('level','=', valeur)])
        for check in check_opt:
            if check.default_value:
                retour = check.id
        return retour
       
    def _get_default_company_id(self):
        return self._context.get('force_company', self.env.user.company_id.id)
       
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', default=lambda self: self.env['res.country'].search([('code','=','FR')]))
    family_type_id = fields.Many2one('hubi.family', string='Type', domain=[('level', '=', 'Type')], help="The type of the partner.", default=lambda self: self._default_family('Type'))
    family_job_id = fields.Many2one('hubi.family', string='Job', domain=[('level', '=', 'Job')], help="The job of the partner.", default=lambda self: self._default_family('Job'))
    family_id = fields.Many2one('hubi.family', string='Family', domain=[('level', '=', 'Family')], help="The family of the partner.", default=lambda self: self._default_family('Family'))
    cee_code = fields.Char(string='CEE Code')
    remote_operation = fields.Boolean(string='Remote operation', default=False)
    sender_establishment = fields.Many2one('res.partner', string='Sender establishment', default=_get_default_company_id)
    excluded_packaging = fields.Boolean(string='Excluded packaging', default=False)
    shipping = fields.Boolean(string='Shipping', default=False)
    billing_fees = fields.Boolean(string='Billing fees', default=False)
    frs_code = fields.Char(string='FRS Code')
    ifls_code = fields.Char(string='IFLS Code')
    ifls_edit_invoice = fields.Boolean(string='IFLS Edit Invoice', default=False)
    ifls_edit_delivery = fields.Boolean(string='IFLS Edit Delivery', default=False)
    ifls_edit_etiq = fields.Boolean(string='IFLS Edit Etiq', default=False)

    discount_invoice = fields.Float(string='Discount Invoice')
    discount_ca = fields.Float(string='Discount CA')
    discount_period_ca = fields.Selection([("Monthly", "Monthly"), ("Quarterly", "Quarterly"),
                              ("Annual", "Annual")], string="Period Discount CA")
    discount_description = fields.Char(string='CA Discount Description')
    deb = fields.Boolean(string='DEB', default=False)
    product_grouping = fields.Boolean(string='Product grouping', default=False)
    invoice_grouping = fields.Boolean(string='Invoice grouping', default=False)
    number_invoice = fields.Integer(string = 'Number Invoice', default=1)
    number_delivery = fields.Integer(string = 'Number Delivery', default=1)
    bottom_message_invoice = fields.Text(string='Bottom message invoice')
    bottom_message_delivery = fields.Text(string='Bottom message delivery')
    edit_price_kg = fields.Boolean(string='Edit price kg', default=False)
    valued_delivery = fields.Boolean(string='Valued delivery', default=False)
    amount_com_kg = fields.Float(string='Amount commission kg')  
    periodicity_invoice = fields.Selection([("Daily", "Daily"),("Weekly", "Weekly"),("Decade", "Decade"),
                              ("Fortnight", "Fortnight"),("Monthly", "Monthly")], string="Invoice Period")
    edit_weight = fields.Boolean(string='Edit weight', default=False)
    auxiliary_account_customer = fields.Char(string='Auxiliary Account Customer')
    auxiliary_account_supplier = fields.Char(string='Auxiliary Account Supplier')
    carrier_id = fields.Many2one('delivery.carrier',string = 'Carrier')
    price_list_id = fields.Integer(string = 'Price List')
    edi_invoice = fields.Boolean(string='EDI Invoice', default=False)
    edi_invoice_prod = fields.Boolean(string='EDI Invoice Production', default=False)
    edi_transport_recipient = fields.Char(string='EDI Transport Recipient')
    order_code_ean = fields.Char(string='Order Code_EAN')
    order_name = fields.Char(string='Order Name')
    code_ean = fields.Char(string='EAN Code')
    customer_color_etiq = fields.Selection([("#FF00FF", "magenta"),("#0000FF", "blue"),
                                    ("#FFFF00", "yellow"),("#FF0000", "red"),
                                    ("#008000", "green"),("#D2691E", "brown"),
                                    ("#FFFFFF", "white"),("#CCCCCC", "grey"),
                                    ("#FFC0CB", "pink")], string='Customer Color Etiq') 
    customer_name_etiq = fields.Char(string='Customer Name Etiq')
    customer_city_etiq = fields.Char(string='Customer City Etiq')
    automatic_batch = fields.Boolean(string='Automatic Batch', default=False)
    ean128 = fields.Boolean(string='EAN128', default=False)
    code_ean128 = fields.Char(string='Start of barcode 128')
    compteur_ean128 = fields.Integer(string='Barcode 128 counter', default=0)

    dlc = fields.Boolean(string='DLC', default=False)
    dlc_number_day = fields.Integer(string = 'DLC Number Day')
    type_etiq = fields.Selection([("1", "Etiquette Type 1"),("2", "Etiquette Type 2"),
                              ("3", "Etiquette Type 3")], string="Type Etiq")
    asset = fields.Char(string='Asset')
    siret = fields.Char(string='Siret')
    rcs = fields.Char(string='RCS')
    naf = fields.Char(string='NAF')
    health_number = fields.Char(string='Health Number')
    red_label_number = fields.Char(string='Red Label Number')
    cnuf = fields.Char(string='CNUF')
    company_name_etiq = fields.Char(string='Customer Name Etiq')
    company_city_etiq = fields.Char(string='Customer City Etiq')
    label_model_id =  fields.Many2one('hubi.labelmodel', string='Label model')
    etiq_printer = fields.Many2one('hubi.printer', string='Label Printer', domain=[('isimpetiq', '=', True)])
    etiq_mention = fields.Char(string='Etiq Mention')
    
    statistics_alpha_1 = fields.Char(string='statistics alpha 1')
    statistics_alpha_2 = fields.Char(string='statistics alpha 2')
    statistics_alpha_3 = fields.Char(string='statistics alpha 3')
    statistics_alpha_4 = fields.Char(string='statistics alpha 4')
    statistics_alpha_5 = fields.Char(string='statistics alpha 5')
    statistics_num_1 = fields.Float(string='statistics numerical 1')
    statistics_num_2 = fields.Float(string='statistics numerical 2')
    statistics_num_3 = fields.Float(string='statistics numerical 3')
    statistics_num_4 = fields.Float(string='statistics numerical 4')
    statistics_num_5 = fields.Float(string='statistics numerical 5')
    
    over_credit = fields.Boolean('Allow Over Credit?', default=True)
    
    is_frs=fields.Boolean(string='is_FRS', compute='_is_Visible', default=lambda self: self._default_is_Visible('REF_FRS'))
    is_ifls=fields.Boolean(string='is_IFLS', compute='_is_Visible', default=lambda self: self._default_is_Visible('GESTION_IFLS'))
    is_edi_facture=fields.Boolean(string='is_EDI_FACTURE', compute='_is_Visible', default=lambda self: self._default_is_Visible('EDI_FACTURE'))
    is_edi_transporteur=fields.Boolean(string='is_EDI_TRANSPORTEUR', compute='_is_Visible', default=lambda self: self._default_is_Visible('EDI_TRANSPORTEUR'))
    is_bl_valorise=fields.Boolean(string='is_BL_VALORISE', compute='_is_Visible', default=lambda self: self._default_is_Visible('BL_VALORISE'))
    is_etiq_lot_auto=fields.Boolean(string='is_ETIQ_LOT_AUTO', compute='_is_Visible', default=lambda self: self._default_is_Visible('ETIQ_LOT_AUTO'))
    is_prix_kg=fields.Boolean(string='is_PRIX_KG', compute='_is_Visible', default=lambda self: self._default_is_Visible('PRIX_KG'))
    is_type_tiers=fields.Boolean(string='is_TYPE_TIERS', compute='_is_Visible', default=lambda self: self._default_is_Visible('TYPE_TIERS'))
    is_etiq_dlc=fields.Boolean(string='is_ETIQ_DLC', compute='_is_Visible', default=lambda self: self._default_is_Visible('ETIQ_DLC'))
    is_etiq_couleur_client=fields.Boolean(string='is_ETIQ_COULEUR_CLIENT', compute='_is_Visible', default=lambda self: self._default_is_Visible('ETIQ_COULEUR_CLIENT'))
    is_etiq_ean_128=fields.Boolean(string='is_ETIQ_EAN_128', compute='_is_Visible', default=lambda self: self._default_is_Visible('ETIQ_EAN_128'))
    is_etiq_mode=fields.Boolean(string='is_ETIQ_MODE', compute='_is_Visible', default=lambda self: self._default_is_Visible('ETIQ_MODE'))
    is_etiq_type=fields.Boolean(string='is_ETIQ_TYPE', compute='_is_Visible', default=lambda self: self._default_is_Visible('ETIQ_TYPE'))
    is_export_compta=fields.Boolean(string='is_EXPORT_COMPTA', compute='_is_Visible', default=lambda self: self._default_is_Visible('EXPORT_COMPTA'))
    is_fonction_deporte=fields.Boolean(string='is_FONCTION_DEPORTE', compute='_is_Visible', default=lambda self: self._default_is_Visible('FONCTION_DEPORTE'))
    is_regr_prod_fac=fields.Boolean(string='is_REGR_PROD_FAC', compute='_is_Visible', default=lambda self: self._default_is_Visible('REGR_PROD_FAC'))
    
    @api.onchange('name')
    def _onchange_auxiliary(self):
       
        val_company_id = self.company_id.id 
        val_name = 'General Settings'
        name_partner = ""
        if self.name:
            name_partner = self.name.replace('\\','') \
                     .replace('"','') \
                     .replace('\n', '') \
                     .replace(' ', '') \
                     .replace('-', '') \
                     .replace('_', '') \
                     .replace("'", '') \
                     .replace('.', '') \
                     .replace('ê', 'e') \
                     .replace('è', 'e') \
                     .replace('é', 'e') \
                     .replace('à', 'a') \
                     .replace('ô', 'o') \
                     .replace('ö', 'o') \
                     .replace('î', 'i') 
                     
                        
        settings = self.env['hubi.general_settings'].search([('name','=', val_name), ('company_id','=', val_company_id)])
        if settings:
            root_customer = settings.root_account_auxiliary_customer
            root_supplier = settings.root_account_auxiliary_supplier
            length_auxiliary = settings.length_account_auxiliary or 0
            complete_0_auxiliary = settings.complete_0_account_auxiliary or False
            
            if (root_customer and not self.auxiliary_account_customer ):
                account_customer = root_customer + name_partner
                if length_auxiliary != 0:
                    if (complete_0_auxiliary):
                        account_customer = account_customer.ljust(length_auxiliary,'0')
                    else:    
                        account_customer = account_customer[0:length_auxiliary]
                        
                self.auxiliary_account_customer = account_customer

            if (root_customer and not self.auxiliary_account_supplier ):
                account_supplier = root_supplier + name_partner
                if length_auxiliary != 0:
                    if (complete_0_auxiliary):
                        account_supplier = account_supplier.ljust(length_auxiliary,'0')
                    else:    
                        account_supplier = account_supplier[0:length_auxiliary]
            
                self.auxiliary_account_supplier = account_supplier

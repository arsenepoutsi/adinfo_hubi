# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, RedirectWarning, except_orm, Warning

from . import tools_hubi
import logging

_logger = logging.getLogger(__name__)
   
class HubiInheritedProductTemplate(models.Model):
    _inherit = "product.template"
    
    def _is_Visible(self):
        return tools_hubi._is_Visible_class(self, 'Product')

    def _default_is_Visible(self, valeur):
        return tools_hubi._default_is_Visible_class(self,valeur) 
        #self.env["hubilecturemodule_classe"]._default_is_Visible_class(valeur)
        #super(HubiLectureModule, self)._default_is_Visible_class(valeur)
        
    def _default_family(self, valeur): 
        retour = 0
        option=self.env['hubi.family']

        check_opt=option.search([('level','=', valeur),('company_id', '=',self.company_id.id)])
        for check in check_opt:
            if check.default_value and retour == 0:
                retour = check.id
        return retour

    def _get_default_company_id(self):
        return self._context.get('force_company', self.env.user.company_id.id)

    family_id = fields.Many2one('hubi.family', string='Caliber', domain=[('level', '=', 'Caliber')], help="The Caliber of the product.", default=lambda self: self._default_family('Caliber'))
    caliber_id = fields.Many2one('hubi.family', string='Caliber', domain=[('level', '=', 'Caliber')], help="The Caliber of the product.", default=lambda self: self._default_family('Caliber'))
    packaging_id = fields.Many2one('hubi.family', string='Packaging', domain=[('level', '=', 'Packaging')], help="The Packaging of the product.", default=lambda self: self._default_family('Packaging'))
    remote_operation = fields.Boolean(string='Remote operation', default=False)
    #sender_establishment =  fields.Many2one('res.company', string='Sender establishment',default=lambda self: self.env['res.company']._company_default_get('product.template'))
    #sender_establishment =  fields.Many2one('res.partner', string='Sender establishment', default=_get_default_company_id)
    sender_establishment =  fields.Many2one('res.partner', string='Reserved Establishment')
    sender_establishment_priority = fields.Boolean(string='Reserved establishment priority', default=False)
    product_color = fields.Selection([("#FF00FF", "magenta"),("#0000FF", "blue"),
                                    ("#FFFF00", "yellow"),("#FF0000", "red"),
                                    ("#008000", "green"),("#D2691E", "brown"),
                                    ("#FFFFFF", "white"),("#CCCCCC", "grey"),
                                    ("#FFC0CB", "pink")], string='Product Color')    
    deb_nomenclature = fields.Char(string='DEB Nomenclature')  
    #pallet_description = fields.Char(string='Pallet Description') 
    etiquette = fields.Boolean(string='Etiquette', default=False)
    #etiq_printer = fields.Many2one('hubi.printer', string='Etiq Printer',  default=lambda self: self.env['hubi.printer'].search([('default','=',True)]))
    etiq_printer = fields.Many2one('hubi.printer', string='Label Printer', domain=[('isimpetiq', '=', True)])

    etiq_mention = fields.Char(string='Etiq Mention')
    etiq_description = fields.Char(string='Etiq Description')
    etiq_latin = fields.Char(string='Etiq Latin')
    etiq_spanish = fields.Char(string='Etiq Spanish')
    etiq_country1 = fields.Char(string='Etiq country 1')
    etiq_country2 = fields.Char(string='Etiq country 2')
    etiq_format = fields.Selection([("1", "large"),("2", "small"),("3", "weight"),("4", "other")], string="Etiq Format")
    etiq_modele = fields.Selection([("1", "classic"),("2", "FD Taste of the quality"),
                                    ("3", "Taste of the quality"),("4", "carton")], string="Etiq Modele")
    etiq_model_supple = fields.Boolean(string='Etiq Model Supplementary', default=False)
    etiq_marenne_oleron = fields.Boolean(string='Etiq Marenne Oleron', default=False)
    label_model_id =  fields.Many2one('hubi.labelmodel', string='Label model')
    quantity = fields.Float(string='Quantity')
    product_customer_ids = fields.One2many('hubi.product_customer_description', 'product_id', string='Product Customer Description')

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
       
    is_fonction_deporte=fields.Boolean(string='is_FONCTION_DEPORTE', compute='_is_Visible', default=lambda self: self._default_is_Visible('FONCTION_DEPORTE'))
    is_etiquette=fields.Boolean(string='is_ETIQUETTE', compute='_is_Visible', default=lambda self: self._default_is_Visible('ETIQUETTE'))
    is_etiq_format=fields.Boolean(string='is_ETIQ_FORMAT', compute='_is_Visible', default=lambda self: self._default_is_Visible('ETIQ_FORMAT'))
    is_etiq_marenne=fields.Boolean(string='is_ETIQ_MARENNE', compute='_is_Visible', default=lambda self: self._default_is_Visible('ETIQ_MARENNE'))
    is_etiq_mode=fields.Boolean(string='is_ETIQ_MODE', compute='_is_Visible', default=lambda self: self._default_is_Visible('ETIQ_MODE'))
    is_etiq_prod_edition=fields.Boolean(string='is_ETIQ_PROD_EDITION', compute='_is_Visible', default=lambda self: self._default_is_Visible('ETIQ_PROD_EDITION'))
    is_etiq_prod_libelle=fields.Boolean(string='is_ETIQ_PROD_LIBELLE', compute='_is_Visible', default=lambda self: self._default_is_Visible('ETIQ_PROD_LIBELLE'))
    is_etiq_prod_lib_espagnol=fields.Boolean(string='is_ETIQ_PROD_LIB_ESPAGNOL', compute='_is_Visible', default=lambda self: self._default_is_Visible('ETIQ_PROD_LIB_ESPAGNOL'))
    is_etiq_prod_lib_latin=fields.Boolean(string='is_ETIQ_PROD_LIB_LATIN', compute='_is_Visible', default=lambda self: self._default_is_Visible('ETIQ_PROD_LIB_LATIN'))

    @api.multi
    def name_get(self):
 
        res = super(HubiInheritedProductTemplate, self).name_get()
        data = []
        for product in self:
            display_value = ''
            display_value += product.categ_id.display_name or ""
            display_value += ' / '
            display_value += product.caliber_id.name or ""
            display_value += ' / '
            display_value += product.packaging_id.name or ""
            display_value += ' / '
            display_value += product.name or ""
            display_value += '   ['
            display_value += product.default_code or ""
            display_value += ']'
            data.append((product.id, display_value))
        return data
    
    @api.onchange('packaging_id', 'caliber_id', 'categ_id')
    def _onchange_reference(self):

        refer = ""
        ref_pac = ""
        ref_cal = ""
        ref_cat = ""
        try:
            if self.packaging_id.reference: 
                ref_pac = self.packaging_id.reference
            if self.caliber_id.reference:    
                ref_cal = self.caliber_id.reference
            if self.categ_id.reference:    
                ref_cat = self.categ_id.reference
            refer = ("%s%s%s") % (ref_cat, ref_cal, ref_pac)
            
        except Exception as e: 
            
            refer = ""
       
        self.default_code = refer
        
        if self.packaging_id.weight and self.weight==0: 
            self.weight = self.packaging_id.weight
            
    @api.onchange('barcode')
    def _onchange_barcode(self):
        # Test si code EAN13 correct
        #result = {}
        if self.barcode:
            if (len(self.barcode) < 12 or len(self.barcode) > 14):
                raise ValidationError("ERROR : Barcode EAN13. The length is invalid")
            else:
                cle_ean13 = tools_hubi.calcul_cle_code_ean13(self, self.barcode)
                old_barcode = self.barcode
                self.barcode = tools_hubi.mid(self.barcode,0,12) + cle_ean13
                if (len(old_barcode) == 13) and (not cle_ean13 == old_barcode[12]):
                        raise Warning(_('Barcode EAN13 invalid. The key is ' + cle_ean13))
                        
                        #raise ValidationError("Barcode EAN13 invalid. The key is " + cle_ean13)
                        
                        #result['warning'] = {
                        #    'title': _('Warning'),
                        #    'message': _(('Barcode EAN13 invalid. The key is %s'), cle_ean13)}
                        
                        #return {
                        #    'warning': {
                        #    'title': _('Warning!'),
                        #    'message': _('Barcode EAN13 invalid. The key is %s') % cle_ean13,                }
                        #}
                        

        
    @api.multi
    def update_product_etiq(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        
        self.env.cr.commit()
        
        prod_compos = self.env['product.template'].browse(self._context.get('active_ids', []))
        for compo in prod_compos:
            # Search products from this category and caliber
            products=self.env['product.template'].search([
                ('categ_id', '=', compo.categ_id.id),
                ('caliber_id', '=', compo.caliber_id.id),
                ('packaging_id', '!=', False),    ])   
            for prod in products:
                if compo.etiq_printer and not prod.etiq_printer:   
                    prod.write({'etiq_printer':compo.etiq_printer})
                if compo.etiq_mention and not prod.etiq_mention:   
                    prod.write({'etiq_mention':compo.etiq_mention})    
                if compo.etiq_description and not prod.etiq_description:   
                    prod.write({'etiq_description':compo.etiq_description})  
                if compo.etiq_latin and not prod.etiq_latin:   
                    prod.write({'etiq_latin':compo.etiq_latin})  
                if compo.etiq_spanish and not prod.etiq_spanish:   
                    prod.write({'etiq_spanish':compo.etiq_spanish})     
                if compo.product_color and not prod.product_color:   
                    prod.write({'product_color':compo.product_color})     
                if compo.label_model_id and not prod.label_model_id:   
                    prod.write({'label_model_id':compo.label_model_id})     

        
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    @api.constrains('company_id')
    def _check_company(self):
        if (self.company_id not in self.env.user.company_ids): 
            raise ValidationError(_('The chosen company is not in the allowed companies for this product'))

         
class HubiProductCustomer(models.Model):
    _name = "hubi.product_customer_description"
    
    description = fields.Char(string="Description", required=True)
    product_id = fields.Many2one('product.template', string='Parent Product', index=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Partner', ondelete='cascade', index=True, domain=[('customer', '=', True)])

class HubiInheritedProductCategory(models.Model):
    _inherit = "product.category"
    
    reference = fields.Char(string='Reference')
    shell = fields.Boolean(string='Shell', default=True)
    category_caliber_ids = fields.One2many('hubi.product_category_caliber', 'categ_id', string='Caliber for this category')
    nb_day_dluo = fields.Integer(string='Number day DLUO', default=0)
    
    
    @api.multi
    def action_create_products(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        product_count = 0
        category_id = self.id
        account_income_id = self.property_account_income_categ_id.id
        account_expense_id = self.property_account_expense_categ_id.id
            
        #create  products from the category
        query_args = {'id_category' : self.id}
        
        self._cr.execute("DELETE FROM wiz_create_product_from_category WHERE categ_id=%s ", (self.id,))
        
        query = """SELECT categ_id, caliber_id, hubi_family.id, 
                    caliber_family.name AS Name_Caliber, hubi_family.name AS Name_Packaging, 
                    product_category.complete_name AS Name_Category,
                    product_category.reference AS Ref_Category, caliber_family.reference AS Ref_Caliber, 
                    hubi_family.reference AS Ref_Packaging, hubi_family.weight AS Weight_Packaging  
                    FROM hubi_product_category_caliber 
                    INNER JOIN product_category ON categ_id = product_category.id 
                    INNER JOIN hubi_family AS caliber_family ON caliber_id = caliber_family.id 
                    , hubi_family
                    WHERE hubi_family.level_product='Packaging' AND categ_id=%(id_category)s
                    ORDER BY categ_id, caliber_family.name,  hubi_family.name"""

        self.env.cr.execute(query, query_args)
        ids = [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9]) for r in self.env.cr.fetchall()]
            
        for category, caliber, packaging, caliber_name, packaging_name, category_name, category_ref, caliber_ref, packaging_ref, packaging_weight in ids:
            # Product doesn't exist with this category, caliber and packaging
            id_prod = 0  
            products_templ = self.env['product.template'].search([
            ('categ_id', '=', self.id),
            ('caliber_id', '=', caliber),
            ('packaging_id', '=', packaging), ])         
            for prod in products_templ:
                id_prod = prod.id
            
            if id_prod == 0: 
                price_vals = {
                    'categ_id': category_id,
                    'caliber_id':caliber,
                    'packaging_id': packaging,
                    'caliber_name':caliber_name,
                    'packaging_name': packaging_name,
                    'categ_name':category_name,
                    'categ_reference':category_ref,                    
                    'caliber_reference':caliber_ref,
                    'packaging_reference': packaging_ref,
                    'account_income_id': account_income_id,
                    'account_expense_id': account_expense_id,
                        
                    'weight': packaging_weight,
                    #'weight':_('0'),
                    'price':'0',
                    'quantity':'0',             
                    }

                price = self.env['wiz.create.product.from.category'].create(price_vals)
                product_count = product_count + 1

        self.env.cr.commit()
        message_lib = ("%s %s %s %s ") % ("Create Product for category = (",self.id, ") ", self.name)
        
        #This function opens a window to create  products from the category
        try:
            create_product_form_id = ir_model_data.get_object_reference('hubi', 'create_product_from_category_form_view')[1]
            
        except ValueError:
            create_product_form_id = False
            
        try:
            search_view_id = ir_model_data.get_object_reference('hubi', 'create_product_from_category_search')[1]
            
        except ValueError:
            search_view_id = False
          
        ctx = {
            #'group_by':['category_id','caliber_id'],
            'default_model': 'product.category',
            'default_res_id': self.ids[0],
            'default_categ_id':category_id,
            'default_account_income_id':account_income_id,
            'default_account_expense_id':account_expense_id,
            'default_message':message_lib
            
        }
        domaine = [('categ_id', '=', category_id)]   
         
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [['categ_id', '=', self.id]],
            'res_model': 'wiz.create.product.from.category',
            #'src_model': 'product.category',
            'views': [(create_product_form_id, 'tree')],
            'view_id': create_product_form_id,
            'target': 'new',
            #'context': ctx
            
        }

    
class HubiCategoryCaliber(models.Model):
    _name = "hubi.product_category_caliber"
    
    categ_id = fields.Many2one('product.category', string='Parent Category', index=True, ondelete='cascade')
    caliber_id = fields.Many2one('hubi.family', string='Possible Caliber for this category', ondelete='cascade', index=True, domain=[('level', '=', 'Caliber')])

class HubiInheritedProductProduct(models.Model):
    _inherit = "product.product"
    
    

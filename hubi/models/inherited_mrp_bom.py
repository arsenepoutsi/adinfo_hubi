# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
   
class HubiMrpBom(models.Model):
    _inherit = "mrp.bom"
 
    @api.one
    @api.depends('product_tmpl_id', 'product_id')
    def _get_display_name(self):
        if self.product_tmpl_id:
            products_templ=self.env['product.template']
            products_templ = self.env['product.template'].search([('id', '=', self.product_tmpl_id.id)])            
            #self.info_price = ("%s %s %s %s") % (products_templ.categ_id.display_name, products_templ.family_id.name, products_templ.weight, products_templ.uom_id.name)
            self.display_name = ("%s %s %s %s %s %s %s %s") % ("[",products_templ.default_code,"]",products_templ.categ_id.display_name,"/", products_templ.caliber_id.name," - ", products_templ.packaging_id.name)
       
        else:
            self.display_name = _("")
            

    
    display_name = fields.Char(string='Article', compute='_get_display_name')
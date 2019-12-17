# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
class WizCreateProductFromCategory(models.TransientModel):
    _name = "wiz.create.product.from.category"
    _description = "Wizard create products from the category"
    _order = 'categ_id, caliber_name, packaging_name'

    categ_id= fields.Integer('Category')
    caliber_id= fields.Integer('Caliber')
    packaging_id= fields.Integer('Packaging')
    caliber_name= fields.Char('Caliber Name')
    packaging_name= fields.Char('Packaging Name')
    categ_name= fields.Char('Category Name')
    categ_reference= fields.Char('Category Reference')
    caliber_reference= fields.Char('Caliber Reference')
    packaging_reference= fields.Char('Packaging Reference')

    weight = fields.Float(string='Weight')
    price = fields.Float( string='Default Price Unit')
    quantity = fields.Float( string='Quantity')
    account_income_id = fields.Many2one('account.account', string='Account Income')
    account_expense_id = fields.Many2one('account.account', string='Account Expense')
    etiq_printer = fields.Many2one('hubi.printer', string='Etiq Printer')

#    @api.multi
#    def create(self):
#        self.ensure_one()
#        ir_model_data = self.env['ir.model.data']
#        product_count = 0
#        category_id = self.id
#        #create  products from the category
#        query_args = {'id_category' : self.id}
        
#        self._cr.execute("DELETE FROM wiz_create_product_from_category WHERE categ_id=%s ", (self.id,))
        
#        query = """SELECT categ_id, caliber_id, hubi_family.id, caliber_family.name AS Name_Caliber, hubi_family.name AS Name_Packaging, 
#                    product_category.reference AS Ref_Category, caliber_family.reference AS Ref_Caliber, hubi_family.reference AS Ref_Packaging 
#                    FROM hubi_product_category_caliber 
#                    INNER JOIN product_category ON categ_id = product_category.id 
#                    INNER JOIN hubi_family AS caliber_family ON caliber_id = caliber_family.id 
#                    , hubi_family
#                    WHERE hubi_family.level_product='Packaging' AND categ_id=%(id_category)s
#                    ORDER BY categ_id, caliber_id, hubi_family.id"""

#        self.env.cr.execute(query, query_args)
#        ids = [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]) for r in self.env.cr.fetchall()]
            
#        for category, caliber, packaging, caliber_name, packaging_name, category_ref, caliber_ref, packaging_ref in ids:
#            # Product doesn't exist with this category, caliber and packaging
            
#            price_vals = {
#                    'categ_id': self.id,
#                    'caliber_id':caliber,
#                    'packaging_id': packaging,
#                    'caliber_name':caliber_name,
#                    'packaging_name': packaging_name,
#                    'categ_reference':category_ref,                    
#                    'caliber_reference':caliber_ref,
#                    'packaging_reference': packaging_ref,

#                    'weight':_('0'),
#                    'price':_('0'),             
#                    }

#            price = self.env['wiz.create.product.from.category'].create(price_vals)
#            product_count = product_count + 1

#        self.env.cr.commit()    

    @api.onchange('weight', 'price', 'quantity')
    def _onchange_input(self):
       weight_kg=self.weight
       px=self.price
       qte=self.quantity
       origin_line = getattr(self, '_origin', self)
       self._cr.execute("UPDATE wiz_create_product_from_category SET  weight=%s , price=%s, quantity=%s WHERE id=%s", (weight_kg, px, qte, origin_line.id,))
       self.env.cr.commit()
       
    @api.onchange('etiq_printer')
    def _onchange_printer(self):
       if self.etiq_printer:
           label_printer=self.etiq_printer.id
       
           origin_line = getattr(self, '_origin', self)
           self._cr.execute("UPDATE wiz_create_product_from_category SET  etiq_printer=%s WHERE id=%s", (label_printer, origin_line.id,))
           self.env.cr.commit()       
        
    @api.multi
    def create_product(self):
        #create the product from the category
        self.env.cr.commit()

        category = self.categ_id
        # default uom_id / uom_po_id
        uom_unit = self.env.ref('product.product_uom_unit')
        uom_kg = self.env.ref('product.product_uom_kgm')
        uom_unit_id = uom_unit.id
        uom_kg_id = uom_kg.id
        
        # default taxes
        taxes_ref = self.env.ref('account.field_product_template_taxes_id')
        taxes_supplier_ref = self.env.ref('account.field_product_template_supplier_taxes_id')
        
        taxe_id = 0
        taxes  = self.env['ir.default'].search([('field_id', '=', taxes_ref.id),  ])
        for taxe in taxes:
            taxe_id = taxes.json_value  

        taxe_supplier_id = 0
        taxes_supplier  = self.env['ir.default'].search([('field_id', '=', taxes_supplier_ref.id),  ])
        for taxe_supplier in taxes_supplier:
            taxe_supplier_id = taxes.json_value  

        query_args = {'id_category': self.categ_id, 'id_user': self.env.user.id}
        query = """SELECT caliber_id, packaging_id, caliber_name, packaging_name, categ_name,
                    categ_reference, caliber_reference, packaging_reference, weight, price, quantity, etiq_printer 
                    FROM wiz_create_product_from_category 
                    WHERE categ_id=%(id_category)s AND create_uid=%(id_user)s AND weight<>0"""

        self.env.cr.execute(query, query_args)
        ids = [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11]) for r in self.env.cr.fetchall()]
            
        for caliber_id, packaging_id, caliber_name, packaging_name, categ_name, categ_reference, caliber_reference, packaging_reference, weight, price, quantity, etiq_printer in ids:
            Ref_Interne_Component = categ_reference + caliber_reference
            Ref_Interne = categ_reference + caliber_reference + packaging_reference
            #Name_Product = packaging_name + '*' + categ_reference + caliber_reference
            Name_Product = categ_name + ' ' + caliber_name + ' x ' + packaging_name 
            Name_Interne_Component = categ_name + ' ' + caliber_name
            
            # Create Component product if it doesn't exist with this category, caliber
            id_tmpl_compo = 0  
            products_prod = self.env['product.template'].search([
                ('categ_id', '=', category),
                ('caliber_id', '=', caliber_id), 
                ('packaging_id', '=', False), 
                ('type', '=', 'product'), ])         
            for compo in products_prod:
                id_tmpl_compo = compo.id
            
            if id_tmpl_compo == 0: 
                # Create the product.template
                product_tmpl_compo_vals = {
                    'name': Name_Interne_Component,
                    'default_code': Ref_Interne_Component,
                    'pallet_description': Ref_Interne_Component,
                    'weight': '0',
                    'quantity': '0',
                    'list_price': '0',
                    'categ_id': category,
                    'caliber_id': caliber_id,
                    'packaging_id': _(''),
                    'uom_id': uom_kg_id,
                    'uom_po_id': uom_kg_id,
                    #'taxes_id': taxe_id,
                    #'supplier_taxes_id': taxe_supplier_id,
                    'purchase_ok': True,
                    'sale_ok': False,
                    'type': 'product',
                    'tracking': 'lot',
                     }
                product_tmpl_compo = self.env['product.template'].create(product_tmpl_compo_vals)
                id_tmpl_compo = product_tmpl_compo.id
            
            # Look for the id of the component in product.product
            products_prod_compo = self.env['product.product'].search([
                ('product_tmpl_id', '=', id_tmpl_compo),
                  ])         
            for prod_compo in products_prod_compo:
                id_compo = prod_compo.id
    
            # Create product if it doesn't exist with this category, caliber and packaging
            id_prod = 0  
            products_templ = self.env['product.template'].search([
            ('categ_id', '=', category),
            ('caliber_id', '=', caliber_id),
            ('packaging_id', '=', packaging_id), ])         
            for prod in products_templ:
                id_prod = prod.id
            
            if id_prod == 0: 
                # Create the product.template
                product_tmpl_vals = {
                    'name': Name_Product,
                    'default_code': Ref_Interne,
                    'pallet_description': Name_Product,
                    'weight': weight,
                    'quantity': quantity,
                    'list_price': price,
                    'categ_id': category,
                    'caliber_id': caliber_id,
                    'packaging_id': packaging_id,
                    'uom_id': uom_unit_id,
                    'uom_po_id': uom_unit_id,
                    #'taxes_id': taxe_id,
                    #'supplier_taxes_id': taxe_supplier_id,
                    'purchase_ok': False,
                    'sale_ok': True,
                    'type': 'consu',
                    'tracking': 'none',
                    'etiq_printer': etiq_printer,
                     }
                product_tmpl = self.env['product.template'].create(product_tmpl_vals)

                # Create the product.product  --> automatic creation
                #product_vals = {
                #    'product_tmpl_id': product_tmpl.id,
                #    'default_code': Ref_Interne,
                #    'weight': weight,
                #     }
                #product = self.env['product.product'].create(product_vals)
            
                # Create the component mrp_bom
                mrp_bom_vals = {
                    'product_tmpl_id': product_tmpl.id,
                    'product_qty': '1',
                    'sequence': '0',
                    'product_uom_id': uom_unit_id,
                    'type': 'phantom',
                    'ready_to_produce':'asap',
                     }
                mrp_bom = self.env['mrp.bom'].create(mrp_bom_vals)
                                
                # Create the component mrp_bom_line
                mrp_bom_line_vals = {
                    'product_id': id_compo,
                    'product_qty': weight,
                    'product_uom_id': uom_kg_id,
                    'bom_id': mrp_bom.id,
                     }
                mrp_bom_line = self.env['mrp.bom.line'].create(mrp_bom_line_vals)

            self.env.cr.commit()
        
        self._cr.execute("DELETE FROM wiz_create_product_from_category WHERE categ_id=%s AND create_uid=%s", (self.categ_id, self.env.user.id))
        self.env.cr.commit()
        
        return {'type': 'ir.actions.act_window_close'}
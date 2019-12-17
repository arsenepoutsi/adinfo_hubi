# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, timedelta, datetime
from odoo.exceptions import ValidationError


class Wizard_productprice(models.TransientModel):
    _name = "wiz.productprice"
    _description = "Wizard creation of price"
    
    category_id = fields.Many2one('product.category', 'Internal Category', required=True)
    date_start = fields.Date('Start Date', help="Starting date for the pricelist item validation")
    date_end = fields.Date('End Date', help="Ending valid for the pricelist item validation")

    pricelist_ids = fields.Many2many("product.pricelist")
    message = fields.Text(string="Information")
    
    #@api.multi
    def create_price_item_old(self):
        #pricelist = self.env['product.pricelist'].browse(context['active_ids'])[0]
        pricelist_ids = self.env.context.get('active_ids', [])
        for p in self.env['product.pricelist'].sudo().browse(pricelist_ids):
        #for p in self.env.context["active_ids"]:
            product_categ=self.env['product.template'].search([('categ_id','=', self.category_id.id)])
            for categ in product_categ:
                price_vals = {
                'pricelist_id':p.id,
                'product_tmpl_id': categ.id,
                'applied_on':'1_product',
                'min_quantity':'1',
                'compute_price':'fixed',
                'sequence':'5',
                'base':'list_price',
                'fixed_price':'0',
                'price_discount':'0',
                'price_max_margin':'0',
                'percent_price':'0',
                'price_surchage':'0',
                'price_round':'0',
                'price_min_margin':'0',                
                }
                if self.env.context.get('tx_currency_id'):
                    price_vals['currency_id'] = self.env.context.get('tx_currency_id')

                price = self.env['product.pricelist.item'].create(price_vals)
                #price.post()
        
        view_id = self.env["ir.model.data"].get_object_reference("hubi", "wiz_create_productprice_step2")
        self.message = ("%s %s %s %s %s ") % ("Create Price OK"," / p.id= ",p.id, "/ self.category_id.id = ",self.category_id.id)
        return {"type":"ir.actions.act_window",
                "view_mode":"form",
                "view_type":"form",
                "views":[(view_id[1], "form")],
                "res_id":self.id,
                "target":"new",
                "res_model":"wiz.productprice"                
                }

    #@api.multi
    def create_price_item(self):
        #'fixed_price':_('0'),
        pricelist_ids = self.env.context.get('active_ids', [])
        for p in self.env['product.pricelist'].sudo().browse(pricelist_ids):
            product_count = 0
            product_code = p.id
            categ_code = self.category_id.id 
            company_code = p.company_id.id
            query_args = {'product_code': product_code,'categ_code' : categ_code, 'company_id' : company_code}
            query = """SELECT  Product_template.id, Product_template.list_price, barcode,
                        case Product_template.weight when 0 then Product_template.list_price 
                            else round(Product_template.list_price/Product_template.weight,3) end  as price_w   
                        FROM Product_template 
                        inner join product_product on product_product.product_tmpl_id = Product_template.id
                        WHERE categ_id = %(categ_code)s 
                        AND Product_template.type <> 'service'
                        AND Product_template.company_id = %(company_id)s 
                        AND Product_template.id not in 
                        (SELECT product_tmpl_id FROM product_pricelist_item 
                        WHERE pricelist_id= %(product_code)s AND product_tmpl_id is not null) 
                        AND product_product.id not in 
                        (SELECT product_id FROM mrp_bom_line WHERE  product_id is not null)
                        ORDER BY Product_template.id"""


            self.env.cr.execute(query, query_args)
            ids = [(r[0], r[1], r[2], r[3]) for r in self.env.cr.fetchall()]
            
            for categ, price_total, barcode, price_weight in ids:
                price_vals = {
                    'pricelist_id':p.id,
                    'product_tmpl_id': categ,
                    'applied_on':'1_product',
                    'min_quantity':'1',
                    'compute_price':'fixed',
                    'sequence':'5',
                    'base':'list_price',
                    'fixed_price': price_total,
                    'price_discount':'0',
                    'price_max_margin':'0',
                    'percent_price':'0',
                    'price_surchage':'0',
                    'price_round':'0',
                    'price_min_margin':'0',
                    'price_EAN13': barcode, 
                    'date_start': self.date_start,
                    'date_end': self.date_end, 
                    'price_weight': price_weight,              
                     }
                if self.env.context.get('tx_currency_id'):
                    price_vals['currency_id'] = self.env.context.get('tx_currency_id')

                price = self.env['product.pricelist.item'].create(price_vals)
                product_count = product_count + 1
        
        view_id = self.env["ir.model.data"].get_object_reference("hubi", "wiz_create_productprice_step2")
        self.message = ("%s %s %s %s %s %s %s") % ("Create Price OK  for category = (",self.category_id.id, ") ", self.category_id.complete_name, " for ", product_count, " lines")
        return {"type":"ir.actions.act_window",
                "view_mode":"form",
                "view_type":"form",
                "views":[(view_id[1], "form")],
                "res_id":self.id,
                "target":"new",
                "res_model":"wiz.productprice"                
                }

    
    #@api.model
    def default_get(self, fields):
        
        res = super(Wizard_productprice, self).default_get(fields)
        res["pricelist_ids"] = self.env.context["active_ids"]
        if not self.env.context["active_ids"]:
            raise ValidationError("No select record")
        return res           
        

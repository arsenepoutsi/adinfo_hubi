# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
   
class WizSearchProduct(models.TransientModel):
    _name = "wiz.search.product"
    _description = "Wizard create products from the pricelist in the sale orders"
    
    order_id = fields.Integer('Order id', index=True, required=True)
    pricelist_id = fields.Integer('Price list')
    message = fields.Text(string="Information")
    #pricelist_line_ids = fields.One2many('wiz.search.product.line', 'order_line_id', string='Price list line')
    
    
    _sql_constraints = [
    ('uniq_order', 'unique(order_id)', 'A wiz already exists with this sale order. It must be unique !'),
    ]
      
    #@api.multi
    def search_product(self):

        sale_order_ids = self.env.context.get('active_ids', [])
        sale_order_id = sale_order_ids[0]
        for p in self.env['sale.order'].sudo().browse(sale_order_ids):
            product_count = 0
        
            #create  products depending on the price list
            query_args = {'pricelist_code': p.pricelist_id.id,'date_order' : p.date_order,'id_order' : sale_order_id}
            query = """select product_tmpl_id, date_start, date_end, 
                    case compute_price when 'fixed' then fixed_price else list_price*(1-percent_price/100) end as Price
                    from product_pricelist_item 
                    inner join product_template on product_tmpl_id=product_template.id
                    where (pricelist_id= %(pricelist_code)s ) and (product_tmpl_id is not null) 
                    and (date_start<=%(date_order)s  or date_start is null)
                    and (date_end>=%(date_order)s  or date_start is null)
                    order by product_tmpl_id"""

            self.env.cr.execute(query, query_args)
            ids = [(r[0], r[1], r[2], r[3]) for r in self.env.cr.fetchall()]
            
            for product, date_start, date_end, unit_price in ids:
                price_vals = {
                    'order_line_id': sale_order_id,
                    'pricelist_line_id':self.pricelist_id,
                    'product_id': product,
                    'qty_invoiced':'1',
                    'price_unit':unit_price,
                    'date_start': date_start,
                    'date_end': date_end,               
                     }

                price = self.env['wiz.search.product.line'].create(price_vals)
                #price.write(price_vals)
                product_count = product_count + 1

        self.env.cr.commit()
       
        view_id = self.env["ir.model.data"].get_object_reference("hubi", "search_product_wizard_form_step2")
        #view_id = self.env["ir.model.data"].get_object_reference("hubi", "Price_List_Lines_form_view")
        self.message = ("%s %s %s %s %s %s") % ("Create Product for price list = (",self.pricelist_id, ") ", p.pricelist_id.name, " * ",self.id)
        return {"type":"ir.actions.act_window",
                "view_mode":"form",
                "view_type":"form",
                "views":[(view_id[1], "form")],
                "res_id":self.id,
                "target":"new",
                "res_model":"wiz.search.product"                
                }
        
    #@api.model
    #def default_get(self, fields):
        
        #res = super(WizSearchProduct, self).default_get(fields)
        #caller_id = self._context.get('active_id')
        #if caller_id:
        #    res['pricelist_id'] = self._context.get('pricelist_id')
    

        #res["pricelist_ids"] = self.env.context["active_ids"]
        #if not self.env.context["active_ids"]:
        #    raise ValidationError("No select record")
        
        #sale_order_ids = self.env.context.get('active_ids', [])
        #for p in self.env['sale.order'].sudo().browse(sale_order_ids):
        #    res["sale_order_id"] = sale_order_ids[0]
        #    res["pricelist_id"] =p.pricelist_id.id
        #    res["message"] = ("%s %s %s %s ") % ("Create Product for price list = (",p.pricelist_id.id, ") ", p.pricelist_id.name)
        
        
        #return res      
 
class WizSearchProductLine(models.TransientModel):
    _name = "wiz.search.product.line"
    _description = "Wizard create products line from price list in the sale orders"
    _order = 'order_line_id, category_id, caliber_id, product_id'
    
    order_line_id= fields.Integer('Order')
    pricelist_line_id= fields.Integer('Price list')
    product_id = fields.Many2one('product.product', 'Product')
    qty_invoiced = fields.Float(string='Quantity')
    price_unit = fields.Float( string='Price Unit')
    date_start = fields.Date(string='Date Start')
    date_end = fields.Date(string='Date End')
    category_id= fields.Char('Category')
    caliber_id= fields.Char('Caliber')

    #@api.onchange('qty_invoiced', 'price_unit')
    #def _onchange_reference(self):
    #   qty=self.qty_invoiced
    #   px=self.price_unit
    #   origin_line = getattr(self, '_origin', self)
    #   self._cr.execute("UPDATE wiz_search_product_line SET  qty_invoiced=%s , price_unit=%s WHERE id=%s", (qty,px,origin_line.id,))
    #   self.env.cr.commit()
       
    @api.onchange('qty_invoiced')
    def _onchange_qty(self):
        origin_line = getattr(self, '_origin', self)
        # Find price for this quantity
        pricelist_item = self.env['product.pricelist.item'].search([
            ('pricelist_id', '=', self.pricelist_line_id),
            ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id)], order='min_quantity desc')
        for item in pricelist_item:
            if item.min_quantity <= self.qty_invoiced:
               #case compute_price when 'fixed' then fixed_price else list_price*(1-percent_price/100) end as Price
                if item.compute_price == 'fixed':
                   self.price_unit = item.fixed_price  
                else:
                   self.price_unit =  item.product_tmpl_id.list_price*(1-item.percent_price/100) 

                values = ({ 
                    'price_unit' : self.price_unit or 0.00,
                    'qty_invoiced': self.qty_invoiced or 0.00, 
                    })
                #self.update(values) 
                
                 
                #self.super(WizSearchProductLine, self.sudo()).write({
                #    'price_unit': self.price_unit or 0.00,
                #    'qty_invoiced': self.qty_invoiced or 0.00 
                #})
                self._cr.execute("UPDATE wiz_search_product_line SET  qty_invoiced=%s , price_unit=%s WHERE id=%s", (self.qty_invoiced,self.price_unit,origin_line.id,))
                self.env.cr.commit()
                return 
        
        values = ({ 
            'qty_invoiced': self.qty_invoiced or 0.00, 
            })
        self._cr.execute("UPDATE wiz_search_product_line SET  qty_invoiced=%s  WHERE id=%s", (self.qty_invoiced,origin_line.id,))
        self.env.cr.commit()
        #self.update(values)   

    @api.onchange('price_unit')
    def _onchange_price(self):
        origin_line = getattr(self, '_origin', self)
        values = ({ 
            'price_unit' : self.price_unit or 0.00,
            'qty_invoiced': self.qty_invoiced or 0.00, 
            })
        #self.update(values)
        self._cr.execute("UPDATE wiz_search_product_line SET  price_unit=%s WHERE id=%s", (self.price_unit,origin_line.id,))
        self.env.cr.commit()   
        
    #@api.multi
    def update_sale(self):
        #update sale line depending on the price list
        #origin_line = getattr(self, '_origin', self)
        #self._cr.execute("UPDATE wiz_search_product_line SET  qty_invoiced=%s , price_unit=%s WHERE id=%s", (self.qty_invoiced,self.price_unit,origin_line.id,))
        #self.env.cr.commit()
       
        pricelist = self.pricelist_line_id
        order_line = self.order_line_id
        query_args = {'pricelist_code': self.pricelist_line_id, 'id_order' : self.order_line_id, 'id_user': self.env.user.id}
        query = """SELECT product_id,qty_invoiced, price_unit 
                    FROM wiz_search_product_line 
                    WHERE order_line_id=%(id_order)s AND pricelist_line_id=%(pricelist_code)s AND create_uid=%(id_user)s AND qty_invoiced<>0"""

        self.env.cr.execute(query, query_args)
        ids = [(r[0], r[1], r[2]) for r in self.env.cr.fetchall()]
            
        for product, qty, unit_price in ids:
            price_vals = {
                    'order_id': self.order_line_id,
                    'product_id': product,
                    'product_uom_qty':qty,
                    'price_unit':unit_price,
                     }

            price = self.env['sale.order.line'].create(price_vals)

        self.env.cr.commit()
        
        self._cr.execute("DELETE FROM wiz_search_product_line WHERE order_line_id=%s AND pricelist_line_id=%s AND create_uid=%s", (order_line, pricelist, self.env.user.id))
        self.env.cr.commit()
        
        return {'type': 'ir.actions.act_window_close'}
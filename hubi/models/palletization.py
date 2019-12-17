# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HubiPalletization(models.Model):
    _name = 'hubi.palletization'
    _description = "Palletization"
    _order = 'name'
 
    def _get_qty(self):
        return (self.uom_qty or 0) - (self.pallet_qty  or 0)
    
    def _get_default_company_id(self):
        #return self._context.get('force_company', self.env.user.company_id.id)
        return self.env['sale.order'].search([('id', '=', self.order_id.id)]).company_id.id
   
   
    name = fields.Char(string='Name', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=_get_default_company_id, required=True)
    order_id = fields.Many2one('sale.order', string='Order Reference', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    default_pallet_qty = fields.Float(string='Default Quantity on the Pallet')
    uom_qty = fields.Float(string='Order Quantity')
    pallet_qty = fields.Float(string='Quantity on the Pallet')
    residual_qty = fields.Float(string='Residual Quantity', compute='_residual_qty')
    input_pallet_id = fields.Many2one('hubi.palletization.line', string='Complete No Pallet')
    #input_pallet_id = fields.Many2one('hubi.palletization.line', string='Complete No Pallet', domain="[('order_id', '=', order_id)]")
    
    input_qty = fields.Float(string='Complete Quantity', default=_get_qty)
    
    
    #@api.onchange('default_pallet_qty')
    #def onchange_order_id(self):
    #    res = {}
    #    if self.order_id:
    #        order_number = self._context.get('active_id')
    #        res['domain'] = {'input_pallet_id': [('order_id', '=', order_number)]}
    #    return res

    #@api.one
    def _default_qty(self):
        self.default_pallet_qty = self.product_id.default_pallet_qty
 
    #@api.one
    def _residual_qty(self):
        #qty_p = self.pallet_qty  or 0
        #qty_o = self.uom_qty or 0
        #pallet_line=self.env['hubi.palletization'].search([('order_line_id','=', self.id)])
        #for line in pallet_line:
        #    if line.quantity :
        #        qty_p = line.quantity
           
        self.residual_qty = (self.uom_qty or 0) - (self.pallet_qty  or 0)

    def new_pallet(self):
        self.env.cr.commit() 
        
        #company_code = self.env['sale.order'].search([('id', '=', self.id)]).company_id.id or self._context.get('company_id') or self.env['res.users']._get_company().id
        company_code = self.env['sale.order'].search([('id', '=', self.order_id.id)]).company_id.id
        id_order = self.order_id.id
        
        max_qty = self.default_pallet_qty
        if self.residual_qty != 0 and max_qty > 0:
            # Find the last pallet
            no_pallet = 0
            query_args = {'id_order' : id_order, 'company_code' : company_code}
            query = """SELECT pallet_no FROM hubi_palletization_line 
                    WHERE order_id=%(id_order)s and company_id=%(company_code)s 
                    order by pallet_no desc LIMIT 1"""

            self.env.cr.execute(query, query_args)
            ids = [(r[0]) for r in self.env.cr.fetchall()]
            
            for last_no in ids:
                no_pallet=last_no 
            
            reste = self.residual_qty
            qty_a_pl= self.residual_qty
            new_qty_pallet = self.pallet_qty + self.residual_qty
     
            palletization_line_ids = self.env['hubi.palletization.line'].search([('palletization_id', '=', self.id), ('company_id', '=', company_code)])
            if (not palletization_line_ids) or (qty_a_pl != 0):
                qty = 0
 
                if max_qty > 0:
                    while qty_a_pl !=0:
                        if qty_a_pl >= max_qty:
                            qty = max_qty
                            reste = qty_a_pl - max_qty
                        else:
                            qty = qty_a_pl
                            reste = 0
                
                        qty_a_pl = reste
                        no_pallet += 1
                    
                        # Create palletization line
                        # 'company_id': self._context.get('force_company', self.env.user.company_id.id),
                        name_line = ('Order : %s / Pallet : %s') % (self.order_id.id,no_pallet)
                        pallet_line_vals = {
                            'name': name_line,
                            'company_id': company_code,
                            'palletization_id':self.id,
                            'order_id': self.order_id.id,
                            'product_id': self.product_id.id,
                            'quantity': qty,
                            'pallet_no': no_pallet,
                            
                            }
                        palletization_line = self.env['hubi.palletization.line'].create(pallet_line_vals)  
                
                    # Update pallet_qty on hubi_palletization
                    self._cr.execute("UPDATE hubi_palletization set pallet_qty = %s, input_qty = %s WHERE id=%s ", (new_qty_pallet, reste, self.id))
                    self.env.cr.commit()
        
    def complete_pallet(self):
        self.env.cr.commit() 
        
        #company_code = self.env['sale.order'].search([('id', '=', self.id)]).company_id.id or self._context.get('company_id') or self.env['res.users']._get_company().id
        company_code = self.env['sale.order'].search([('id', '=', self.order_id.id)]).company_id.id
        id_order = self.order_id.id
        
        max_qty = self.default_pallet_qty
        no_pallet = self.input_pallet_id.pallet_no
        no_product = self.product_id.id
        
        if self.input_qty != 0 and self.input_pallet_id != 0 and self.residual_qty != 0 and max_qty > 0:
            if self.input_qty > self.residual_qty:
                qty_a_pl = self.residual_qty
            else:    
                qty_a_pl = self.input_qty 
            
            new_qty_pallet = self.pallet_qty + qty_a_pl  
            reste = self.residual_qty - qty_a_pl
            
            # Update pallet_qty on hubi_palletization
            self._cr.execute("UPDATE hubi_palletization set pallet_qty = %s, input_qty = %s, input_pallet_id= null WHERE id=%s ", (new_qty_pallet, reste, self.id))
            
            
            # Find the line in hubi_palletization_line for this pallet_id and this product_id
            palletization_line_ids = self.env['hubi.palletization.line'].search([('palletization_id', '=', self.id), ('pallet_no', '=', no_pallet), ('product_id', '=', no_product), ('company_id', '=', company_code) ])
            if (not palletization_line_ids):
                # Create palletization line
                name_line = ('Order : %s / Pallet : %s') % (self.order_id.id, no_pallet)
                pallet_line_vals = {
                    'name': name_line,
                    'company_id': company_code,
                    'palletization_id':self.id,
                    'order_id': self.order_id.id,
                    'product_id': no_product,
                    'quantity': qty_a_pl,
                    'pallet_no': no_pallet,
                    }
                palletization_line = self.env['hubi.palletization.line'].create(pallet_line_vals)  
            else:
                # Update quantity on hubi_palletization_line
                new_qty = palletization_line_ids.quantity + qty_a_pl 
                self._cr.execute("UPDATE hubi_palletization_line set quantity = %s WHERE palletization_id=%s and pallet_no=%s and product_id=%s  and company_id=%s  ", 
                                 (new_qty, self.id, no_pallet, no_product, company_code))

            self.env.cr.commit() 

  
        
    #@api.model
    #def get(self, name, model, res_id=False):
    #    domain = self._get_domain(name, model)
    #    if domain is not None:
    #        domain = [('res_id', '=', res_id)] + domain
    #        order_number = self._context.get('active_id')
    #        res['domain'] = {'input_pallet_id': [('order_id', '=', order_number)]}
            #make the search with company_id asc to make sure that properties specific to a company are given first
            #prop = self.search(domain, limit=1, order='company_id')
            #if prop:
            #    return prop.get_by_record()
    #    return False

    #def _get_domain(self, prop_name, model):
        #self._cr.execute("SELECT id FROM ir_model_fields WHERE name=%s AND model=%s", (prop_name, model))
        #res = self._cr.fetchone()
        #if not res:
        #    return None
        #company_id = self._context.get('force_company') or self.env['res.company']._company_default_get(model, res[0]).id
        #return [('fields_id', '=', res[0]), ('company_id', 'in', [company_id, False])]
        #res = {}
        #if self.order_id:
        #    order_number = self._context.get('active_id')
        #    res['domain'] = {'input_pallet_id': [('order_id', '=', order_number)]}
        #return res
        
        
class HubiPalletizationLine(models.Model):
    _name = "hubi.palletization.line"
    _description = "Palletization Line"
    _order = 'name'
     
    def _get_default_company_id(self):
        #return self.env['sale.order'].search([('id', '=', self.id)]).company_id.id or self._context.get('force_company', self.env.user.company_id.id)
        return self.env['sale.order'].search([('id', '=', self.order_id.id)]).company_id.id
   
    name = fields.Char(string='Name', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=_get_default_company_id, required=True)
    palletization_id = fields.Many2one('hubi.palletization', string='Palletization Reference', required=True)
    #order_id = fields.Char(string='sale.order')
    order_id = fields.Many2one('sale.order', string='Order Reference', required=True)
    pallet_no = fields.Integer(string='Pallet Number')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity on the Pallet')

    def delete_pallet(self):
        self.env.cr.commit() 

        # delete in hubi.palletization.line
        #company_code = self.env['sale.order'].search([('id', '=', self.id)]).company_id.id or self._context.get('company_id') or self.env['res.users']._get_company().id
        company_code = self.env['sale.order'].search([('id', '=', self.order_id.id)]).company_id.id
        id_order = self.order_id.id

        qty = self.quantity
        palletization_id = self.palletization_id.id
        no_pallet_supp = self.pallet_no
        order_id = self.order_id.id
        no_product = self.product_id.id
        
        self._cr.execute("DELETE FROM hubi_palletization_line  WHERE id=%s ", (self.id,))
 
        # update in hubi.palletization : pallet_qty
        palletization_ids = self.env['hubi.palletization'].search([('id', '=', palletization_id)])
        if (palletization_ids) :
            qty_p =(palletization_ids.pallet_qty or 0) - qty
            qty_r =(palletization_ids.uom_qty or 0) - (qty_p  or 0)
            #palletization_ids.write({"pallet_qty":[(4, qty_p)]})
            palletization_ids.write({'pallet_qty': qty_p})
            palletization_ids.write({'input_qty': qty_r})
            
        
        #new_no_pallet = no_pallet_supp
        
        no_pallet_exist = False
        pallets = self.env['hubi.palletization.line'].search([('order_id', '=', order_id), ('company_id', '=', company_code), ('pallet_no', '=', no_pallet_supp)] , order='pallet_no asc')
        for pallet in pallets:
            no_pallet_exist = True
            
        if (not no_pallet_exist):
            # rename No pallet : 
            pallets = self.env['hubi.palletization.line'].search([('order_id', '=', order_id), ('company_id', '=', company_code), ('pallet_no', '>=', no_pallet_supp)] , order='pallet_no asc')
            for pallet in pallets:
                new_no_pallet = pallet.pallet_no
                if (pallet.pallet_no == 1):
                    new_no_pallet = 1
                else:    
                    new_no_pallet = new_no_pallet - 1
                name_line = ('Order : %s / Pallet : %s') % (order_id, new_no_pallet)
                pallet.write({'name': name_line, 'pallet_no': new_no_pallet})
            
            #new_no_pallet += 1
                
        self.env.cr.commit()
        
        
class HubiProductPalletization(models.Model):
    _inherit = "product.template"

    pallet_description = fields.Char(string='Pallet Description') 
    default_pallet_qty = fields.Float(string='Default Quantity on the Pallet')

class HubiSaleOrderPalletization(models.Model):
    _inherit = "sale.order"

    palletization_ids = fields.One2many('hubi.palletization', 'order_id', string='Palletization Lines', copy=True, auto_join=True)
    palletization_line_ids = fields.One2many('hubi.palletization.line', 'order_id', string='Palletization Pallets')

    def create_pallet(self):
        self.env.cr.commit()
        # Find the last pallet
        #company_code = self.env['sale.order'].search([('id', '=', self.id)]).company_id.id or self._context.get('company_id') or self.env['res.users']._get_company().id
        company_code = self.env['sale.order'].search([('id', '=', self.id)]).company_id.id
        id_order = self.id

        no_pallet = 0
        query_args = {'id_order' : id_order, 'company_code' : company_code}
        query = """SELECT pallet_no FROM hubi_palletization_line 
                    WHERE order_id=%(id_order)s  and company_id=%(company_code)s  
                    order by pallet_no desc LIMIT 1"""

        self.env.cr.execute(query, query_args)
        ids = [(r[0]) for r in self.env.cr.fetchall()]
            
        for last_no in ids:
            no_pallet=last_no 
        
        # Update pallet_qty on hubi_palletization

        # Find the sale.order.line
        query="""SELECT  order_id, product_id,
                coalesce(product_template.default_pallet_qty,0) AS default_pallet_qty,
                sum(product_uom_qty)  AS uom_qty   
                FROM sale_order_line 
                inner join product_product on product_id = product_product.id
                inner join product_template on product_template.id = product_product.product_tmpl_id
                where order_id = %(id_order)s  and sale_order_line.company_id=%(company_code)s 
                group by order_id, product_id,
                product_template.default_pallet_qty
                order by order_id, product_id"""    

        self.env.cr.execute(query, query_args)
        ids = [(r[0],r[1],r[2],r[3]) for r in self.env.cr.fetchall()]
            
        for  order_id, prod_id, max_qty, uom_qty in ids:
            if max_qty >0:
                palletization_ids = self.env['hubi.palletization'].search([('order_id', '=', order_id), ('product_id', '=', prod_id), ('company_id', '=', company_code)])
                if not palletization_ids:
                    # Create palletization 
                    name_line = ('Order : %s ') % (order_id)
                    pallet_vals = {
                        'name': name_line,
                        'company_id': company_code,
                        'order_id': order_id,
                        'product_id': prod_id,
                        'uom_qty': uom_qty,
                        'default_pallet_qty': max_qty,
                        'pallet_qty': 0,
                        }
                    palletization = self.env['hubi.palletization'].create(pallet_vals)  
                else:
                    query_maj = """UPDATE hubi_palletization set uom_qty = %s, default_pallet_qty = %s  
                    WHERE order_id=%s AND product_id=%s  and company_id=%s """
                    self._cr.execute(query_maj, (uom_qty, max_qty, order_id, prod_id, company_code))
                    self.env.cr.commit()
                    
            
        # Create palletization line    
        query="""SELECT id, order_id, product_id,
                coalesce(default_pallet_qty,0) AS default_pallet_qty,
                coalesce(uom_qty,0)  AS uom_qty,
                coalesce(pallet_qty,0)  AS pallet_qty     
                FROM hubi_palletization
                where order_id = %(id_order)s  and company_id=%(company_code)s 
                order by order_id, product_id"""    

        self.env.cr.execute(query, query_args)
        ids = [(r[0],r[1],r[2],r[3],r[4],r[5]) for r in self.env.cr.fetchall()]
            
        for  palletization_id, order_id, prod_id, max_qty, uom_qty, pallet_qty in ids:
            reste = uom_qty - pallet_qty
            qty_a_pl= uom_qty - pallet_qty
                
            palletization_line_ids = self.env['hubi.palletization.line'].search([('palletization_id', '=', palletization_id), ('company_id', '=', company_code)])
            if (not palletization_line_ids) or (qty_a_pl != 0):
                qty = 0
 
                if max_qty > 0:
                    while qty_a_pl !=0:
                        if qty_a_pl >= max_qty:
                            qty = max_qty
                            reste = qty_a_pl - max_qty
                        else:
                            qty = qty_a_pl
                            reste = 0
                
                        qty_a_pl = reste
                        no_pallet += 1
                    
                        # Create palletization line
                        name_line = ('Order : %s / Pallet : %s') % (order_id, no_pallet)
                        pallet_line_vals = {
                            'name': name_line,
                            'company_id': company_code,
                            'palletization_id': palletization_id,
                            'order_id': order_id,
                            'product_id': prod_id,
                            'quantity': qty,
                            'pallet_no': no_pallet,
                            
                            }
                        palletization_line = self.env['hubi.palletization.line'].create(pallet_line_vals)  
                
                    # Update pallet_qty on hubi_palletization
                    self._cr.execute("UPDATE hubi_palletization set pallet_qty = %s, input_qty = %s WHERE id=%s ", (uom_qty, reste, palletization_id))
                    self.env.cr.commit()
                  
                    
                    
    #@api.multi
    def action_palletization(self):
        self.env.cr.commit()
        self.create_pallet()  
        
        self.ensure_one()
        view_id = self.env["ir.model.data"].get_object_reference("hubi", "hubi_palletization_form")
        
        action = self.env.ref('hubi.action_hubi_palletization').read()[0]
        ##action['views'] = [(self.env.ref('hubi.hubi_palletization_form').id, 'form')]
        action['views'] = [(view_id[1], 'form')]
        action['res_id'] = self.id
        action['res_model'] = "sale.order"
        
        return action
    
        #return {"type":"ir.actions.act_window",
        #        "view_mode":"form",
        #        "view_type":"form",
        #        "views":[(view_id[1], "form")],
        #        "res_id": 'sale.order' and self.id,
        #        "res_model":"sale.order"                
        #        }
    
       
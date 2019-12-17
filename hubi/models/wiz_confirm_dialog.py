# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, timedelta, datetime
from odoo.exceptions import ValidationError


class Wizard_confirm_dialog(models.TransientModel):
    _name = "wiz.confirm.dialog"
    _description = "Wizard for confirm dialog"
    
    confirm_message = fields.Text(string="Information")
    code_message = fields.Text(string="Code Message")
    
    @api.multi
    def wiz_update_sale_batch_number(self):
        sale_ids = self.env['sale.order'].browse(self._context.get('active_ids', []))
        sale_ids.update_sale_batch_number()

    
    @api.multi
    def wiz_update_product_etiq(self):
        prod_ids = self.env['product.template'].browse(self._context.get('active_ids', []))
        prod_ids.update_product_etiq()
        
        #context = dict(self._context or {})
        #active_ids = context.get('active_ids', []) or []
        
        #self.env.cr.commit()
        
        #prod_compos = self.env['product.template'].browse(self._context.get('active_ids', []))
        #for compo in prod_compos:
            # Search products from this category and caliber
        #    products=self.env['product.template'].search([
        #        ('categ_id', '=', compo.categ_id.id),
        #        ('caliber_id', '=', compo.caliber_id.id),
        #        ('packaging_id', '!=', False),    ])   
        #    for prod in products:
        #        if compo.etiq_printer and not prod.etiq_printer:   
        #            prod.write({'etiq_printer':compo.etiq_printer})
        #        if compo.etiq_mention and not prod.etiq_mention:   
        #            prod.write({'etiq_mention':compo.etiq_mention})    
        #        if compo.etiq_description and not prod.etiq_description:   
        #            prod.write({'etiq_description':compo.etiq_description})  
        #        if compo.etiq_latin and not prod.etiq_latin:   
        #            prod.write({'etiq_latin':compo.etiq_latin})  
        #        if compo.etiq_spanish and not prod.etiq_spanish:   
        #            prod.write({'etiq_spanish':compo.etiq_spanish})     

        
        #return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def wiz_create_credit_note(self):
        invoice_ids = self.env['wiz.creditnote'].browse(self._context.get('active_ids', []))
        res = invoice_ids.create_credit_note()
        
        if len(res) >= 1:
            action  = self.env.ref('account.action_invoice_out_refund').read()[0]
            action['domain'] = [('id', 'in', res),('type','=','out_refund')]    
            return action
            
            #view = self.env.ref('account.invoice_tree')
            #try:
            #    invoice_tree_id = self.env["ir.model.data"].get_object_reference("account", "invoice_tree")[1]
            #except ValueError:
            #    invoice_tree_id = False
            
            #return {'type':'ir.actions.act_window',
            #    'name':'Credit Note CA' ,
            #    'res_model':'account.invoice' , 
            #    'view_mode':'tree,form,calendar,graph',
            #    'view_type':'form',
            #    'views': [(view.id, 'tree')],
            #    'view_id': view.id,
            #    'domain':[('id', 'in', res),('type','=','out_refund')], 
            #    'context':{'type':'out_refund'} ,
            #    #'target': 'new'
            #    }
        else:    
            return {'type': 'ir.actions.act_window_close'}
        
    @api.multi
    def wiz_prepare_order_line_print_label(self):
        sale_order_ids = self.env['wiz_sale_order_print_label'].browse(self._context.get('active_ids', []))
        res = sale_order_ids.load_order_line('order')
        
        if len(res) >= 1:
            action = self.env.ref('hubi.action_wiz_sale_order_print_label_tree').read()[0]
            action['domain'] = [('id', 'in', res)]
        else:
            action = {'type': 'ir.actions.act_window_close'}    
            
        return action  
        
        
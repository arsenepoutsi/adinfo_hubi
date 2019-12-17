# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, timedelta, datetime
import time
import calendar
from dateutil.relativedelta import relativedelta


class Wizard_prepare_creditnote_ca(models.TransientModel):
    _name = "wiz.prepare.creditnote"
    _description = "Wizard preparation of credit-note from invoice"
    
    def add_months(sourcedate,months):
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month // 12
        month = month % 12 + 1
        day = min(sourcedate.day,calendar.monthrange(year,month)[1])
        return datetime.date(year,month,day)


    #@api.model
    def _default_start(self):
        return fields.Date.context_today(self)

    #@api.model
    def _default_finish(self):
        finish = datetime.today() + timedelta(days=7)
        return fields.Date.context_today(self, timestamp=finish)
    
    #@api.model
    def _default_product_id(self):
        product_id = self.env['ir.config_parameter'].sudo().get_param('hubi.default_discount_ca_product_id')
        return self.env['product.product'].browse(int(product_id))
    
    #@api.model
    @api.onchange('periodicity_creditnote')
    def onchange_periodicity_creditnote(self):
        finish = datetime.today()
        
        if self.periodicity_creditnote == "Annual":
            finish = datetime.today() + relativedelta(months=-12) 
        if self.periodicity_creditnote == "Quarterly":
            finish = datetime.today() + relativedelta(months=-3) 
        if self.periodicity_creditnote == "Monthly":
            #start_date = datetime.today()
            #days_in_month = calendar.monthrange(start_date.year, start_date.month)[1]
            #finish = start_date + timedelta(days=-days_in_month)
            finish = datetime.today()+ relativedelta(months=-1) 
        
        self.date_start = finish
    
    
    periodicity_creditnote = fields.Selection([("Monthly", "Monthly"),("Quarterly", "Quarterly"),
                    ("Annual", "Annual")], string="Credit-note Period", default='Monthly')
    #date_start = fields.Date('Start Date', help="Starting date for the creation of invoices",default=_default_finish)
    date_start = fields.Date('Start Date', help="Starting date for the creation of credit-note",default=lambda self: fields.Date.today())
    date_end = fields.Date('End Date', help="Ending valid for the the creation of credit-note", default=lambda self: fields.Date.today())
    date_creditnote = fields.Date(string="Credit-note Date", default=lambda self: fields.Date.today()) 
    product_id = fields.Many2one('product.product', string='Discount Product', domain=[('type', '=', 'service')],
        default=_default_product_id)
    #invoice_ids = fields.Many2many("wiz.creditnote", string='Credit-note')
     
    message = fields.Text(string="Information")
   
    #@api.model
    #@api.multi
    def action_view_prepare_creditnote(self):
        #invoices = self.mapped('invoice_ids')
        #action = self.env.ref('account.action_invoice_tree1').read()[0]
        #if len(invoices) > 1:
        #    action['domain'] = [('id', 'in', invoices.ids)]
        #elif len(invoices) == 1:
        #    action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
        #    action['res_id'] = invoices.ids[0]
        #else:
        #    action = {'type': 'ir.actions.act_window_close'}
        query_args = {'origin_id': self.id}
        query = """ SELECT  origin_id FROM wiz_creditnote
                    WHERE origin_id = %(origin_id)s """

        self.env.cr.execute(query, query_args)
        invoices = [r[0] for r in self.env.cr.fetchall()]
        #invoices = self.env['wiz_creditnote'].search([('id', 'in', ids)])
        
        if len(invoices) > 1:
            action = self.env.ref('hubi.action_creditnote_tree').read()[0]
            action['domain'] = [('origin_id', 'in', invoices)]
        else:
            action = {'type': 'ir.actions.act_window_close'}    
            
        return action  
   
    #@api.multi
    def prepare_creditnote_ca(self):  
        self._cr.execute("DELETE FROM wiz_creditnote WHERE create_uid=%s", (self.env.user.id,))
        self.env.cr.commit()
        date_fin = datetime.strptime(self.date_end, "%Y-%m-%d")  + timedelta(hours=23) + timedelta(minutes=59) + timedelta(seconds=59)

        query_args = {'periodicity_creditnote': self.periodicity_creditnote,'date_start' : self.date_start,'date_end' : date_fin, 'company_id' : self.env.user.company_id.id}
        query = """ SELECT  account_invoice.number, account_invoice.date_invoice,
                    CASE account_invoice.type WHEN  'out_refund' THEN 'A' ELSE 'F' END AS type_invoice ,
                    account_invoice.commercial_partner_id, account_invoice.partner_id,
                    account_invoice_line_tax.tax_id, res_partner.discount_ca, res_partner.discount_description,
                    sum(account_invoice_line.price_subtotal_signed) AS price_subtotal
                FROM account_invoice 
                    INNER JOIN res_partner ON res_partner.id = account_invoice.commercial_partner_id 
                    INNER JOIN account_invoice_line ON account_invoice_line.invoice_id = account_invoice.id
                    INNER JOIN account_invoice_line_tax ON account_invoice_line_tax.invoice_line_id = account_invoice_line.id
                    INNER JOIN account_tax ON account_tax.id = account_invoice_line_tax.tax_id 
                WHERE (account_invoice.type = 'out_invoice'  OR account_invoice.type = 'out_refund')
                    AND state <> 'draft'
                    AND date_invoice between %(date_start)s AND %(date_end)s
                    AND res_partner.discount_period_ca = %(periodicity_creditnote)s 
                    AND account_invoice.company_id = %(company_id)s
                GROUP BY account_invoice.number, account_invoice.date_invoice,
                    CASE account_invoice.type WHEN  'out_refund' THEN 'A' ELSE 'F' END ,
                    account_invoice.commercial_partner_id, account_invoice.partner_id,
                    account_invoice_line_tax.tax_id, res_partner.discount_ca, res_partner.discount_description
                ORDER BY account_invoice.partner_id, account_invoice.number
                """

        self.env.cr.execute(query, query_args)
        ids = [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8]) for r in self.env.cr.fetchall()]
        for number_invoice, date_invoice, type_invoice, commercial_partner_id, partner_id, tax_id, discount_ca,discount_description, price_subtotal in ids:
            Name_Discount = self.product_id.name + ' ' + self.periodicity_creditnote
            discount_vals = {
                    'name': Name_Discount,
                    'number_invoice': number_invoice,
                    'date_invoice': date_invoice,
                    'type_invoice': type_invoice,
                    'partner_id': partner_id,
                    'product_id': self.product_id.id,
                    'quantity': '1',
                    'price_unit': price_subtotal,
                    #'discount':  '0',
                    'discount':  discount_ca,
                    'note': discount_description,
                    #'tax_id': tax_id.id,
                    'tax_id': tax_id,
                    'date_creditnote': self.date_creditnote,
                    'origin_id': self.id,
                     }
            prepare_creditnote = self.env['wiz.creditnote'].create(discount_vals)
        self.env.cr.commit() 
        #view_id = self.env["ir.model.data"].get_object_reference("hubi", "view_hubi_creditnote_tree")
        #return {"type":"ir.actions.act_window",
        #        "view_mode":"tree",
        #        "view_type":"form",
        #        "views":[(view_id[1], "form")],
        #        "res_id":self.id,
        #        "target":"new",
        #        "res_model":"wiz.affect.contract"                
        #        }
        
        #return {'type': 'ir.actions.act_window_close'} 
        return self.action_view_prepare_creditnote()    
    
    
class Wizard_create_creditnote_ca(models.Model):
    _name = "wiz.creditnote"
    _description = "Wizard creation of credit-note from invoice"
    
    number_invoice = fields.Char(string="Number Invoice")
    type_invoice = fields.Char(string="Type Invoice")
    date_invoice = fields.Date(string="Date Invoice")
    partner_id = fields.Many2one('res.partner', string='Partner')
    product_id = fields.Many2one('product.product', string='Discount Product', domain=[('type', '=', 'service')])
    quantity = fields.Float( string='Quantity')
    price_unit = fields.Float( string='Price Unit')
    discount = fields.Float( string='Discount')
    tax_id = fields.Many2one('account.tax', string='Tax')
    date_creditnote = fields.Date(string="Credit-note Date") 
    
    name = fields.Char(string="Name")
    note = fields.Text(string="Information")
    origin_id = fields.Integer('Origin')
    creditnote_ok = fields.Boolean('OK', default=False)
    
    #@api.multi
    def create_credit_note(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        user_id = self.env.user.id
        
        self.env.cr.commit()
        params = [tuple(active_ids)]
        
        query = """SELECT partner_id, date_creditnote, product_id, quantity,
                    discount, tax_id, name, note, create_uid, sum(price_unit) as price_unit
                    FROM wiz_creditnote where create_uid = """ + str(user_id) + """ AND id in %s
                    GROUP BY  partner_id, date_creditnote, product_id, quantity,
                    discount, tax_id, name, note, create_uid
                    ORDER BY partner_id
                   """
        #self._cr.execute(query, (user_id, tuple(self.ids)))
        self._cr.execute(query, tuple(params))
        
        #lines_invoice = self.env['wiz.creditnote'].browse(self._context.get('active_ids', []))
        #for lines in line_invoice.sorted(key=lambda r: (r.partner_id.id, r.number_invoice)):    

        list_invoices_ids = []
        
        ids = [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9]) for r in self.env.cr.fetchall()]
        for partner_id, date_creditnote, product_id, quantity, discount, tax_id, name, commentaire, create_uid, price_unit in ids:
            Name_Discount = name + ' ' + commentaire
        
            inv_obj = self.env['account.invoice']
            ir_property_obj = self.env['ir.property']

            # product
            product_prod  = self.env['product.product'].search([('id', '=', product_id),  ])
            product  = self.env['product.template'].search([('id', '=', product_prod.product_tmpl_id.id),  ])
            # partner
            partner  = self.env['res.partner'].search([('id', '=',partner_id),  ])
            
            account_id = False
            if product_id:
                account_id = product.property_account_income_id.id
            #if not account_id:
            #        inc_acc = ir_property_obj.get('property_account_income_categ_id', 'product.category')
            #        account_id = order.fiscal_position_id.map_account(inc_acc).id if inc_acc else False
            if not account_id:
                    raise UserError(
                         _('There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
                        (product.name,))
            
            amount = price_unit * ((100 - discount) / 100)
            if price_unit <= 0.00:
                    raise UserError(_('The value of the credit note amount must be positive.'))
            context = {'lang': partner.lang}
 
            del context
            taxes = product.taxes_id.filtered(lambda r: not partner.company_id or r.company_id == partner.company_id)
            tax_ids = taxes.ids
            
            invoice = inv_obj.create({
                'name': Name_Discount,
                'origin': _(""),
                'type': 'out_refund',
                'reference': False,
                'account_id': partner.property_account_receivable_id.id,
                'partner_id': partner_id,
                'partner_shipping_id': partner.carrier_id.id,
                'invoice_line_ids': [(0, 0, {
                    'name': name,
                    'origin':  _(""),
                    'account_id': account_id,
                    'price_unit': price_unit,
                    'quantity': 1.0,
                    'discount': 100 - discount,
                    'uom_id': product.uom_id.id,
                    'product_id': product_id,
                    
                    'invoice_line_tax_ids': [(6, 0, tax_ids)],
                    'account_analytic_id':  False,
                })],
                'currency_id': partner.property_product_pricelist.currency_id.id,
                'payment_term_id': partner.property_payment_term_id.id,
                'fiscal_position_id': partner.property_account_position_id.id,
                'team_id': partner.team_id.id,
                'user_id': create_uid,
                'comment': commentaire,
            })
            
            invoice.compute_taxes()
            #invoice.message_post_with_view('mail.message_origin_link',
            #        values={'self': invoice, 'origin': 'create credit note'},
            #        subtype_id=self.env.ref('mail.mt_note').id)
            
            self.env.cr.commit()
            list_invoices_ids.append(int(invoice.id))
            
            
        # Update Creditnote_ok
        query = """UPDATE wiz_creditnote SET creditnote_ok = True where create_uid = """ + str(user_id) + """  AND id in %s
                   """
        #self._cr.execute(query,  (user_id, tuple(self.ids)))
        self._cr.execute(query, tuple(params))
        self.env.cr.commit()
        return list_invoices_ids
    
        #action = self.env.ref('account.action_invoice_tree1').read()[0]
        #if len(list_invoices_ids) >= 1:
            #action  = self.env.ref('account.action_invoice_out_refund').read()[0]
            #action['domain'] = [('id', 'in', invoices_ids),('type','=','out_refund')]    
            #return action
            #view_id = self.env["ir.model.data"].get_object_reference("account", "invoice_tree")
        #    view = self.env.ref('account.invoice_tree')
            
        #    return {'type':'ir.actions.act_window',
        #        'view_mode':'form',
        #        'view_type':'tree,form',
        #        #'views': [(view.id, 'tree')],
        #        #'view_id': view.id,
        #        'view_id': False,
        #        'domain': [('id', 'in', list_invoices_ids),('type','=','out_refund')],  
        #        #"target":"new",
        #        'res_model':'account.invoice' ,               
        #        }
        #else:    
        #    return {'type': 'ir.actions.act_window_close'}
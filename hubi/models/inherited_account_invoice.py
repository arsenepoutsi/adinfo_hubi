# -*- coding: utf-8 -*-
from functools import partial
from odoo import models, fields, api, tools, _, SUPERUSER_ID
from odoo.tools.misc import formatLang
from odoo.exceptions import UserError, AccessError
import base64
   
class HubiAccountInvoice(models.Model):
    _inherit = "account.invoice"


#    @api.one
#    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
#                 'currency_id', 'company_id', 'date_invoice', 'type', 'discount_type', 'discount_rate')
#    def _compute_amount_old(self):
#        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        
#        self.amount_before_discount = self.amount_untaxed
       
#        if self.discount_type == 'percent':
#            self.amount_discount =  self.amount_before_discount * self.discount_rate/100
#        else:
#            rate_d = (self.discount_rate / self.amount_before_discount) * 100
#            self.amount_discount =  self.amount_before_discount * rate_d/100
        
#        self.amount_untaxed =  self.amount_before_discount - self.amount_discount
#        self.amount_tax = sum(line.amount_total for line in self.tax_line_ids)
#        self.amount_total = self.amount_untaxed + self.amount_tax
                  
#        amount_total_company_signed = self.amount_total
#        amount_untaxed_signed = self.amount_untaxed
#        amount_tax_signed = self.amount_tax
#        amount_before_discount_signed = self.amount_before_discount
#        amount_discount_signed = self.amount_discount
        
#        if self.currency_id and self.currency_id != self.company_id.currency_id:
#            currency_id = self.currency_id.with_context(date=self.date_invoice)
#            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
#            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
#            amount_tax_signed= currency_id.compute(self.amount_tax, self.company_id.currency_id)
#            amount_before_discount_signed = currency_id.compute(self.amount_before_discount, self.company_id.currency_id)
#            amount_discount_signed = currency_id.compute(self.amount_discount, self.company_id.currency_id)
            
#        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
#        self.amount_total_company_signed = amount_total_company_signed * sign
#        self.amount_total_signed = self.amount_total * sign
#        self.amount_untaxed_signed = amount_untaxed_signed * sign
#        self.amount_tax_signed = amount_tax_signed * sign
#        self.amount_before_discount_signed = amount_before_discount_signed * sign
#        self.amount_discount_signed = amount_discount_signed * sign



    #@api.one
    #@api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
    #             'currency_id', 'company_id', 'date_invoice', 'type')
    #def compute_amount_tax(self):
    #    amount_tax_signed = self.amount_tax
    #    if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
    #         amount_tax_signed= currency_id.compute(self.amount_tax, self.company_id.currency_id)
            
    #    sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
    #    self.amount_tax_signed = amount_tax_signed * sign
        
    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
                 'currency_id', 'company_id', 'date_invoice', 'type')
    def _compute_amount(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(line.amount_total for line in self.tax_line_ids)
        self.amount_total = self.amount_untaxed + self.amount_tax
        self.amount_discount = sum((line.quantity * line.price_unit * line.discount)/100 for line in self.invoice_line_ids)
        self.amount_before_discount = self.amount_untaxed + self.amount_discount
        
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        amount_tax_signed = self.amount_tax
        amount_discount_signed = self.amount_discount
        amount_before_discount_signed = self.amount_before_discount
        
        if self.currency_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
            amount_tax_signed= currency_id.compute(self.amount_tax, self.company_id.currency_id)
            amount_discount_signed = currency_id.compute(self.amount_discount, self.company_id.currency_id)
            amount_before_discount_signed = currency_id.compute(self.amount_before_discount, self.company_id.currency_id)
            
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign
        self.amount_tax_signed = amount_tax_signed * sign
        self.amount_discount_signed = amount_discount_signed * sign
        self.amount_before_discount_signed = amount_before_discount_signed * sign
        
        
    date_invoice = fields.Date(string='Invoice Date',
        readonly=True, states={'draft': [('readonly', False)]}, index=True,
        help="Keep empty to use the current date", copy=False, 
        default=lambda self: fields.Date.today())
    #shipper_id = fields.Many2one('hubi.shipper', string='Shipper')
    pallet_number = fields.Integer(string = 'Number of pallet')
    comment = fields.Text(string='Comment')
    sending_date = fields.Date(string="Sending Date")   
    packaging_date = fields.Date(string="Packaging Date")  
    carrier_id = fields.Many2one('delivery.carrier',string = 'Carrier') 
    
    amount_tax_signed = fields.Monetary(string='Tax Amount in Company Currency', currency_field='company_currency_id',
        store=True, readonly=True, compute='_compute_amount')

    discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], string='Discount Type',
                                     readonly=True, states={'draft': [('readonly', False)]}, default='percent')
    discount_rate = fields.Float('Discount Amount', digits=(16, 2), readonly=True, states={'draft': [('readonly', False)]})
    amount_discount = fields.Monetary(string='Discount', store=True, readonly=True, compute='_compute_amount',
                                      track_visibility='always')

    amount_before_discount = fields.Monetary(string='Amount before discount',
        store=True, readonly=True, compute='_compute_amount', track_visibility='always')
    amount_before_discount_signed = fields.Monetary(string='Amount before discount in Company Currency', currency_field='company_currency_id',
        store=True, readonly=True, compute='_compute_amount')
    amount_discount_signed = fields.Monetary(string='Amount discount in Company Currency', currency_field='company_currency_id',
        store=True, readonly=True, compute='_compute_amount')



    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id_shipper(self):
        """
        Update the following fields when the partner is changed:
        - Carrier
        """
        if not self.partner_id:
            self.update({
                'carrier_id': False,

            })
            return
    
        values = { 
            'carrier_id' : self.partner_id.carrier_id and self.partner_id.carrier_id.id or False
            }
 
        self.update(values)
        
#    @api.multi
#    def _get_tax_amount_by_group(self):
#        self.ensure_one()
#        currency = self.currency_id or self.company_id.currency_id
#        fmt = partial(formatLang, self.with_context(lang=self.partner_id.lang).env, currency_obj=currency)
#        res = {}
#        for line in self.tax_line_ids:
#            res.setdefault(line.tax_id.tax_group_id, {'base': 0.0, 'amount': 0.0})
#            res[line.tax_id.tax_group_id]['amount'] += line.amount + line.amount_rounding - line.amount_discount
#            res[line.tax_id.tax_group_id]['base'] += line.base - line.base_discount
#        res = sorted(res.items(), key=lambda l: l[0].sequence)
#        res = [(
#            r[0].name, r[1]['amount'], r[1]['base'],
#            fmt(r[1]['amount']), fmt(r[1]['base']),
#        ) for r in res]
#        return res    
    
    @api.onchange('discount_type', 'discount_rate', 'invoice_line_ids')
    def supply_rate(self):
        for inv in self:
            if inv.discount_type == 'percent':
                for line in inv.invoice_line_ids:
                    line.discount = inv.discount_rate
            else:
                total = discount = 0.0
                for line in inv.invoice_line_ids:
                    total += (line.quantity * line.price_unit)
                if inv.discount_rate != 0:
                    discount = (inv.discount_rate / total) * 100
                else:
                    discount = inv.discount_rate
                for line in inv.invoice_line_ids:
                    line.discount = discount

    @api.multi
    def compute_invoice_totals(self, company_currency, invoice_move_lines):
        total = 0
        total_currency = 0
        for line in invoice_move_lines:
            if self.currency_id != company_currency:
                currency = self.currency_id.with_context(date=self.date or self.date_invoice or fields.Date.context_today(self))
                line['currency_id'] = currency.id
                line['amount_currency'] = currency.round(line['price'])
                line['price'] = currency.compute(line['price'], company_currency)
            else:
                line['currency_id'] = False
                line['amount_currency'] = False
                line['price'] = line['price']
            if self.type in ('out_invoice', 'in_refund'):
                total += line['price']
                total_currency += line['amount_currency'] or line['price']
                line['price'] = - line['price']
            else:
                total -= line['price']
                total_currency -= line['amount_currency'] or line['price']
        return total, total_currency, invoice_move_lines

    @api.multi
    def button_dummy(self):
        self.supply_rate()
        return True 
    
    @api.multi
    def invoice_send_email(self):
        #raise UserError(_('Send email.'))
        attachments_ids = []
        Envoi = False
        NbLig = len(self.ids)
        CodePartner=999999
        EMailPartner="z"
        CptLig = 0
        #for ligne in self.sorted(key=lambda r: (r.partner_id.id, r.id)):
        for ligne in self.sorted(key=lambda r: (r.partner_id.email, r.id)):
            CptLig = CptLig + 1
           
            #if ((ligne.partner_id.id != CodePartner) and (CodePartner != 999999)) or (CptLig == NbLig):
            if ((ligne.partner_id.email != EMailPartner) and (EMailPartner != "z")) :
                self.send_email(ligne,EMailPartner,attachments_ids)
                Envoi = False
                attachments_ids = []
                
                #if not ligne.partner_id.email:
                #    raise UserError(_("Cannot send email: partner %s has no email address.") % ligne.partner_id.name)
                #su_id = self.env['res.partner'].browse(SUPERUSER_ID)
                #template_id = self.env['ir.model.data'].get_object_reference('hubi',  'email_template_invoice')[1]
                #template_browse = self.env['mail.template'].browse(template_id)
                #email_to =  ligne.partner_id.email    #self.env['res.partner'].browse(ligne.partner_id).email
                #if template_browse:
                #    values = template_browse.generate_email(ligne.id, fields=None)
                #    values['email_to'] = email_to
                #    values['email_from'] = 'adinfo.be@groupeadinfo.com' #su_id.email
                #    values['res_id'] = ligne.id   #False
                #    if not values['email_to'] and not values['email_from']:
                #        pass
                
                #    values['attachment_ids'] = [(6, 0, attachments_ids)] #attachments_ids
                #    #values['attachment_ids'] = attachments_ids
                                
                #    mail_mail_obj = self.env['mail.mail']
                #    msg_id = mail_mail_obj.create(values)
                #    if msg_id:
                #        mail_mail_obj.send(msg_id)
        
            if ligne.partner_id.email:
                CodePartner = ligne.partner_id.id
                EMailPartner = ligne.partner_id.email
                Envoi = True
 
                #pdf = self.env.ref('account.account_invoices').sudo().render_qweb_pdf([ligne.id])[0]
                pdf = self.env.ref('hubi.account_invoices_hubi').sudo().render_qweb_pdf([ligne.id])[0]
                # attachment
                #attachments_ids = [(0, 0, {'name': 'Invoice'+(ligne.display_name),
                #                                         'type': 'binary', 
                #                                         'res_id':ligne.id,
                #                                         'res_model':'account.invoice',
                #                                         'datas':base64.b64encode(pdf),
                #                                         'mimetype': 'application/x-pdf',
                #                                         'datas_fname': "" +(ligne.display_name)+".pdf",
                #                                         'datas': base64.b64encode(pdf)})]
            
                id_w = self.env['ir.attachment'].create({
                    'name': 'Invoice'+(ligne.display_name)+"_"+str(ligne.id),
                    'type': 'binary', 
                    'res_id':ligne.id,
                    'res_model':'account.invoice',
                    'datas':base64.b64encode(pdf),
                    'mimetype': 'application/x-pdf',
                    'datas_fname':ligne.display_name+'_'+str(ligne.id)+'.pdf'
                    })
                attachments_ids.append(id_w.id)
            
        if (Envoi):
            self.send_email(ligne,EMailPartner,attachments_ids)   
        
        #raise UserError(_("Mail send"))           
        #return True
            #template_obj = self.env['mail.mail']
            #template_data = {
            #    'subject': 'Due Invoice Notification : ' ,
            #    'body_html': 'message_body',
            #    'email_to': partner.partner_id.email,
            #    'email_from': 'adinfo.be@groupeadinfo.com'
            #    }
            #template_id = template_obj.create(template_data)
            #template_obj.send(template_id)
            
            #tools.email_send(email_from='adinfo.be@groupeadinfo.com',
            #                email_to=partner.partner_id.email,
            #                subject='Some subject',
            #                body='Some body',
            #                on_error=None)

             
            
            #template_id = self.env.ref('account.invoice')
            #mail_id = template_id.send_mail(partner.partner_id.id)

            #ir_model_data = self.env['ir.model.data']
            #try:
            #    template_id = ir_model_data.get_object_reference('hubi', 'email_template_accounting_transfer')[1]
            #except ValueError:
            #    template_id = False

            
            #template_id.with_context(lang=user.lang).send_mail(partner.partner_id.id, force_send=True, raise_exception=True)
            #_logger.info("Email sent for partner <%s> to <%s>", partner.partner_id.login, partner.partner_id.email)

            #if partner.template_id and partner.template_id.mail_template_id:
            #    self.template_id.mail_template_id.send_mail(partner.id)
    
        #return True
    
    def send_email(self,ligne,email_to,attachments_ids):    
        
        #if not ligne.partner_id.email:
        #    raise UserError(_("Cannot send email: partner %s has no email address.") % ligne.partner_id.name)
        if email_to:
            su_id = self.env['res.partner'].browse(SUPERUSER_ID)
            template_id = self.env['ir.model.data'].get_object_reference('hubi',  'email_template_invoice')[1]
            template_browse = self.env['mail.template'].browse(template_id)
            #email_to = self.env['res.partner'].browse(ligne.partner_id).email
            
            if template_browse:
                values = template_browse.generate_email(ligne.id, fields=None)
                values['email_to'] = email_to
                values['email_from'] = su_id.email 
                values['res_id'] = ligne.id   #False
                if not values['email_to'] and not values['email_from']:
                    pass
                
                values['attachment_ids'] = [(6, 0, attachments_ids)] #attachments_ids
                #values['attachment_ids'] = attachments_ids
                                
                mail_mail_obj = self.env['mail.mail']
                msg_id = mail_mail_obj.create(values)
                if msg_id:
                    mail_mail_obj.send(msg_id) 
                               
            
class HubiAccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.onchange('category_id', 'caliber_id', 'packaging_id')
    def _onchange_product(self):
        product_domain = [('sale_ok','=',True)]
        
        if self.category_id:
            product_domain = [('categ_id', '=', self.category_id.id)]+ product_domain[0:]
        if self.caliber_id:
            product_domain = [('caliber_id', '=', self.caliber_id.id)] + product_domain[0:]
        if self.packaging_id:
            product_domain = [('packaging_id', '=', self.packaging_id.id)] + product_domain[0:]
            
        if self.category_id  and self.caliber_id  and self.packaging_id:
            # Recherche de l'artcle en fonction des sélections 
            id_prod = 0  
            products_templ = self.env['product.template'].search([
            ('categ_id', '=', self.category_id.id),
            ('caliber_id', '=', self.caliber_id.id),
            ('packaging_id', '=', self.packaging_id.id), ])         
            for prod in products_templ:
                id_prod = prod.id
                
            if id_prod != 0:
                # search the code in product.product
                products_prod_prod = self.env['product.product'].search([
                ('product_tmpl_id', '=', id_prod),  ])         
                for prod_prod in products_prod_prod:
                    id_prod_prod = prod_prod.id
                    
                self.product_id = id_prod_prod    
        
        return {'domain': {'product_id': product_domain}}
    
    @api.one
    @api.depends('quantity', 'price_total', 'product_id')
    def _compute_weight(self):
        """
        Compute the weights of the account invoice lines.
        """
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        #sign = 1
        for line in self:
            factor = line.uom_id.factor * line.product_id.uom_id.factor
            if factor != 0: 
                weight = line.product_id.weight * (line.quantity / factor)
            else:
                weight = line.product_id.weight * line.quantity  
            weight = round(weight,3)
            
            weight_signed = weight * sign
                    
            if weight!=0:
                if line.discount >= 100: 
                    price_weight = (line.price_unit * line.quantity) / weight                       
                else:  
                    price_weight = line.price_subtotal / weight
            else:   
                price_weight = 0
               
            price_weight = round(price_weight ,3)   
            
            line.update({
                'weight': weight,
                'weight_signed': weight_signed,
                'price_weight': price_weight
            })

    @api.one
    @api.depends('price_total')
    def compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price_total_signed = self.price_total
        if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            price_total_signed = self.invoice_id.currency_id.with_context(date=self.invoice_id._get_currency_rate_date()).compute(price_total_signed, self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_total_signed = price_total_signed * sign
    
    category_id = fields.Many2one('product.category', 'Internal Category', domain=[('parent_id','!=',False), ('shell', '=', True)], store=False)
    caliber_id = fields.Many2one('hubi.family', string='Caliber', domain=[('level', '=', 'Caliber')], help="The Caliber of the product.", store=False)
    packaging_id = fields.Many2one('hubi.family', string='Packaging', domain=[('level', '=', 'Packaging')], help="The Packaging of the product.", store=False)
    weight = fields.Float(string='Weight ', store=True, readonly=True, compute='_compute_weight')
    price_weight = fields.Float(string='Price Weight ', store=True, readonly=True, compute='_compute_weight')
    weight_signed = fields.Float(string='Weight Signed', store=True, readonly=True, compute='_compute_weight')
    price_total_signed = fields.Monetary(string='Amount Signed in Company Currency', currency_field='company_currency_id',
        store=True, readonly=True, compute='compute_price')
    comment = fields.Char(string='Comment')


#class AccountInvoiceTax(models.Model):
#    _inherit = "account.invoice.tax"
     
    #@api.depends('invoice_id.discount_type', 'invoice_id.discount_rate', 'invoice_id.invoice_line_ids')
    #def compute_rate_discount(self):
    #    rate_d = 0
    #    for invoice in self.mapped('invoice_id'):
    #        if invoice.discount_type == 'percent':
    #            rate_d = invoice.discount_rate
    #        else:
    #            total = discount = 0.0
    #            for line in invoice.tax_line_ids:
    #                total += (line.base)
    #            if invoice.discount_rate != 0:
    #                rate_d = (invoice.discount_rate / total) * 100
                
        
    #    for tax in self:
    #        tax.base_discount = 0.0
    #        tax.amount_discount = 0.0
    #        if tax.tax_id:
    #           tax.base_discount = tax.base * rate_d/100
    #           tax.amount_discount = tax.base_discount  * tax.tax_id.amount /100           
                


    #amount_discount = fields.Monetary(string="Amount Discount", compute='compute_rate_discount', store=True)
    #base_discount = fields.Monetary(string="Base Discount", compute='compute_rate_discount', store=True)
    
    
    
    #@api.depends('amount', 'amount_rounding')
    #def _compute_amount_total(self):
    #    for tax_line in self:
    #        tax_line.amount_total = tax_line.amount + tax_line.amount_rounding - tax_line.amount_discount

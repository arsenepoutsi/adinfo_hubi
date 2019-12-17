# -*- coding: utf-8 -*-
from odoo import models, fields, api, _,  SUPERUSER_ID
from odoo.exceptions import UserError, AccessError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import time
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import date, timedelta, datetime   
import base64
from ..controllers import ctrl_print

class HubiSaleOrderLine(models.Model):
    _inherit = "sale.order.line"
       
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

            #self.env.cr.execute('SELECT id FROM product_template '
            #            'WHERE categ_id = %s AND caliber_id = %s AND packaging_id = %s  ',
            #            (self.category_id.id, self.caliber_id.id, self.packaging_id.id))
            #res = self.env.cr.fetchone()
            #if res:
            #   id_prod = res[0]
                
            if id_prod != 0:
                # search the code in product.product
                products_prod_prod = self.env['product.product'].search([
                ('product_tmpl_id', '=', id_prod),  ])         
                for prod_prod in products_prod_prod:
                    id_prod_prod = prod_prod.id
                    
                self.product_id = id_prod_prod    
        
        return {'domain': {'product_id': product_domain}}

    @api.depends('product_uom_qty', 'price_total', 'product_id', 'order_id')
    def _compute_weight(self):
        """
        Compute the weights of the Sale Order lines.
        """
        for line in self:
            factor = line.product_uom.factor * line.product_id.uom_id.factor
            if factor != 0: 
                weight = line.product_id.weight * (line.product_uom_qty / factor)
            else:
                weight = line.product_id.weight * line.product_uom_qty  
            weight = round(weight,3)
                     
            if weight!=0:
                if line.discount >= 100: 
                    price_weight = (line.price_unit * line.product_uom_qty) / weight                          
                else:  
                    price_weight = line.price_subtotal / weight
            else:   
                price_weight = 0
               
            price_weight = round(price_weight ,3)   
            
            line.update({
                'weight': weight,
                'price_weight': price_weight
                
            })
            

    @api.depends('order_id', 'product_id', 'order_id.packaging_date', 'order_partner_id')
    def _compute_dluo(self):
        for line in self:
            if line.order_id.packaging_date and line.product_id.id:
                if line.order_partner_id.dlc_number_day and line.order_partner_id.dlc_number_day>0:
                    val_nb_day=line.order_partner_id.dlc_number_day
                else:    
                    val_nb_day=line.product_id.categ_id.nb_day_dluo or 7
                val_calcul_dluo = fields.Date.from_string(line.order_id.packaging_date) + timedelta(days=val_nb_day)
                
                line.update({
                'date_dluo': val_calcul_dluo
                })

    
    @api.onchange('product_id')
    def product_change(self):
        if self.product_id.id:
            super(HubiSaleOrderLine, self).product_uom_change()
            
            # Batch number
            if not self.no_lot:
                _nolot = ''
                if self.order_id.sending_date:
                    val_calcul_lot = self.order_id.calcul_lot 
                    dateAAAAMMJJ=fields.Date.from_string(self.sending_date).strftime('%Y%m%d')
                    dateQQQ=fields.Date.from_string(self.sending_date).strftime('%Y%j')
        
                    if val_calcul_lot=='AQ': 
                        _nolot = dateQQQ
                    else:
                        if val_calcul_lot=='AMJ': 
                            _nolot = dateAAAAMMJJ

                self.no_lot = _nolot
              
            if self.price_unit == 0:
                #raise UserError(_('Error in the price. The value is 0.'))
                title = ("Warning for %s") % self.product_id.name
                message = 'Error in the price. The value is 0.'
                warning = {
                    'title': title,
                    'message': message, }
                return {'warning': warning}
    
            
    category_id = fields.Many2one('product.category', 'Internal Category', domain=[('parent_id','!=',False), ('shell', '=', True)], store=False)
    caliber_id = fields.Many2one('hubi.family', string='Caliber', domain=[('level', '=', 'Caliber')], help="The Caliber of the product.", store=False)
    packaging_id = fields.Many2one('hubi.family', string='Packaging', domain=[('level', '=', 'Packaging')], help="The Packaging of the product.", store=False)
    weight = fields.Float(string='Weight ', store=True, readonly=True, compute='_compute_weight')
    price_weight = fields.Float(string='Price Weight ', store=True, readonly=True, compute='_compute_weight')
    comment = fields.Char(string='Comment')
    no_lot = fields.Char(string='Batch number')
    partner_id = fields.Many2one("res.partner", string='Customer')
    done_packing = fields.Boolean(string='Packing Done')
    sending_date = fields.Date(string="Sending Date", store=False, compute='_compute_date_sending' )
    date_dluo = fields.Date(string="DLUO Date",store=True, compute='_compute_dluo')   
    etiquette_product = fields.Boolean(string="Product label", related='product_id.etiquette')
   
    #@api.multi
    def invoice_line_create(self, invoice_id, qty):
        #invoice_line_vals = super(HubiSaleOrder, self)._prepare_invoice_line(qty=qty)
        invoice_line_vals = super(HubiSaleOrderLine, self).invoice_line_create(invoice_id, qty)
        invoice_line_vals.update({
            'comment': self.comment,
            #'no_lot': self.no_lot
        })
        return invoice_line_vals  
    
    #@api.multi
    def print_label(self):
        #self.filtered(lambda s: s.state == 'draft').write({'state': 'sent'})
        #return self.env.ref('hubi.report_orderline_label').report_action(self)
        ##return {'type': 'ir.actions.report','report_name': 'report_saleorder_hubi_document','report_type':"qweb-pdf"}
        sale_order_ids = self.env['wiz_sale_order_print_label'].browse(self.id)
        res = sale_order_ids.load_order_line('order_line')
        
        if len(res) >= 1:
            action = self.env.ref('hubi.action_wiz_sale_order_print_label_tree').read()[0]
            action['domain'] = [('id', 'in', res)]
            
        return action
    
    #@api.multi
    def validation(self, fields):
        #Lorsque l'on appuie sur le bouton, la ligne n'est plus affichée sur la page
        self.update({
                'done_packing': True,
                #'packaging_date':fields.Date.context_today(self),

            })
        return
 
    #@api.multi
    def _compute_date_sending(self):
        for line in self:
            #line.sending_date = line.order_id.sending_date
            line.update({
                'sending_date': line.order_id.sending_date,
                
            })
               
class HubiSaleOrder(models.Model):
    _inherit = "sale.order"

    #@api.multi
    def action_search_products(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        product_count = 0
        sale_order_id = self.id
        #create  products depending on the pricelist
        query_args = {'pricelist_code': self.pricelist_id.id,'date_order' : self.date_order,'id_order' : self.id}
        
        self._cr.execute("DELETE FROM wiz_search_product_line WHERE order_line_id=%s AND pricelist_line_id=%s", (self.id,self.pricelist_id.id,))
        
        prod_prec = ''
        query = """Select product_product.id, date_start, date_end, product_category.complete_name, hubi_family.name, 
                    case compute_price when 'fixed' then fixed_price else list_price*(1-percent_price/100) end as Price,
                    case when  date_start is null then '01/01/1900' ELSE date_start END as date_debut, min_quantity 
                    from product_pricelist_item
                    inner join product_template on product_pricelist_item.product_tmpl_id=product_template.id
                    inner join product_product on product_product.product_tmpl_id=product_template.id
                    inner join product_category on product_template.categ_id = product_category.id
                    inner join hubi_family on product_template.caliber_id = hubi_family.id
                    where (pricelist_id= %(pricelist_code)s ) and (product_pricelist_item.product_tmpl_id is not null) 
                    and (date_start<=%(date_order)s  or date_start is null)
                    and (date_end>=%(date_order)s  or date_start is null)
                    AND (product_product.id NOT IN (SELECT product_id FROM sale_order_line WHERE order_id=%(id_order)s))
                    order by product_product.id, date_debut desc, min_quantity """

        self.env.cr.execute(query, query_args)
        ids = [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]) for r in self.env.cr.fetchall()]
            
        for product, date_start, date_end, category, caliber, unit_price, date_debut, qty in ids:
            if product != prod_prec:
                price_vals = {
                    'order_line_id': sale_order_id,
                    'pricelist_line_id':self.pricelist_id.id,
                    'product_id': product,
                    'qty_invoiced':'0',
                    'price_unit':unit_price,
                    'date_start': date_start,
                    'date_end': date_end, 
                    'category_id': category,
                    'caliber_id': caliber,               
                    }

                price = self.env['wiz.search.product.line'].create(price_vals)
                product_count = product_count + 1
                prod_prec = product

        self.env.cr.commit()
        message_lib = ("%s %s %s %s ") % ("Create Product for price list = (",self.pricelist_id.id, ") ", self.pricelist_id.name)
        
        #This function opens a window to create  products depending on the pricelist
        try:
            search_product_form_id = ir_model_data.get_object_reference('hubi', 'Price_List_Lines_form_view')[1]
            
        except ValueError:
            search_product_form_id = False
            
        try:
            search_view_id = ir_model_data.get_object_reference('hubi', 'Price_List_Lines_search')[1]
            
        except ValueError:
            search_view_id = False
          
        ctx = {
            #'group_by':['category_id','caliber_id'],
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            'default_order_line_id':self.id,
            'default_pricelist_line_id':self.pricelist_id.id
            ,'default_message':message_lib
            
        }
        dom = [
            ('order_line_id', '=', sale_order_id),
            ('pricelist_line_id', '=', self.pricelist_id.id)
        ]   
         
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'wiz.search.product.line',
            'views': [(search_product_form_id, 'tree')],
            'view_id': search_product_form_id,
            'search_view_id': search_view_id,
            #'target': 'inline',
            'target': 'new',
            'context': ctx,
            'domain':dom,
        }
    
     
    #@api.multi
    def action_print_label(self):
        sale_order_ids = self.env['wiz_sale_order_print_label'].browse(self._ids)
        res = sale_order_ids.load_order_line('order')
        
        if len(res) >= 1:
            action = self.env.ref('hubi.action_wiz_sale_order_print_label_tree').read()[0]
            action['domain'] = [('id', 'in', res)]
         
        return action  

    #@api.one
    @api.depends('company_id')
    def _calcul_lot(self):
        val_calcul_lot = 'M'
        settings = self.env['hubi.general_settings'].search([('name','=', 'General Settings'), ('company_id','=', self.company_id.id)])
        for settings_vals in settings:
            if settings_vals.calcul_lot:
                val_calcul_lot = settings_vals.calcul_lot
        self.calcul_lot = val_calcul_lot
        

    #shipper_id = fields.Many2one('hubi.shipper', string='Shipper')
    pallet_number = fields.Integer(string = 'Number of pallet')
    comment = fields.Text(string='Comment')
    #order_reference = fields.Char(string='Order Reference')
    sending_date = fields.Date(string="Sending Date", default=lambda self: fields.Date.today())   
    packaging_date = fields.Date(string="Packaging Date", default=lambda self: fields.Date.today())   
    calcul_lot = fields.Text(string="Batch Number Calculation", store=False, compute='_calcul_lot')
    periodicity_invoice = fields.Selection(string="Invoice Period", related='partner_id.periodicity_invoice')#,store=True)
    invoice_grouping = fields.Boolean(string="Invoice grouping", related='partner_id.invoice_grouping')#,store=True)



    #@api.multi
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

        #if self.partner_id.shipper_id:
        #    values['shipper_id'] = self.partner_id.shipper_id and self.partner_id.shipper_id.id or False
        self.update(values)
        
    #@api.multi
    def action_invoice_create(self, grouped=False, final=False, dateInvoice=False):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        inv_obj = self.env['account.invoice']
        inv_lines = self.env['account.invoice.line']
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        invoices = {}
        references = {}
        account_divers  = self.env['product.category'].search([('reference', 'in', ['D', 'd', 'DIVERS','Divers','divers',''] )], limit=1 ) 
        
        if not dateInvoice:
            date_invoices = time.strftime('%Y-%m-%d')
        else:
            date_invoices = dateInvoice 
               
        date_due = False
        
        for order in self.sorted(key=lambda r: (r.partner_id.id, r.id)):
            inv_group = grouped
            
            #partners = self.env['res.partner'].search([('id','=',order.partner_id.id)])
            #for partner in partners:
            #    inv_group = partner.invoice_grouping
            
            if order.partner_id.invoice_grouping:
               inv_group = False
            else:
               inv_group = True
                   
            group_key = order.id if inv_group else (order.partner_invoice_id.id, order.currency_id.id)
        
            for line in order.order_line.sorted(key=lambda l: l.qty_to_invoice < 0):
                if float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    continue
                create_ent_bl = False
                if group_key not in invoices:
                    inv_data = order._prepare_invoice()
                    invoice = inv_obj.create(inv_data)
                    references[invoice] = order
                    invoices[group_key] = invoice
                    
                    create_ent_bl = True
                    
                elif group_key in invoices:
                    vals = {}
                    if order.name not in invoices[group_key].origin.split(', '):
                        vals['origin'] = invoices[group_key].origin + ', ' + order.name
                        create_ent_bl = True
                    if order.client_order_ref and order.client_order_ref not in invoices[group_key].name.split(', ') and order.client_order_ref != invoices[group_key].name:
                        vals['name'] = invoices[group_key].name + ', ' + order.client_order_ref
                    invoices[group_key].write(vals)
                    
                if create_ent_bl:
                    #month = order.date_order.month 
                    #year = order.date_order.year
                    #day = order.date_order.day
                    #dateorder=datetime.strptime(order.date_order, '%d-%m-%Y')
                    dateorder=fields.Date.from_string(order.date_order).strftime('%d/%m/%Y')
                    res = {
                        'name': 'BL no ' + order.name + ' du ' + dateorder,
                        'sequence':0,
                        'origin': order.name,
                        'price_unit': 0,
                        'quantity': 0,
                        'product_id':  False,
                        'layout_category_id':  False,
                        'account_id':  account_divers.property_account_income_categ_id.id or 630,
                    }
                    #
                    res.update({'invoice_id': invoices[group_key].id })
                    inv_lines |= self.env['account.invoice.line'].create(res)   
                    
                if line.qty_to_invoice > 0:
                    line.invoice_line_create(invoices[group_key].id, line.qty_to_invoice)
                elif line.qty_to_invoice < 0 and final:
                    line.invoice_line_create(invoices[group_key].id, line.qty_to_invoice)

            if references.get(invoices.get(group_key)):
                if order not in references[invoices[group_key]]:
                    references[invoice] = references[invoice] | order

        if not invoices:
            raise UserError(_('There is no invoiceable line.'))

        for invoice in invoices.values():
            if not invoice.invoice_line_ids:
                raise UserError(_('There is no invoiceable line.'))
            
            if date_invoices:
                invoice.date_invoice = date_invoices
                
                if invoice.payment_term_id:
                    pterm = invoice.payment_term_id
                    pterm_list = pterm.with_context(currency_id=invoice.company_id.currency_id.id).compute(value=1, date_ref=date_invoices)[0]
                    date_due = max(line[0] for line in pterm_list)
                elif invoice.date_due and (date_invoices > invoice.date_due):
                    date_due = date_invoice
                
                if date_due and not invoice.date_due:
                    invoice.date_due = date_due
            
            # If invoice is negative, do a refund invoice instead
            if invoice.amount_untaxed < 0:
                invoice.type = 'out_refund'
                for line in invoice.invoice_line_ids:
                    line.quantity = -line.quantity
            # Use additional field helper function (for account extensions)
            for line in invoice.invoice_line_ids:
                line._set_additional_fields(invoice)
            # Necessary to force computation of taxes. In account_invoice, they are triggered
            # by onchanges, which are not triggered when doing a create.
            invoice.compute_taxes()
            invoice.message_post_with_view('mail.message_origin_link',
                values={'self': invoice, 'origin': references[invoice]},
                subtype_id=self.env.ref('mail.mt_note').id)
        return [inv.id for inv in invoices.values()]  

    #@api.multi
    def _prepare_invoice(self,):
        invoice_vals = super(HubiSaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'discount_type': 'percent',
            'discount_rate': self.partner_id.discount_invoice
        })
        return invoice_vals     
     
    #@api.multi
    def print_quotation(self):
        self.filtered(lambda s: s.state == 'draft').write({'state': 'sent'})
        return self.env.ref('hubi.action_report_saleorder_hubi').report_action(self)
    
    #@api.multi
    def action2_palletization2(self):
        action = self.env.ref('hubi.action_hubi_palletization').read()[0]
        action['views'] = [(self.env.ref('hubi.hubi_palletization_form').id, 'form')]
        action['res_id'] = self.id

        return action
        #return {'type': 'ir.actions.act_window_close'} 
        
    #@api.multi
    def check_limit(self):
        self.ensure_one()
        partner = self.partner_id
        moveline_obj = self.env['account.move.line']
        movelines = moveline_obj.search(
            [('partner_id', '=', partner.id),
             ('account_id.user_type_id.name', 'in', ['Receivable', 'Payable']),
             ('full_reconcile_id', '=', False)]
        )
        debit, credit = 0.0, 0.0
        today_dt = datetime.strftime(datetime.now().date(), DF)
        for line in movelines:
            if line.date_maturity < today_dt:
                credit += line.debit
                debit += line.credit

        if (credit - debit + self.amount_total) > partner.credit_limit:
            if not partner.over_credit:
                msg = 'Can not confirm Sale Order,Total mature due Amount ' \
                      '%s as on %s !\nCheck Partner Accounts or Credit ' \
                      'Limits !' % (credit - debit, today_dt)
                raise UserError(_('Credit Over Limits !\n' + msg))
            partner.write({'credit_limit': credit - debit + self.amount_total})
        return True

    #@api.multi
    def action_confirm(self):
        res = super(HubiSaleOrder, self).action_confirm()
        for order in self:
            order.check_limit()
        return res        
    
    #@api.multi
    def sale_order_send_email(self):
        #raise UserError(_('Send email.'))
        attachments_ids = []
        Envoi = False
        NbLig = len(self.ids)
        CodePartner=999999
        EMailPartner="z"
        CptLig = 0
        for ligne in self.sorted(key=lambda r: (r.partner_id.email, r.id)):
            CptLig = CptLig + 1
           
            if ((ligne.partner_id.email != EMailPartner) and (EMailPartner != "z")) :
                self.send_email(ligne,EMailPartner,attachments_ids)
                Envoi = False
                attachments_ids = []
                
            if ligne.partner_id.email:
                CodePartner = ligne.partner_id.id
                EMailPartner = ligne.partner_id.email
                Envoi = True
 
                #pdf = self.env.ref('sale.action_report_saleorder').sudo().render_qweb_pdf([ligne.id])[0]
                pdf = self.env.ref('hubi.action_report_saleorder_hubi').sudo().render_qweb_pdf([ligne.id])[0]
                # attachment
            
                id_w = self.env['ir.attachment'].create({
                    'name': 'Sale order'+(ligne.display_name)+"_"+str(ligne.id),
                    'type': 'binary', 
                    'res_id':ligne.id,
                    'res_model':'sale.order',
                    'datas':base64.b64encode(pdf),
                    'mimetype': 'application/x-pdf',
                    'datas_fname':ligne.display_name+'_'+str(ligne.id)+'.pdf'
                    })
                attachments_ids.append(id_w.id)
            
        if (Envoi):
            self.send_email(ligne,EMailPartner,attachments_ids)  
            #raise UserError(_('Email send.')) 
        
         #return True
    
    def send_email(self,ligne,email_to,attachments_ids):    
        
        #if not ligne.partner_id.email:
        #    raise UserError(_("Cannot send email: partner %s has no email address.") % ligne.partner_id.name)
        if email_to:
            current_uid = self._context.get('uid')
            su_id_current = self.env['res.partner'].browse(current_uid)
            
            su_id = self.env['res.partner'].browse(SUPERUSER_ID)
            template_id = self.env['ir.model.data'].get_object_reference('hubi',  'email_template_sale_order')[1]
            template_browse = self.env['mail.template'].browse(template_id)
            #email_to = self.env['res.partner'].browse(ligne.partner_id).email
            
            if template_browse:
                values = template_browse.generate_email(ligne.id, fields=None)
                values['email_to'] = email_to
                values['email_from'] = su_id_current.email 
                #values['email_from'] = su_id.email
                values['res_id'] = ligne.id   #False
                if not values['email_to'] and not values['email_from']:
                    pass
                
                values['attachment_ids'] = [(6, 0, attachments_ids)] #attachments_ids
                                
                mail_mail_obj = self.env['mail.mail']
                msg_id = mail_mail_obj.create(values)
                if msg_id:
                    mail_mail_obj.send(msg_id) 
    
    #@api.multi
    def update_sale_batch_number(self):
        if self.sending_date:
            _nolot =''
            self.env.cr.commit()
            val_calcul_lot = 'M'
            
            settings = self.env['hubi.general_settings'].search([('name','=', 'General Settings'), ('company_id','=', self.company_id.id)])
            for settings_vals in settings:
                if settings_vals.calcul_lot:
                    val_calcul_lot = settings_vals.calcul_lot

            dateAAAAMMJJ=fields.Date.from_string(self.sending_date).strftime('%Y%m%d')
            dateQQQ=fields.Date.from_string(self.sending_date).strftime('%Y%j')
        
            if val_calcul_lot=='AQ': 
                _nolot = dateQQQ
            else:
                if val_calcul_lot=='AMJ': 
                    _nolot = dateAAAAMMJJ
            
            if _nolot !='':
                order_lines = self.env['sale.order.line'].search([('order_id', '=', self.id)])
                for line in order_lines:
                    line.write({'no_lot':_nolot})
        
        return {'type': 'ir.actions.act_window_close'}
    
 
    @api.onchange('sending_date')
    def onchange_sending_date(self):
        if self.calcul_lot != 'M':
            self.update_sale_batch_number()
            

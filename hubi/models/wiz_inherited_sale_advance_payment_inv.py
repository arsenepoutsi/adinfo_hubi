# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, timedelta, datetime
import time
import calendar
from dateutil.relativedelta import relativedelta


class HubiSaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
       
    date_invoice = fields.Date(string="Invoice Date", default=lambda self: fields.Date.today())   
     
            
    @api.multi
    def create_invoices(self):
        context = dict(self.env.context)
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))

        if self.advance_payment_method == 'delivered':
            sale_orders.action_invoice_create(dateInvoice=self.date_invoice)
        elif self.advance_payment_method == 'all':
            sale_orders.action_invoice_create(final=True, dateInvoice=self.date_invoice)
        else:
            res = super(HubiSaleAdvancePaymentInv, self.with_context(context)).create_invoices()
            
        self.env.cr.commit()
 
        if not self.date_invoice:
            date_invoice = time.strftime('%Y-%m-%d')
        else:
            date_invoice = self.date_invoice 
              
        date_due = False
       
        for order in sale_orders:
            # Search the invoice
            invoices=self.env['account.invoice'].search([('origin','=', order.name)])
            for invoice in invoices:
                if date_invoice:
                    invoice.write({'date_invoice':date_invoice})
                
                    #invoice.write({'date_invoice':date_invoice})
                    if invoice.payment_term_id:
                        pterm = invoice.payment_term_id
                        pterm_list = pterm.with_context(currency_id=invoice.company_id.currency_id.id).compute(value=1, date_ref=date_invoice)[0]
                        date_due = max(line[0] for line in pterm_list)
                    elif invoice.date_due and (date_invoice > invoice.date_due):
                            date_due = date_invoice
                
                if date_due and not invoice.date_due:
                    invoice.write({'date_due':date_due})
                
                if order.sending_date and not invoice.sending_date:    
                   invoice.write({'sending_date':order.sending_date}) 
                   
                if order.packaging_date and not invoice.packaging_date:    
                   invoice.write({'packaging_date':order.packaging_date}) 

                if order.pallet_number and not invoice.pallet_number:    
                   invoice.write({'pallet_number':order.pallet_number})

                if order.comment and not invoice.comment:    
                   invoice.write({'comment':order.comment})                                                                     
                    
                if order.carrier_id.id and not invoice.carrier_id:    
                   invoice.write({'carrier_id':order.carrier_id.id})
                   
         
        if self._context.get('open_invoices', False):
            return sale_orders.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}        
        #return res
        
class Wizard_create_invoice_period(models.TransientModel):
    _name = "wiz.invoiceperiod"
    _description = "Wizard creation of invoice from period"
    
    def add_months(sourcedate,months):
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month // 12
        month = month % 12 + 1
        day = min(sourcedate.day,calendar.monthrange(year,month)[1])
        return datetime.date(year,month,day)


    @api.model
    def _default_start(self):
        return fields.Date.context_today(self)

    @api.model
    def _default_finish(self):
        finish = datetime.today() + timedelta(days=7)
        return fields.Date.context_today(self, timestamp=finish)
    
    @api.model
    @api.onchange('periodicity_invoice')
    def onchange_periodicity_invoice(self):
        finish = datetime.today()
        
        if self.periodicity_invoice == "Weekly":
            finish = datetime.today() + timedelta(days=-7)
        if self.periodicity_invoice == "Decade":
            finish = datetime.today() + timedelta(days=-10)
        if self.periodicity_invoice == "Fortnight":
            finish = datetime.today() + timedelta(days=-14)
        if self.periodicity_invoice == "Monthly":
            #start_date = datetime.today()
            #days_in_month = calendar.monthrange(start_date.year, start_date.month)[1]
            #finish = start_date + timedelta(days=-days_in_month)
            finish = datetime.today()+ relativedelta(months=-1) 
        
        self.date_start = finish
    
    
    periodicity_invoice = fields.Selection([("Daily", "Daily"),("Weekly", "Weekly"),("Decade", "Decade"),
                    ("Fortnight", "Fortnight"),("Monthly", "Monthly")], string="Invoice Period", default='Daily')
    #date_start = fields.Date('Start Date', help="Starting date for the creation of invoices",default=_default_finish)
    date_start = fields.Date('Start Date', help="Starting date for the creation of invoices",default=lambda self: fields.Date.today())
    date_end = fields.Date('End Date', help="Ending valid for the the creation of invoices", default=lambda self: fields.Date.today())
    date_invoice = fields.Date(string="Invoice Date", default=lambda self: fields.Date.today()) 
    sale_order_ids = fields.Many2many("sale.order")
    message = fields.Text(string="Information")
   
    @api.multi
    def create_invoice_period(self):  
        date_fin = datetime.strptime(self.date_end, "%Y-%m-%d")  + timedelta(hours=25) + timedelta(minutes=59) + timedelta(seconds=59)
        query_args = {'periodicity_invoice': self.periodicity_invoice,'date_start' : self.date_start,'date_end' : date_fin}
        query = """ SELECT  sale_order.id 
                        FROM sale_order 
                        INNER JOIN res_partner on res_partner.id = sale_order.partner_id 
                        WHERE invoice_status = 'to invoice' 
                        AND date_order between %(date_start)s AND %(date_end)s
                        AND periodicity_invoice=%(periodicity_invoice)s """

        self.env.cr.execute(query, query_args)
        ids = [r[0] for r in self.env.cr.fetchall()]
        sale_orders = self.env['sale.order'].search([('id', 'in', ids)])
        
        sale_orders.action_invoice_create(dateInvoice=self.date_invoice)
        
        for order in sale_orders:
            # Search the invoice
            invoices=self.env['account.invoice'].search([('origin','=', order.name)])
            for invoice in invoices:
                if order.sending_date and not invoice.sending_date:    
                   invoice.write({'sending_date':order.sending_date}) 
                   
                if order.packaging_date and not invoice.packaging_date:    
                   invoice.write({'packaging_date':order.packaging_date}) 

                if order.pallet_number and not invoice.pallet_number:    
                   invoice.write({'pallet_number':order.pallet_number})

                if order.comment and not invoice.comment:    
                   invoice.write({'comment':order.comment})                                                                     
                    
                if order.carrier_id.id and not invoice.carrier_id:    
                   invoice.write({'carrier_id':order.carrier_id.id})
        
        #return {'type': 'ir.actions.act_window_close'} 
        return sale_orders.action_view_invoice()      
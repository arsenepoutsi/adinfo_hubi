# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import fields, models, api

class HubiSaleReportCarrier(models.Model):
    _name = "sale.report.carrier"
    _description = "Sales Orders Statistics Carrier"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    name = fields.Char('Order Reference', readonly=True)
    date = fields.Datetime('Date Order', readonly=True)
    confirmation_date = fields.Datetime('Confirmation Date', readonly=True)
    #product_id = fields.Many2one('product.product', 'Product', readonly=True)
    #product_uom = fields.Many2one('product.uom', 'Unit of Measure', readonly=True)
    product_uom_qty = fields.Float('Qty Ordered', readonly=True)
    qty_delivered = fields.Float('Qty Delivered', readonly=True)
    qty_to_invoice = fields.Float('Qty To Invoice', readonly=True)
    qty_invoiced = fields.Float('Qty Invoiced', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Partner', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    user_id = fields.Many2one('res.users', 'Salesperson', readonly=True)
    price_total = fields.Float('Total', readonly=True)
    price_subtotal = fields.Float('Untaxed Total', readonly=True)
    amt_to_invoice = fields.Float('Amount To Invoice', readonly=True)
    amt_invoiced = fields.Float('Amount Invoiced', readonly=True)
    #product_tmpl_id = fields.Many2one('product.template', 'Product Template', readonly=True)
    #categ_id = fields.Many2one('product.category', 'Product Category', readonly=True)
    nbr = fields.Integer('# of Lines', readonly=True)
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist', readonly=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', readonly=True)
    team_id = fields.Many2one('crm.team', 'Sales Channel', readonly=True, oldname='section_id')
    country_id = fields.Many2one('res.country', 'Partner Country', readonly=True)
    commercial_partner_id = fields.Many2one('res.partner', 'Commercial Entity', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Sales Done'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True)
    weight = fields.Float('Gross Weight', readonly=True)
    volume = fields.Float('Volume', readonly=True)
    
    carrier_name = fields.Char('Carrier Name', readonly=True)
    sending_date = fields.Date('Sending Date', readonly=True)
    invoice_status = fields.Selection([
        ('upselling', 'Upselling Opportunity'),
        ('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('no', 'Nothing to Invoice')
        ], string='Invoice Status', readonly=True)
    price_weight = fields.Float(string='Price Weight', group_operator='avg', readonly=True)
    pallet_number = fields.Integer(string = 'Number of pallet')

    stat_partner_1 = fields.Char('statistics partner 1', readonly=True)
    stat_partner_2 = fields.Char('statistics partner 2', readonly=True)
    stat_partner_3 = fields.Char('statistics partner 3', readonly=True)
    stat_partner_4 = fields.Char('statistics partner 4', readonly=True)
    stat_partner_5 = fields.Char('statistics partner 5', readonly=True)

    def _selectC(self):
        select_str = """
            WITH currency_rate as (%s)
             SELECT min(l.id) as id,
                    sum(l.product_uom_qty / u.factor * u2.factor) as product_uom_qty,
                    sum(l.qty_delivered / u.factor * u2.factor) as qty_delivered,
                    sum(l.qty_invoiced / u.factor * u2.factor) as qty_invoiced,
                    sum(l.qty_to_invoice / u.factor * u2.factor) as qty_to_invoice,
                    sum(l.price_total / COALESCE(cr.rate, 1.0)) as price_total,
                    sum(l.price_subtotal / COALESCE(cr.rate, 1.0)) as price_subtotal,
                    sum(l.amt_to_invoice / COALESCE(cr.rate, 1.0)) as amt_to_invoice,
                    sum(l.amt_invoiced / COALESCE(cr.rate, 1.0)) as amt_invoiced,
                    sum(s.pallet_number) as pallet_number,
                    count(*) as nbr,
                    s.name as name,
                    to_char(s.date_order, 'DD/MM/YYYY') as date,
                    to_char(s.confirmation_date, 'DD/MM/YYYY') as confirmation_date,
                    s.state as state,
                    s.partner_id as partner_id,
                    s.user_id as user_id,
                    s.company_id as company_id,
                    extract(epoch from avg(date_trunc('day',s.date_order)-date_trunc('day',s.create_date)))/(24*60*60)::decimal(16,2) as delay,
                    
                    s.pricelist_id as pricelist_id,
                    s.analytic_account_id as analytic_account_id,
                    s.team_id as team_id,
                    
                    partner.country_id as country_id,
                    partner.commercial_partner_id as commercial_partner_id,
                    sum(p.weight * l.product_uom_qty / u.factor * u2.factor) as weight,
                    sum(p.volume * l.product_uom_qty / u.factor * u2.factor) as volume
                    ,CASE WHEN dc.name IS NULL THEN ' '::character varying  ELSE dc.name END AS carrier_name,
                    s.sending_date as sending_date,
                    s.invoice_status as invoice_status, 
                    avg(l.price_weight) as price_weight
                    
                    , partner.statistics_alpha_1 as stat_partner_1,
                    partner.statistics_alpha_2 as stat_partner_2, partner.statistics_alpha_3 as stat_partner_3,
                    partner.statistics_alpha_4 as stat_partner_4, partner.statistics_alpha_5 as stat_partner_5

        """ % self.env['res.currency']._select_companies_rates()
        return select_str

    def _fromC(self):
        from_str = """
                sale_order_line l
                      join sale_order s on (l.order_id=s.id)
                      join res_partner partner on s.partner_id = partner.id
                        left join product_product p on (l.product_id=p.id)
                            left join product_template t on (p.product_tmpl_id=t.id)
                    left join product_uom u on (u.id=l.product_uom)
                    left join product_uom u2 on (u2.id=t.uom_id)
                    left join product_pricelist pp on (s.pricelist_id = pp.id)
                    left join currency_rate cr on (cr.currency_id = pp.currency_id and
                        cr.company_id = s.company_id and
                        cr.date_start <= coalesce(s.date_order, now()) and
                        (cr.date_end is null or cr.date_end > coalesce(s.date_order, now())))
                    left join delivery_carrier dc on (s.carrier_id = dc.id)    
        """
        return from_str

    def _group_byC(self):
        group_by_str = """
            GROUP BY
                    s.name,
                    to_char(s.date_order, 'DD/MM/YYYY'),
                    to_char(s.confirmation_date, 'DD/MM/YYYY'),
                    s.partner_id,
                    s.user_id,
                    s.state,
                    s.company_id,
                    s.pricelist_id,
                    s.analytic_account_id,
                    s.team_id,
                    
                    partner.country_id,
                    partner.commercial_partner_id
                    , dc.name, s.sending_date,
                    s.invoice_status 
                    
                    ,partner.statistics_alpha_1, 
                    partner.statistics_alpha_2, partner.statistics_alpha_3, 
                    partner.statistics_alpha_4, partner.statistics_alpha_5
        """
        return group_by_str

    @api.model_cr
    def init(self):
        # self._table = sale_report_carrier
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s
            )""" % (self._table, self._selectC(), self._fromC(), self._group_byC()))


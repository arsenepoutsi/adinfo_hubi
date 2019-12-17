# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api


class AccountInvoiceReport(models.Model):
    _name = "hubi.invoice.statistic.report"
    _description = "Invoices Statistics"
    _auto = False
    _rec_name = 'date'

    @api.multi
    @api.depends('currency_id', 'date', 'price_total', 'price_average', 'residual')
    def _compute_amounts_in_user_currency(self):
        """Compute the amounts in the currency of the user
        """
        context = dict(self._context or {})
        user_currency_id = self.env.user.company_id.currency_id
        currency_rate_id = self.env['res.currency.rate'].search([
            ('rate', '=', 1),
            '|', ('company_id', '=', self.env.user.company_id.id), ('company_id', '=', False)], limit=1)
        base_currency_id = currency_rate_id.currency_id
        ctx = context.copy()
        for record in self:
            ctx['date'] = record.date
            record.user_currency_price_total = base_currency_id.with_context(ctx).compute(record.price_total, user_currency_id)
            record.user_currency_price_average = base_currency_id.with_context(ctx).compute(record.price_average, user_currency_id)
            record.user_currency_residual = base_currency_id.with_context(ctx).compute(record.residual, user_currency_id)

    date = fields.Date(readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    product_qty = fields.Float(string='Product Quantity', readonly=True)
    uom_name = fields.Char(string='Reference Unit of Measure', readonly=True)
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms', oldname='payment_term', readonly=True)
    fiscal_position_id = fields.Many2one('account.fiscal.position', oldname='fiscal_position', string='Fiscal Position', readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True)
    categ_id = fields.Many2one('product.category', string='Product Category', readonly=True)
    journal_id = fields.Many2one('account.journal', string='Journal', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    commercial_partner_id = fields.Many2one('res.partner', string='Partner Company', help="Commercial Entity")
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    user_id = fields.Many2one('res.users', string='Salesperson', readonly=True)
    price_total = fields.Float(string='Total Without Tax', readonly=True)
    user_currency_price_total = fields.Float(string="Total Without Tax", compute='_compute_amounts_in_user_currency', digits=0)
    price_average = fields.Float(string='Average Price', readonly=True, group_operator="avg")
    user_currency_price_average = fields.Float(string="Average Price", compute='_compute_amounts_in_user_currency', digits=0)
    currency_rate = fields.Float(string='Currency Rate', readonly=True, group_operator="avg", groups="base.group_multi_currency")
    nbr = fields.Integer(string='# of Lines', readonly=True)  # TDE FIXME master: rename into nbr_lines
    type = fields.Selection([
        ('out_invoice', 'Customer Invoice'),
        ('in_invoice', 'Vendor Bill'),
        ('out_refund', 'Customer Credit Note'),
        ('in_refund', 'Vendor Credit Note'),
        ], readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled')
        ], string='Invoice Status', readonly=True)
    date_due = fields.Date(string='Due Date', readonly=True)
    account_id = fields.Many2one('account.account', string='Account', readonly=True, domain=[('deprecated', '=', False)])
    account_line_id = fields.Many2one('account.account', string='Account Line', readonly=True, domain=[('deprecated', '=', False)])
    partner_bank_id = fields.Many2one('res.partner.bank', string='Bank Account', readonly=True)
    residual = fields.Float(string='Due Amount', readonly=True)
    user_currency_residual = fields.Float(string="Total Residual", compute='_compute_amounts_in_user_currency', digits=0)
    country_id = fields.Many2one('res.country', string='Country of the Partner Company')
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account', groups="analytic.group_analytic_accounting")

    caliber_name = fields.Char('Caliber Name', readonly=True)
    packaging_name = fields.Char('Packaging Name', readonly=True)
    carrier_id = fields.Many2one('delivery.carrier',string = 'Carrier', readonly=True) 
    weight_total = fields.Float(string='Total Weight', readonly=True)
    price_weight = fields.Float(string='Price Weight', group_operator='avg', readonly=True)
    category_partner = fields.Char('Category Partner', readonly=True)
    free_product = fields.Boolean(string='Free Product', default=False, readonly=True)

    stat_prod_1 = fields.Char('Statistics product 1', readonly=True)
    stat_prod_2 = fields.Char('Statistics product 2', readonly=True)
    stat_prod_3 = fields.Char('Statistics product 3', readonly=True)
    stat_prod_4 = fields.Char('Statistics product 4', readonly=True)
    stat_prod_5 = fields.Char('Statistics product 5', readonly=True)
    stat_partner_1 = fields.Char('Statistics partner 1', readonly=True)
    stat_partner_2 = fields.Char('Statistics partner 2', readonly=True)
    stat_partner_3 = fields.Char('Statistics partner 3', readonly=True)
    stat_partner_4 = fields.Char('Statistics partner 4', readonly=True)
    stat_partner_5 = fields.Char('Statistics partner 5', readonly=True)
   
    _order = 'date desc'

    _depends = {
        'account.invoice': [
            'account_id', 'amount_total_company_signed', 'commercial_partner_id', 'company_id',
            'currency_id', 'date_due', 'date_invoice', 'fiscal_position_id',
            'journal_id', 'partner_bank_id', 'partner_id', 'payment_term_id',
            'residual', 'state', 'type', 'user_id',
        ],
        'account.invoice.line': [
            'account_id', 'invoice_id', 'price_subtotal', 'product_id',
            'quantity', 'uom_id', 'account_analytic_id',
        ],
        'product.product': ['product_tmpl_id'],
        'product.template': ['categ_id'],
        'product.uom': ['category_id', 'factor', 'name', 'uom_type'],
        'res.currency.rate': ['currency_id', 'name'],
        'res.partner': ['country_id'],
    }

    def _select(self):
        select_str = """
            SELECT sub.id, sub.date, sub.product_id, sub.partner_id, sub.country_id, sub.account_analytic_id,
                sub.payment_term_id, sub.uom_name, sub.currency_id, sub.journal_id,
                sub.fiscal_position_id, sub.user_id, sub.company_id, sub.nbr, sub.type, sub.state,
                sub.categ_id, sub.date_due, sub.account_id, sub.account_line_id, sub.partner_bank_id,
                sub.product_qty, sub.price_total as price_total, sub.price_average as price_average,
                COALESCE(cr.rate, 1) as currency_rate, sub.residual as residual, sub.commercial_partner_id as commercial_partner_id
                ,sub.carrier_id AS carrier_id, 
                sub.caliber_name AS caliber_name, sub.packaging_name AS packaging_name, 
                
                sub.stat_prod_1 as stat_prod_1, sub.stat_prod_2 as stat_prod_2,
                sub.stat_prod_3 as stat_prod_3, sub.stat_prod_4 as stat_prod_4,
                sub.stat_prod_5 as stat_prod_5, sub.stat_partner_1 as stat_partner_1,
                sub.stat_partner_2 as stat_partner_2, sub.stat_partner_3 as stat_partner_3,
                sub.stat_partner_4 as stat_partner_4, sub.stat_partner_5 as stat_partner_5,
               
                sub.category_partner AS category_partner, sub.weight_total AS weight_total,
                sub.price_weight as price_weight
                
        """
        return select_str

    def _sub_select(self):
        select_str = """
                SELECT ail.id AS id,
                    ai.date_invoice AS date,
                    ail.product_id, ai.partner_id, ai.payment_term_id, ail.account_analytic_id,
                    u2.name AS uom_name,
                    ai.currency_id, ai.journal_id, ai.fiscal_position_id, ai.user_id, ai.company_id,
                    1 AS nbr,
                    ai.type, ai.state, pt.categ_id, ai.date_due, ai.account_id, ail.account_id AS account_line_id,
                    ai.partner_bank_id,
                    SUM ((invoice_type.sign * ail.quantity) / u.factor * u2.factor) AS product_qty,
                    SUM(ail.price_subtotal_signed * invoice_type.sign) AS price_total,
                    SUM(ABS(ail.price_subtotal_signed)) / CASE
                            WHEN SUM(ail.quantity / u.factor * u2.factor) <> 0::numeric
                               THEN SUM(ail.quantity / u.factor * u2.factor)
                               ELSE 1::numeric
                            END AS price_average,
                    ai.residual_company_signed / (SELECT count(*) FROM account_invoice_line l where invoice_id = ai.id) *
                    count(*) * invoice_type.sign AS residual,
                    ai.commercial_partner_id as commercial_partner_id,
                    partner.country_id
                    ,ai.carrier_id AS carrier_id,  
                hfc.name AS caliber_name, hfp.name AS packaging_name, 
                
                pt.statistics_alpha_1 as stat_prod_1, pt.statistics_alpha_2 as stat_prod_2,
                pt.statistics_alpha_3 as stat_prod_3, pt.statistics_alpha_4 as stat_prod_4,
                pt.statistics_alpha_5 as stat_prod_5, partner.statistics_alpha_1 as stat_partner_1,
                partner.statistics_alpha_2 as stat_partner_2, partner.statistics_alpha_3 as stat_partner_3,
                partner.statistics_alpha_4 as stat_partner_4, partner.statistics_alpha_5 as stat_partner_5,
                
                (SELECT min(rpc.name)  FROM res_partner_category rpc 
                    LEFT JOIN res_partner_res_partner_category_rel cat ON  ai.commercial_partner_id =cat.partner_id
                    WHERE (cat.category_id = rpc.id  AND rpc.parent_id is not null ) ) AS category_partner 
                ,sum(ail.weight) AS weight_total, avg(ail.price_weight) AS price_weight
                , CASE WHEN ail.discount=100 THEN true ELSE false END AS free_product
        """
        return select_str

    def _from(self):
        from_str = """
                FROM account_invoice_line ail
                JOIN account_invoice ai ON ai.id = ail.invoice_id
                JOIN res_partner partner ON ai.commercial_partner_id = partner.id
                LEFT JOIN product_product pr ON pr.id = ail.product_id
                left JOIN product_template pt ON pt.id = pr.product_tmpl_id
                LEFT JOIN product_uom u ON u.id = ail.uom_id
                LEFT JOIN product_uom u2 ON u2.id = pt.uom_id
                JOIN (
                    -- Temporary table to decide if the qty should be added or retrieved (Invoice vs Credit Note)
                    SELECT id,(CASE
                         WHEN ai.type::text = ANY (ARRAY['in_refund'::character varying::text, 'in_invoice'::character varying::text])
                            THEN -1
                            ELSE 1
                        END) AS sign
                    FROM account_invoice ai
                ) AS invoice_type ON invoice_type.id = ai.id
                LEFT JOIN hubi_family hfc ON (pt.caliber_id = hfc.id)
                    LEFT JOIN hubi_family hfp ON (pt.packaging_id = hfp.id) 
        """
        return from_str

    def _group_by(self):
        group_by_str = """
                GROUP BY ail.id, ail.product_id, ail.account_analytic_id, ai.date_invoice, ai.id,
                    ai.partner_id, ai.payment_term_id, u2.name, u2.id, ai.currency_id, ai.journal_id,
                    ai.fiscal_position_id, ai.user_id, ai.company_id, ai.type, invoice_type.sign, ai.state, pt.categ_id,
                    ai.date_due, ai.account_id, ail.account_id, ai.partner_bank_id, ai.residual_company_signed,
                    ai.amount_total_company_signed, ai.commercial_partner_id, partner.country_id
                    , ai.carrier_id, hfc.name, hfp.name
                    ,pt.statistics_alpha_1, pt.statistics_alpha_2, pt.statistics_alpha_3, pt.statistics_alpha_4, pt.statistics_alpha_5, 
                    partner.statistics_alpha_1, partner.statistics_alpha_2, partner.statistics_alpha_3, 
                    partner.statistics_alpha_4, partner.statistics_alpha_5
                    
        """
        return group_by_str

    #@api.model_cr
    def init(self):
        # self._table = hubi.invoice.statistic.report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            WITH currency_rate AS (%s)
            %s
            FROM (
                %s %s %s
            ) AS sub
            LEFT JOIN currency_rate cr ON
                (cr.currency_id = sub.currency_id AND
                 cr.company_id = sub.company_id AND
                 cr.date_start <= COALESCE(sub.date, NOW()) AND
                 (cr.date_end IS NULL OR cr.date_end > COALESCE(sub.date, NOW())))
        )""" % (
                    self._table, self.env['res.currency']._select_companies_rates(),
                    self._select(), self._sub_select(), self._from(), self._group_by()))

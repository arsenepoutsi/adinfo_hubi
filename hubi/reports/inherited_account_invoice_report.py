# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import fields, models


class HubiAccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    #carrier_name = fields.Char('Carrier Name', readonly=True)
    caliber_name = fields.Char('Caliber Name', readonly=True)
    packaging_name = fields.Char('Packaging Name', readonly=True)
    carrier_id = fields.Many2one('delivery.carrier',string = 'Carrier', readonly=True) 
    #caliber_id = fields.Many2one('hubi.family', string='Caliber', domain=[('level', '=', 'Caliber')], help="The Caliber of the product.", store=False)
    #packaging_id = fields.Many2one('hubi.family', string='Packaging', domain=[('level', '=', 'Packaging')], help="The Packaging of the product.", store=False)
    weight_total = fields.Float(string='Total Weight', readonly=True)
    price_weight = fields.Float(string='Price Weight', group_operator='avg', readonly=True)
    category_partner = fields.Char('Category Partner', readonly=True)
    free_product = fields.Boolean(string='Free Product', default=False, readonly=True)
    number = fields.Char('Number', readonly=True)
    origin = fields.Char(string='Source Document', readonly=True)
    #amount_before_discount = fields.Float(string='Amount before discount', readonly=True)
    #amount_discount = fields.Float(string='Amount discount', readonly=True)
    stat_prod_1 = fields.Char('statistics product 1', readonly=True)
    stat_prod_2 = fields.Char('statistics product 2', readonly=True)
    stat_prod_3 = fields.Char('statistics product 3', readonly=True)
    stat_prod_4 = fields.Char('statistics product 4', readonly=True)
    stat_prod_5 = fields.Char('statistics product 5', readonly=True)
    stat_partner_1 = fields.Char('statistics partner 1', readonly=True)
    stat_partner_2 = fields.Char('statistics partner 2', readonly=True)
    stat_partner_3 = fields.Char('statistics partner 3', readonly=True)
    stat_partner_4 = fields.Char('statistics partner 4', readonly=True)
    stat_partner_5 = fields.Char('statistics partner 5', readonly=True)

    def _select(self):
        #return super(HubiAccountInvoiceReport, self)._select()
        return super(HubiAccountInvoiceReport, self)._select() + """,sub.carrier_id AS carrier_id, 
                sub.caliber_name AS caliber_name, sub.packaging_name AS packaging_name, 
                sub.category_partner AS category_partner, sub.weight_total AS weight_total,
                sub.price_weight as price_weight, sub.free_product, sub.number, sub.origin
                
                ,sub.stat_prod_1 as stat_prod_1, sub.stat_prod_2 as stat_prod_2,
                sub.stat_prod_3 as stat_prod_3, sub.stat_prod_4 as stat_prod_4,
                sub.stat_prod_5 as stat_prod_5, sub.stat_partner_1 as stat_partner_1,
                sub.stat_partner_2 as stat_partner_2, sub.stat_partner_3 as stat_partner_3,
                sub.stat_partner_4 as stat_partner_4, sub.stat_partner_5 as stat_partner_5
                
                """
                #,sub.amount_before_discount, sub.amount_discount
                
    def _sub_select(self):
        #return super(HubiAccountInvoiceReport, self)._sub_select()
        return super(HubiAccountInvoiceReport, self)._sub_select() + """,ai.carrier_id AS carrier_id,  
                hfc.name AS caliber_name, hfp.name AS packaging_name, 
                
                (SELECT min(rpc.name)  FROM res_partner_category rpc 
                    LEFT JOIN res_partner_res_partner_category_rel cat ON  ai.commercial_partner_id =cat.partner_id
                    WHERE (cat.category_id = rpc.id  AND rpc.parent_id is not null ) ) AS category_partner 
                ,sum(ail.weight_signed) AS weight_total, avg(ail.price_weight) AS price_weight
                , CASE WHEN ail.discount=100 THEN true ELSE false END AS free_product, ai.number, ai.origin

                ,pt.statistics_alpha_1 as stat_prod_1, pt.statistics_alpha_2 as stat_prod_2
                ,pt.statistics_alpha_3 as stat_prod_3, pt.statistics_alpha_4 as stat_prod_4,
                pt.statistics_alpha_5 as stat_prod_5, partner.statistics_alpha_1 as stat_partner_1,
                partner.statistics_alpha_2 as stat_partner_2, partner.statistics_alpha_3 as stat_partner_3,
                partner.statistics_alpha_4 as stat_partner_4, partner.statistics_alpha_5 as stat_partner_5
                """
                #,sum(ai.amount_before_discount_signed) AS amount_before_discount, sum(ai.amount_discount_signed) AS amount_discount  
  
    def _from(self):
        #return super(HubiAccountInvoiceReport, self)._from()
        return super(HubiAccountInvoiceReport, self)._from() + """
                    LEFT JOIN hubi_family hfc ON (pt.caliber_id = hfc.id)
                    LEFT JOIN hubi_family hfp ON (pt.packaging_id = hfp.id) 
                    """
                    #LEFT JOIN res_partner_res_partner_category_rel cat ON  ai.commercial_partner_id =cat.partner_id 
                    #LEFT JOIN res_partner_category rpc ON (cat.category_id = rpc.id  AND rpc.parent_id is not null)
                    
    def _group_by(self):
        #return super(HubiAccountInvoiceReport, self)._group_by()
        return super(HubiAccountInvoiceReport, self)._group_by() + """
            , ai.carrier_id, hfc.name, hfp.name, ai.number, ai.origin 
            ,pt.statistics_alpha_1, pt.statistics_alpha_2, pt.statistics_alpha_3, pt.statistics_alpha_4, pt.statistics_alpha_5, 
            partner.statistics_alpha_1, partner.statistics_alpha_2, partner.statistics_alpha_3, 
            partner.statistics_alpha_4, partner.statistics_alpha_5
        """
            
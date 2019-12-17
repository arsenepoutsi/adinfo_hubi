# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
   
class HubiDeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    agency_number = fields.Char(string='Agency Number')
    agency_city = fields.Char(string='Agency City') 
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street 2')
    city = fields.Char(string='City')
    zip = fields.Char(string='Zip')
    department =  fields.Many2one('hubi.department', string='Department')
    contact_name = fields.Char(string='Contact Name')
    phone = fields.Char(string='Phone')
    mobile = fields.Char(string='Mobile')
    fax = fields.Char(string='Fax')
    mail = fields.Char(string='Mail')
    account = fields.Char(string='Account')
    recipient = fields.Char(string='Recipient')
    color_carrier = fields.Selection([("#FF00FF", "magenta"),("#0000FF", "blue"),
                                    ("#FFFF00", "yellow"),("#FF0000", "red"),
                                    ("#008000", "green"),("#D2691E", "brown"),
                                    ("#FFFFFF", "white"),("#CCCCCC", "grey"),
                                    ("#FFC0CB", "pink")], string='Carrier Color Etiq') 
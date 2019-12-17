# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HubiShipper(models.Model):
    _name = 'hubi.shipper'
    _description = "Shipper"
    _order = 'name'
   
    name = fields.Char(string='Name', required=True)
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
    color_shipper = fields.Char(string='Color', default='#FFFFFF')
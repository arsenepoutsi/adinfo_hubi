# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MIADI_EtiquetteImpression(models.Model):
    _name = "hubi.printing"
    _description = "Printing"
    #_order = "name"
    
    printer_name = fields.Char(string="Printer name", required=True)
    label_text = fields.Text(string="Text of label to print", required=True)
    count = fields.Integer(string="Number of labels to print", required=True,default=1)
    printed = fields.Boolean(string="Is printed ?",default=False)
    printing_date = fields.Date(string="Printing date", required=False)
   
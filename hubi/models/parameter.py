# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MIADI_EtiquetteParameter(models.Model):
    _name = "hubi.parameter"
    _description = "Parameters"
    _order = "name"
    
    name = fields.Char(string="Name", required=True)
    value = fields.Char(string="Value", required=True)
    label_model_id =  fields.Many2one('hubi.labelmodel', string='Label model')
    printer_id =  fields.Many2one('hubi.printer', string='Printer')
    
    
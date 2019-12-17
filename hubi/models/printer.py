# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MIADI_EtiquettePrinter(models.Model):
    _name = "hubi.printer"
    _description = "Printer"
    _order = "name"
    
    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Name", required=True)
    realname = fields.Char(string="Windows or Cups name")
    adressip = fields.Char(string="IP Address")
    port = fields.Integer(string="Port")
    commentary = fields.Text(string="Comment")
    isimpetiq = fields.Boolean(string="Label printer",default=False,help="Checked = label printer, Unchecked = normal printer")
    
    _sql_constraints = [("uniq_id","unique(code)","A printer already exists with this code. It must be unique !"),]
    
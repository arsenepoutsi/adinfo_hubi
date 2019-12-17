# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MIADI_EtiquetteLabelModel(models.Model):
    _name = "hubi.labelmodel"
    _description = "Label model"
    _order = "name"
    
    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Name", required=True)
    file = fields.Char(sting="File", required=False, help="Path of the label file")
    text = fields.Text(string="Label text", required=False, help="Paste here copy of label text")
    commentary = fields.Text(string="Comment")
    with_ean128 = fields.Boolean(string='Label with EAN128', default=False)
    
    _sql_constraints = [("uniq_id","unique(code)","A label model already exists with this code. It must be unique !"),]
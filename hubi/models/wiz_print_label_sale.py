from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import os, sys
#import win32print
from ..controllers import ctrl_print
#from controllers import ctrl_print

class wizard_printlabelsale(models.TransientModel):
    _name = "wiz_print_label_sale"
    _description = "Wizard print label from sale"
    
    printer_id = fields.Many2one("miadi_etiquette.printer", required=True)
    label_id = fields.Many2one("miadi_etiquette.labelmodel", required=True)
    #message = fields.Text(string="Information")
    
    @api.multi
    def print_label(self):
        #FP20190318 avant .file
        #printerName = "\\\\" + self.printer_id.adressIp + "\\" + self.printer_id.realName
        #labelFile = self.label_id.file
        printerName = self.printer_id.name
        labelFile = self.label_id.text 
        informations = [("key1","value1"),("key2","value2"),("key3","value3")]
        ctrl_print.printlabelonwindows(printerName,labelFile,'[',informations)
        return {'type': 'ir.actions.act_window_close'}  
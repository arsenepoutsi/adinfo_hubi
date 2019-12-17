# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, timedelta, datetime
import time
import calendar
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from ..controllers import ctrl_print
from . import tools_hubi

class Wizard_create_print_label(models.TransientModel):
    _name = "wiz_create_print_label"
    _description = "Wizard creation of a label and print it"
    
    @api.onchange('category_id', 'caliber_id', 'packaging_id')
    def _onchange_product_ccp(self):
        product_domain = [('sale_ok','=',True),('etiquette', '=', True)]
        
        if self.category_id:
            product_domain = [('categ_id', '=', self.category_id.id)]+ product_domain[0:]
        if self.caliber_id:
            product_domain = [('caliber_id', '=', self.caliber_id.id)] + product_domain[0:]
        if self.packaging_id:
            product_domain = [('packaging_id', '=', self.packaging_id.id)] + product_domain[0:]
            
        if self.category_id  and self.caliber_id  and self.packaging_id:
            # Recherche de l'article en fonction des sélections 
            id_prod = 0  
            products_templ = self.env['product.template'].search([
            ('categ_id', '=', self.category_id.id),
            ('caliber_id', '=', self.caliber_id.id),
            ('packaging_id', '=', self.packaging_id.id), ])         
            for prod in products_templ:
                id_prod = prod.id
                
            if id_prod != 0:
                # search the code in product.product
                products_prod_prod = self.env['product.product'].search([
                ('product_tmpl_id', '=', id_prod),  ])         
                for prod_prod in products_prod_prod:
                    id_prod_prod = prod_prod.id

                self.product_id = id_prod_prod 
       
        return {'domain': {'product_id': product_domain}}

    @api.onchange( 'partner_id')
    def _onchange_partner(self):
        self.carrier_id = None
        if self.partner_id:
           self.carrier_id = self.partner_id.carrier_id 
            
    @api.onchange('product_id', 'partner_id')
    def _onchange_partner_product(self):
        self.pds = None
        self.nb_mini = None 
        self.color_etiq = None
        self.code_barre = None
        self.printer_id =  None 
        self.label_id = None
        self.etabexp_id = None
        self.health_number = None 
        self.code_128 = None 
        
        
        if self.partner_id:
            # Recherche de l'établissement expéditeur 
            id_partner_sender = 0 
            codbar_128 = ""    
            partner_sender = self.env['res.partner'].search([('id', '=', self.partner_id.sender_establishment.id), ])         
            for sender in partner_sender:
                id_partner_sender = sender.id
                health_no = sender.health_number
                if (not sender.compteur_ean128) or (sender.compteur_ean128==0):
                    compt_ean128 = 1
                else:
                    compt_ean128 = sender.compteur_ean128
                     
            if id_partner_sender != 0:
                self.etabexp_id = id_partner_sender
               #if not self.health_number: 
                self.health_number = health_no           
                if self.partner_id.ean128:
                    if sender.code_ean128:
                        codbar_128 = ("%s%08d") % (sender.code_ean128, compt_ean128)
                        self.code_128 = codbar_128
           
            color_partner = self.partner_id.customer_color_etiq
            printer_partner = self.partner_id.etiq_printer
            modele_partner = self.partner_id.label_model_id
             
            
        if (self.product_id) and (self.partner_id):
            color_prod = self.product_id.product_color
            code_barre_prod = self.product_id.barcode
            printer_prod = self.product_id.etiq_printer
            modele_prod = self.product_id.label_model_id
            weight_prod = self.product_id.weight
            number_prod = self.product_id.quantity

                # search the code in product.product
                #products_prod_prod = self.env['product.product'].search([('product_tmpl_id', '=', id_prod),  ])         
                #for prod_prod in products_prod_prod:
                #    id_prod_prod = prod_prod.id
                #    color_prod = prod_prod.product_color
                #    code_barre_prod = prod_prod.barcode
                #    printer_prod = prod_prod.etiq_printer
                #    modele_prod = prod_prod.label_model_id
                #    weight_prod = prod_prod.weight
                #    number_prod = prod_prod.quantity
                
            # Recherche du tarif de l'article        
            id_partner_price = 0  
            partner_price = self.env['product.pricelist.item'].search([
                    ('pricelist_id', '=', self.partner_id.property_product_pricelist.id),
                    ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),
                     ])         
            for price in partner_price:
                id_partner_price = price.id
                
                color_price = price.price_color
                code_barre_price = price.price_ean13
                printer_price = price.price_printer
                modele_price = price.label_model_id   
            
            self.pds = weight_prod
            self.nb_mini = number_prod   
              
            # Priorité 1 : Tarif
            if id_partner_price != 0:
                    self.color_etiq = color_price
                    self.code_barre = code_barre_price
                    self.printer_id =  printer_price 
                    self.label_id = modele_price
                
            if not self.color_etiq:
                if color_prod:
                    self.color_etiq = color_prod
                elif color_partner:
                    self.color_etiq = color_partner  

            if not self.code_barre:    
                    self.code_barre = code_barre_prod 
            if not self.printer_id:
                if printer_prod:
                    self.printer_id =  printer_prod 
                elif printer_partner:
                    self.printer_id = printer_partner     
                
            if not self.label_id:    
                #Priorité 2 = client
                if modele_partner:
                    self.label_id =  modele_partner 
                elif modele_prod:
                    self.label_id = modele_prod    
    
    @api.depends('product_id', 'packaging_date', 'partner_id')
    def _compute_dluo(self):
        if self.packaging_date and self.product_id.id:
            if self.partner_id.dlc_number_day and self.partner_id.dlc_number_day>0:
                val_nb_day=self.partner_id.dlc_number_day
            else:    
                val_nb_day=self.product_id.categ_id.nb_day_dluo or 7
            val_calcul_dluo = fields.Date.from_string(self.packaging_date) + timedelta(days=val_nb_day)
            self.date_dluo = val_calcul_dluo
               
    packaging_date = fields.Date(string="Packaging date",default=lambda self: fields.Date.today())
    sending_date = fields.Date(string="Sending date",default=lambda self: fields.Date.today())
    caption_etiq = fields.Char(string="Caption label")
    product_id = fields.Many2one('product.product', string='Product')
    #product_name = fields.Char(string="Product")
    #caliber_name = fields.Char(string="Caliber")
    #packaging_name = fields.Char(string="Packaging")
    category_id = fields.Many2one('product.category', 'Internal Category', domain=[('parent_id','!=',False), ('shell', '=', True)], store=False)
    caliber_id = fields.Many2one('hubi.family', string='Caliber', domain=[('level', '=', 'Caliber')], help="The Caliber of the product.", store=False)
    packaging_id = fields.Many2one('hubi.family', string='Packaging', domain=[('level', '=', 'Packaging')], help="The Packaging of the product.", store=False)

    code_barre = fields.Char(string="Bar Code")
    code_128 = fields.Char(string="Bar Code 128")
    qte = fields.Float(string="Quantity", default = 1)
    pds = fields.Float(string="Weight", default = 0)
    numlot = fields.Char(string="Batch number")
    nb_mini = fields.Float(string="Minimum number", default = 0)
    health_number = fields.Char(string='Health Number')
    partner_id = fields.Many2one("res.partner", string='Customer')
    etabexp_id = fields.Many2one("res.partner", string='Sender establishment')
    printer_id = fields.Many2one("hubi.printer", string='Label Printer', domain=[('isimpetiq', '=', True)])
    label_id = fields.Many2one("hubi.labelmodel", string='Label Model')
    color_etiq = fields.Selection([("#FF00FF", "magenta"),("#0000FF", "blue"),
                                    ("#FFFF00", "yellow"),("#FF0000", "red"),
                                    ("#008000", "green"),("#D2691E", "brown"),
                                    ("#FFFFFF", "white"),("#CCCCCC", "grey"),
                                    ("#FFC0CB", "pink")], string='Color Etiq')
    #carrier_id = fields.Integer(string="Carrier ID")
    carrier_id = fields.Many2one('delivery.carrier', 'Carrier ID')
    date_dluo = fields.Date(string="DLUO Date", store=True, compute='_compute_dluo')
    message = fields.Text(string="Information")
   
    @api.multi
    def create_print_label_old(self):  
        self.env.cr.commit()
        query = """SELECT to_char(sl.packaging_date,'DD/MM/YYYY'), to_char(sl.sending_date,'DD/MM/YYYY'), pt.etiq_description, hfc.name, hfp.name,
                    pt.etiq_mention, 
                    sl.code_barre, sl.qte, sl.pds, sl.nb_mini, p.realname, p.adressip,l.file,
                    t.customer_name_etiq, t.customer_city_etiq, etab.health_number, etab.company_name_etiq, etab.company_city_etiq, 
                    sl.numlot, sl.color_etiq, pt.etiq_latin, pt.etiq_spanish
                    FROM wiz_create_print_label sl
                    LEFT JOIN hubi_printer p ON sl.printer_id = p.id 
                    LEFT JOIN hubi_labelmodel l ON sl.label_id = l.id
                    INNER JOIN res_partner t ON t.id = sl.partner_id
                    LEFT JOIN res_partner etab ON etab.id = sl.etabexp_id
                    INNER JOIN product_product prod ON prod.id = sl.product_id
                    INNER JOIN product_template pt ON prod.product_tmpl_id = pt.id
                    INNER JOIN hubi_family AS hfc ON pt.caliber_id = hfc.id 
                    INNER JOIN hubi_family AS hfp ON pt.packaging_id = hfp.id 
                    WHERE sl.id=""" + str(self.id)
        self.env.cr.execute(query)
        
        result = [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13], r[14], r[15], r[16], r[17], r[18], r[19], r[20], r[21]) for r in self.env.cr.fetchall()]
        
        for packaging_date,sending_date,product_name,caliber_name,packaging_name,etiq_mention,code_barre,qte,pds,nb_mini,printerName,adressip,labelFile,clientname1,clientname2,numsanitaire,etabexp1,etabexp2, lot, color, etiq_latin, etiq_spanish in result:
            informations = [
                ("dateemb",packaging_date),
                ("dateexp",sending_date),
                ("produit",product_name),
                ("calibre",caliber_name),
                ("conditionnement",packaging_name),
                ("mention",etiq_mention),
                ("latin",etiq_latin),
                ("spanish",etiq_spanish),
                ("codebarre",code_barre),
                ("qte",int(qte)),
                ("pds",pds),
                ("nb",int(nb_mini)),
                ("numsanitaire",numsanitaire),
                ("client1", clientname1),
                ("client2", clientname2),
                ("etab1", etabexp1),
                ("etab2", etabexp2),
                ("lot", lot),
                ("color", color)]
            
            if(printerName is not None and printerName != "" and labelFile is not None and labelFile != ""):
                if (adressip is not None and adressip != ""):
                    printer = "\\\\" + adressip + "\\" + printerName
                else:
                    printer = printerName
                    
                ctrl_print.printlabelonwindows(printer,labelFile,'[',informations)    

        return {'type': 'ir.actions.act_window_close'} 
    
    @api.multi
    def create_print_label(self):  
        self.env.cr.commit()
        no_id = self.id
        nom_table = "wiz_create_print_label"
        tools_hubi.prepareprintlabel(self, nom_table, no_id)
        return {'type': 'ir.actions.act_window_close'} 
            
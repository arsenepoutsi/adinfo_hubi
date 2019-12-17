from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from ..controllers import ctrl_print
from . import tools_hubi
import datetime

class wizard_sale_order_print_label(models.Model):
    _name = "wiz_sale_order_print_label"
    _description = "Wizard to create table in order to stock order line"
    
    sale_order_line_id = fields.Char(string="Line Id")
    sale_order_id = fields.Integer(string="Sale Order Id")
    sale_order_num = fields.Char(string="Piece")
    packaging_date = fields.Date(string="Packaging date")
    sending_date = fields.Date(string="Sending date")
    caption_etiq = fields.Char(string="Caption label")
    product_id = fields.Integer(string="Product ID")
    product_name = fields.Char(string="Product")
    caliber_name = fields.Char(string="Caliber")
    packaging_name = fields.Char(string="Packaging")
    code_barre = fields.Char(string="Bar Code")
    code_128 = fields.Char(string="Bar Code 128")
    qte = fields.Float(string="Quantity")
    pds = fields.Float(string="Weight")
    numlot = fields.Char(string="Batch number")
    nb_mini = fields.Float(string="Minimum number")
    partner_id = fields.Many2one("res.partner", string='Customer')
    etabexp_id = fields.Many2one("res.partner", string='Sender establishment')
    printer_id = fields.Many2one("hubi.printer", string='Label Printer', domain=[('isimpetiq', '=', True)])
    label_id = fields.Many2one("hubi.labelmodel", string='Label Model')
    color_etiq = fields.Selection([("#FF00FF", "magenta"),("#0000FF", "blue"),
                                    ("#FFFF00", "yellow"),("#FF0000", "red"),
                                    ("#008000", "green"),("#D2691E", "brown"),
                                    ("#FFFFFF", "white"),("#CCCCCC", "grey"),
                                    ("#FFC0CB", "pink")], string='Color Etiq')
    carrier_id = fields.Integer(string="Carrier ID")
    date_dluo = fields.Date(string="DLUO Date")
    
    #@api.model
    #@api.multi
    def action_view_sale_order_line_print_label(self):
        query = """SELECT id FROM wiz_sale_order_print_label"""
        self.env.cr.execute(query)
        order_line = [r[0] for r in self.env.cr.fetchall()]
        
        if len(order_line) >= 1:
            action = self.env.ref('hubi.action_wiz_sale_order_print_label_tree').read()[0]
            action['domain'] = [('id', 'in', order_line)]
        else:
            action = {'type': 'ir.actions.act_window_close'}    
            
        return action  

    #@api.multi
    def update_wiz_table(self):
        line_id = getattr(self, '_origin', self)._ids[0]
        packaging_date = self.packaging_date
        sending_date = self.sending_date
        code_barre = self.code_barre
        qte = self.qte
        pds = self.pds
        nb_mini = self.nb_mini
        printer_id = self.printer_id.id
        label_id = self.label_id.id
        numlot = self.numlot
        
        req = """UPDATE wiz_sale_order_print_label SET 
                    packaging_date=%s,
                    sending_date=%s,
                    code_barre=%s,
                    qte=%s,
                    pds=%s,
                    nb_mini=%s,
                    numlot=%s """
        
        params = (packaging_date, sending_date, code_barre, qte, pds, nb_mini, numlot)
        
        if printer_id:
            req += ",printer_id=" + str(printer_id) + " "
            #params.__add__(printer_id)
            
        if label_id:
            req += ",label_id=" + str(label_id) + " "
            #params.__add__(label_id)
            
        req += "WHERE id='" + str(line_id) + "' "
        #params.__add__(line_id)

        self._cr.execute(req,params)
        self.env.cr.commit()
        
    @api.onchange('packaging_date','sending_date','code_barre','qte','pds','nb_mini','printer_id','label_id','numlot')
    def _onchange_order_line_print_label(self):
        self.update_wiz_table()

    #@api.multi
    def load_order_line(self, origin):
        user = self.env.user.id      
        self.delete_table_temp(user)        
                
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or self._ids or []
        
        self.env.cr.commit()
        params = [tuple(active_ids)]
        #FP20190318 Remplacement ???? sl.pds par case ...sl.pds / sl.qte end
        query1 = """SELECT o.id, o.name,ol.id as line_id,o.packaging_date, o.sending_date, ol.product_id, p.default_code, ol.product_uom_qty, ol.weight,
                    categ.name, cond.name, ol.no_lot, 
                    t.id, etab.id, t.etiq_printer, t.label_model_id, t.customer_color_etiq,
                    pt.quantity,pt.etiq_printer, pt.label_model_id, pt.product_color, p.barcode,
                    linepl.price_printer, linepl.label_model_id, linepl.price_color, linepl.price_ean13, o.carrier_id, ol.date_dluo
                    FROM sale_order o 
                    INNER JOIN sale_order_line ol ON o.id = ol.order_id
                    INNER JOIN product_product p ON ol.product_id = p.id
                    INNER JOIN res_partner t ON o.partner_id = t.id
                    LEFT JOIN res_partner etab ON t.sender_establishment = etab.id
                    INNER JOIN product_template pt ON p.product_tmpl_id = pt.id 
                    LEFT JOIN hubi_family categ ON pt.caliber_id = categ.id
                    LEFT JOIN hubi_family cond ON pt.packaging_id = cond.id 
                    LEFT JOIN ir_property prop ON (prop.res_id = concat('res.partner,', t.id) AND prop.value_reference like 'product.pricelist,_')
                    LEFT JOIN product_pricelist pricelist ON prop.value_reference = concat('product.pricelist,', pricelist.id)
                    LEFT JOIN product_pricelist_item linepl ON (pricelist.id = linepl.pricelist_id AND pt.id = linepl.product_tmpl_id)"""

        if origin == 'order':
            query2 = """ WHERE pt.etiquette = true AND o.id IN %s ORDER BY o.name """
        else:
            query2 = """ WHERE ol.id IN %s ORDER BY o.name """
                
        query = ''.join([query1, query2])
        
        self.env.cr.execute(query, tuple(params))
        list_orders_ids = []
        
        ids = [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], \
                r[11], r[12], r[13], r[14], r[15], r[16], r[17], r[18], r[19], r[20], \
                r[21], r[22], r[23], r[24], r[25], r[26], r[27]) for r in self.env.cr.fetchall()]
        
        for order_id, order_num, sale_order_line_id, packaging_date, sending_date, product_id, product_code, qte, weight, calibre, cond, \
        lot, clientid, etabexpid, clientprinter, clientetiq, clientcolor, nbmini, prodprinter, prodetiq, prodcolor, \
        prodcodbar, priceprinter, priceetiq, pricecolor, pricecodbar, carrier, date_dluo  in ids:
            # Imprimante
            if (priceprinter is not None and priceprinter != ""):
                printer = priceprinter
            else:
                if(prodprinter is not None and prodprinter != ""):
                    printer = prodprinter
                else:
                    if(clientprinter is not None and clientprinter != ""):
                        printer = clientprinter
                    else:
                        printer = None
            # Modèle Etiquette
            if (priceetiq is not None and priceetiq != ""):
                etiq = priceetiq
            else:
                if(clientetiq is not None and clientetiq != ""):
                    etiq = clientetiq
                else:
                    if(prodetiq is not None and prodetiq != ""):
                        etiq = prodetiq
                    else:
                        etiq = None
            # Couleur
            if (pricecolor is not None and pricecolor != ""):
                color = pricecolor
            else:
                if(prodcolor is not None and prodcolor != ""):
                    color = prodcolor
                else:
                    if(clientcolor is not None and clientcolor != ""):
                        color = clientcolor
                    else:
                        color = None
            #Code Barre
            if (pricecodbar is not None and pricecodbar != ""):
                codebarre = pricecodbar
            else:
                if(prodcodbar is not None and prodcodbar != ""):
                    codebarre = prodcodbar
                else:
                    codebarre = None
            
            # printer = None  etiq = None => Default Value
            if (printer is None or etiq is None):
                default_value = self.env['hubi.parameter'].search([('name', '=', 'DEFAULT')])
                for default in default_value:
                    if (printer is None):
                        printer = default.printer_id.id
                    if (etiq is None):
                        etiq = default.label_model_id.id
                    
            insert = {
            'sale_order_id': order_id,
            'sale_order_num': order_num,
            'sale_order_line_id': sale_order_line_id,
            'packaging_date': packaging_date,
            'sending_date': sending_date,
            'product_id': product_id,
            'product_name': product_code,
            'caliber_name': calibre,
            'packaging_name': cond,
            'nb_mini': nbmini,
            'code_barre': codebarre,
            'qte': qte,
            'pds': weight,
            'numlot': lot,
            'partner_id': clientid,
            'etabexp_id': etabexpid,
            'printer_id': printer,
            'label_id': etiq,
            'color_etiq':color,
            'carrier_id':carrier,
            'date_dluo':date_dluo,
            }
            prepare_print_label = self.env['wiz_sale_order_print_label'].create(insert)
            list_orders_ids.append(int(prepare_print_label.id))
            #list_orders_ids.append(int(prepare_print_label.sale_order_line_id))
        
        self.env.cr.commit()
                
        return list_orders_ids
        
        #return self.action_view_sale_order_line_print_label()
        #return {'type': 'ir.actions.act_window_close'}
    
    
    #@api.multi
    def print_label_from_order_old(self):
        #self.update_wiz_table()
        self.env.cr.commit()

        #context = dict(self._context or {})
        active_ids = self.env['wiz_sale_order_print_label'].browse(self.env.context['active_ids'])
        #active_ids = context.get('active_ids', []) or []
        #active_ids = self.env.context.get('active_ids', [])
        
        for id in self.ids:
            self.print_line(id)
        #for id in active_ids:
            #self.print_line(id)
           
        return self.ids
        #return {'type': 'ir.actions.act_window_close'}

    #@api.multi
    def print_label_from_order(self):
        self.env.cr.commit()

        query_args = {'id_sale': self.sale_order_id}
        query = """SELECT id 
                    FROM wiz_sale_order_print_label 
                    WHERE qte<>0 AND label_id is not null"""

        self.env.cr.execute(query, query_args)
        ids = [(r[0]) for r in self.env.cr.fetchall()]

        for id in ids:
            self.print_line(id)
           
        return self.ids
    
    #@api.multi
    def print_line_old(self,id):
        query = """SELECT to_char(sl.packaging_date,'DD/MM/YYYY'),to_char(sl.sending_date,'DD/MM/YYYY'),pt.etiq_description,sl.caliber_name,sl.packaging_name,
                    pt.etiq_mention, 
                    sl.code_barre,sl.qte,sl.pds,sl.nb_mini,p.realname,p.adressip,l.file,
                    t.customer_name_etiq, t.customer_city_etiq, etab.health_number, etab.company_name_etiq, etab.company_city_etiq, sl.numlot, sl.color_etiq
                    FROM wiz_sale_order_print_label sl
                    LEFT JOIN hubi_printer p ON sl.printer_id = p.id 
                    LEFT JOIN hubi_labelmodel l ON sl.label_id = l.id
                    INNER JOIN res_partner t ON t.id = sl.partner_id
                    LEFT JOIN res_partner etab ON etab.id = sl.etabexp_id
                    INNER JOIN product_product prod ON prod.id = sl.product_id
                    INNER JOIN product_template pt ON prod.product_tmpl_id = pt.id
                    WHERE sl.id=""" + str(id)
        self.env.cr.execute(query)
        
        result = [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13], r[14], r[15], r[16], r[17], r[18], r[19]) for r in self.env.cr.fetchall()]
        
        for packaging_date,sending_date,product_name,caliber_name,packaging_name,etiq_mention,code_barre,qte,pds,nb_mini,printerName,adressip,labelFile,clientname1,clientname2,numsanitaire,etabexp1,etabexp2, lot, color in result:
            informations = [
                ("dateemb",packaging_date),
                ("dateexp",sending_date),
                ("produit",product_name),
                ("calibre",caliber_name),
                ("conditionnement",packaging_name),
                ("mention",etiq_mention),
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
        
    #@api.multi
    def print_line(self,id):  
        nom_table = "wiz_sale_order_print_label"
        tools_hubi.prepareprintlabel(self, nom_table, id)
        #return {'type': 'ir.actions.act_window_close'} 
            
    #@api.multi
    def delete_table_temp(self, user):
        query = "DELETE FROM wiz_sale_order_print_label WHERE create_uid=" + str(user)
        self.env.cr.execute(query)
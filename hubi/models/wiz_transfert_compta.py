# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, timedelta, datetime
import time
import calendar
from dateutil.relativedelta import relativedelta
import base64
from . import controller_export_csv_order_line
#import csv
#import codecs
#import collections
import io
import os
import sys
from odoo.tools import pycompat, misc
from . import tools_hubi

class Wizard_transfert_compta(models.TransientModel):
    _name = "wiz.transfertcompta"
    _description = "Wizard transfert compta"
    
    def add_months(sourcedate,months):
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month // 12
        month = month % 12 + 1
        day = min(sourcedate.day,calendar.monthrange(year,month)[1])
        return datetime.date(year,month,day)


    @api.model
    def _default_start(self):
        #return fields.Date.context_today(self)
        start = datetime.today() + timedelta(days=-7)
        return fields.Date.context_today(self, timestamp=start)

    @api.model
    def _default_finish(self):
        finish = datetime.today() + timedelta(days=7)
        return fields.Date.context_today(self, timestamp=finish)
    
    @api.model
    def _get_values(self, valeur):
        """
        Return values for the fields 
        """
        
        val_path_account_transfer = ''
        val_account_file_transfer = ''
        val_writing_file_transfer = ''
        val_mail_accounting = False
        
        company_id = self.env['res.company']._company_default_get('hubi.general_settings')
        val_company_id =company_id.id 
        val_name = 'General Settings'
        
        settings = self.env['hubi.general_settings'].search([('name','=', val_name), ('company_id','=', val_company_id)])
        for settings_vals in settings:
            val_path_account_transfer = settings_vals.path_account_transfer
            val_account_file_transfer = settings_vals.account_file_transfer
            val_writing_file_transfer = settings_vals.writing_file_transfer
            val_mail_accounting = settings_vals.mail_accounting
            
        if valeur == 'path_account_transfer':
            retour = val_path_account_transfer   
                    
        if valeur == 'account_file_transfer':
            retour = val_account_file_transfer  
                    
        if valeur == 'writing_file_transfer':
            retour = val_writing_file_transfer  
            
        if valeur == 'mail_accounting':
            retour = val_mail_accounting                  
        return retour

    date_start = fields.Date('Start Date', help="Starting date for the creation of invoices", default=lambda self: self._default_start())
    date_end = fields.Date('End Date', help="Ending valid for the the creation of invoices", default=lambda self: fields.Date.today())
    journal_ids = fields.Many2many(comodel_name='account.journal',string="Journals", default=lambda self: self.env['account.journal'].search([('type', 'in', ['sale', 'purchase'])]),required=True)
    path_account_transfer = fields.Char(string='Path For Account Transfer', default=lambda self: self._get_values('path_account_transfer'))
    account_file_transfer = fields.Char(string='File For Account Transfer', default=lambda self: self._get_values('account_file_transfer'))
    writing_file_transfer = fields.Char(string='File For Writing Transfer', default=lambda self: self._get_values('writing_file_transfer'))
    template_id  = fields.Many2one('mail.template', 'Mail',  domain=[('model', '=', 'wiz.transfertcompta')])
    message = fields.Text(string="Information")
    mail_accounting = fields.Boolean(string="Send Email", default=lambda self: self._get_values('mail_accounting'))
    re_transfer = fields.Boolean(string="Re-Transfer", default=False)
    compta_data = fields.Binary('Compta File', readonly=True)
    filename = fields.Char(string='Filename', size=256, readonly=True)            
    partner_data = fields.Binary('Partner File', readonly=True)
    partner_filename = fields.Char(string='Partner Filename', size=256, readonly=True)            

    #@api.multi
    def send_mail_template(self):   

        '''
        This function opens a window to compose an email, with the  template message loaded by default
        '''
        csv_path = self.path_account_transfer
        account_file = self.account_file_transfer
        writing_file = self.writing_file_transfer
            
        if csv_path is None:
           csv_path = os.environ.get('LOCALAPPDATA') or os.getcwd()          # c:\odoo\odoo11
        if account_file is None:   
            account_file = 'comptes.txt'
        if writing_file is None:    
            writing_file = 'ecritures.txt'
            
        csv_path = os.path.normpath(csv_path)
        if not csv_path.endswith('\\'):
           csv_path = csv_path + '\\' 
        
         
        writing_f = csv_path + writing_file
        account_f = csv_path + account_file
        attachments_ids = []
        
        if os.path.exists(writing_f):
            with io.open(writing_f, "rb") as wfile:
                byte_data_w = wfile.read()
            
            attachment_w = {
                'name': ("%s" %writing_file),
                'datas_fname': writing_file,
                'datas': base64.encodestring(byte_data_w),
                'type': 'binary'
                }
            id_w = self.env['ir.attachment'].create(attachment_w)
            attachments_ids.append(id_w.id)
 
        if os.path.exists(account_f):
            with io.open(account_f, "rb") as afile:
                byte_data_a = afile.read()

            attachment_a = {
                'name': ("%s" %account_file),
                'datas_fname': account_file,
                'datas': base64.encodestring(byte_data_a),
                'type': 'binary'
                }
            id_a = self.env['ir.attachment'].create(attachment_a)  
            attachments_ids.append(id_a.id)
        
        email_template = self.env.ref('hubi.email_template_accounting_transfer')
        email_template.attachment_ids =  False
        #email_template.attachment_ids =  [(4,id_w.id)]
        email_template.attachment_ids = attachments_ids
        
        #'datas': byte_data,
        #data=0
        #'datas': base64.encode(ufile.read(),data),
        
        #files = os.listdir(csv_path)
        #for ufile in files:


        #email_template.send_mail(self.id, raise_exception=False, force_send=True)
        
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('hubi', 'email_template_accounting_transfer')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        #'attachment_ids':  [(4,id.id)],    
        ctx = {
            'default_model': 'wiz.transfertcompta',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'attachment_ids':  attachments_ids,
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }  
   
    def ecrire_ligne_comptes_ebp(self,auxiliary_account,length_account_gen,length_account_aux,complete_0_gen,complete_0_aux, partner_id, name, street, city, zip, code_pays, country, phone, mobile):
        ligne_p = ""
        listrow_p = list()
        listrow_ps = list()
        
        partner  = self.env['res.partner'].search([('id', '=',partner_id),  ])

        # partner = Customer
        account_customer_id = partner.property_account_receivable_id.id
        account_customer  = self.env['account.account'].search([('id', '=',account_customer_id),  ])
        account_gen_customer_code = account_customer.code
        account_aux_customer_code = partner.auxiliary_account_customer or False
            
        # partner = Supplier
        account_supplier_id = partner.property_account_payable_id.id
        account_supplier  = self.env['account.account'].search([('id', '=',account_supplier_id),  ])
        account_gen_supplier_code = account_supplier.code
        account_aux_supplier_code = partner.auxiliary_account_supplier or False
            
        if auxiliary_account:
            account_customer_code = account_aux_customer_code
            account_supplier_code = account_aux_supplier_code
        else:
            account_customer_code = account_gen_customer_code
            account_supplier_code = account_gen_supplier_code 
        
        if length_account_gen != 0:
                if (complete_0_gen):
                    if account_customer_code:
                        account_customer_code = account_customer_code.ljust(length_account_gen,'0')
                    if account_supplier_code:    
                        account_supplier_code = account_supplier_code.ljust(length_account_gen,'0')
                else: 
                    if account_customer_code:   
                        account_customer_code = account_customer_code[0:length_account_gen]
                    if account_supplier_code:  
                        account_supplier_code = account_supplier_code[0:length_account_gen]
                    
        interloc = ""
        f_name =""
        f_street =""
        f_zip =""
        f_city =""
        f_country =""
        f_phone =""
        f_mobile = ""
                
        if name:
            f_name = name[0:60].replace(',', ' ') 
            f_name = tools_hubi.replace_accent(self, f_name)
                     
        if street:
            f_street = street[0:100].replace(',', ' ')
        if zip:
            f_zip = zip[0:5]
        if city:
             f_city = city[0:30].replace(',', ' ') 
        if country:
            f_country = country[0:35]           
        if phone:
            f_phone = phone[0:20].replace(',', ' ')
        if mobile:
            f_mobile = mobile[0:20].replace(',', ' ') 
            
        if account_customer_code and partner.customer:
            csv_p_row = ""
            csv_p_row+= "{},".format(account_customer_code[0:15])
            csv_p_row+= "{},".format(f_name[0:60])
            csv_p_row+= "{},".format(f_name[0:30])
            csv_p_row+= "{},".format(f_street[0:100])
            csv_p_row+= "{},".format(f_zip[0:5])
            csv_p_row+= "{},".format(f_city[0:30])
            csv_p_row+= "{},".format(f_country[0:35])
            csv_p_row+= "{},".format(interloc)
            csv_p_row+= "{},".format(f_phone[0:20])
            csv_p_row+= "{},".format(f_mobile[0:20])
           
            ligne_p+="{}\n".format(csv_p_row[:-1])
            #lines.append(([account_customer_code[0:15], f_name[0:60], f_name[0:30], f_street[0:100], f_zip[0:5], f_country[0:35], interloc, f_phone[0:20], f_mobile[0:20]  ]))

            listrow_p.append("{}".format(account_customer_code[0:15]))
            listrow_p.append("{}".format(f_name[0:60]))
            listrow_p.append("{}".format(f_name[0:30]))
            listrow_p.append("{}".format(f_street[0:100]))
            listrow_p.append("{}".format(f_zip[0:5]))
            listrow_p.append("{}".format(f_country[0:35]))
            listrow_p.append("{}".format(interloc))
            listrow_p.append("{}".format(f_phone[0:20]))
            listrow_p.append("{}".format(f_mobile[0:20]))
 
        if account_supplier_code and partner.supplier:
            csv_p_row = ""
            csv_p_row+= "{},".format(account_supplier_code[0:15])
            csv_p_row+= "{},".format(f_name[0:60])
            csv_p_row+= "{},".format(f_name[0:30])
            csv_p_row+= "{},".format(f_street[0:100])
            csv_p_row+= "{},".format(f_zip[0:5])
            csv_p_row+= "{},".format(f_city[0:30])
            csv_p_row+= "{},".format(f_country[0:35])
            csv_p_row+= "{},".format(interloc)
            csv_p_row+= "{},".format(f_phone[0:20])
            csv_p_row+= "{},".format(f_mobile[0:20])
           
            ligne_p+="{}\n".format(csv_p_row[:-1])
            #lines.append(([account_supplier_code[0:15], f_name[0:60], f_name[0:30], f_street[0:100], f_zip[0:5], f_country[0:35], interloc, f_phone[0:20], f_mobile[0:20]  ]))
            listrow_ps.append("{}".format(account_supplier_code[0:15]))
            listrow_ps.append("{}".format(f_name[0:60]))
            listrow_ps.append("{}".format(f_name[0:30]))
            listrow_ps.append("{}".format(f_street[0:100]))
            listrow_ps.append("{}".format(f_zip[0:5]))
            listrow_ps.append("{}".format(f_country[0:35]))
            listrow_ps.append("{}".format(interloc))
            listrow_ps.append("{}".format(f_phone[0:20]))
            listrow_ps.append("{}".format(f_mobile[0:20]))
 

        #return ligne
        return {
            'ligne_p': ligne_p,
            'listrow_p': listrow_p,
            'listrow_ps': listrow_ps,
        }    

    
    def ecrire_ligne_ebp(self,auxiliary_account,length_account_gen,length_account_aux,complete_0_gen,complete_0_aux, move_name, journal, compte, partner_name, move_line_name, date_ecr, date_ech, debit, credit, currency, ref, compte_anal, partner_id, nb_lig):
        ligne = ""
        listrow = list()
        libelle = ""
        n_piece=""
               
        partner  = self.env['res.partner'].search([('id', '=',partner_id),  ])

        # partner = Customer
        account_customer_id = partner.property_account_receivable_id.id
        account_customer  = self.env['account.account'].search([('id', '=',account_customer_id),  ])
        account_gen_customer_code = account_customer.code
        account_aux_customer_code = partner.auxiliary_account_customer or False
            
        # partner = Supplier
        account_supplier_id = partner.property_account_payable_id.id
        account_supplier  = self.env['account.account'].search([('id', '=',account_supplier_id),  ])
        account_gen_supplier_code = account_supplier.code
        account_aux_supplier_code = partner.auxiliary_account_supplier or False
        
        compte_gen = compte    
        if (compte_gen == account_gen_customer_code ) or (compte_gen == account_gen_supplier_code):
             if auxiliary_account:
                if (compte_gen == account_gen_customer_code) and (account_aux_customer_code):
                    compte_gen = account_aux_customer_code
                if (compte_gen == account_gen_supplier_code) and (account_aux_supplier_code):
                    compte_gen == account_aux_supplier_code
        
        if length_account_gen != 0:  
            if (complete_0_gen):
                compte_gen = compte_gen.ljust(length_account_gen,'0')
                        
            else:    
                compte_gen=compte_gen[0:length_account_gen] 

        if move_line_name =="/":
            if partner_name:
                libelle = partner_name
        else:
            if move_line_name:
                libelle = move_line_name  
                    
        libelle = libelle.replace(',', '.') 
        libelle = tools_hubi.replace_accent(self, libelle)
                             
        if move_name:
            n_piece = move_name
                    
        if debit == 0:
            montant = credit
            sens = "C"
        else:         
            montant = debit
            sens = "D"
        type_tva = "" 
            
        csv_row = ""
        csv_row+= "{},".format(nb_lig)
        csv_row+= "{},".format(date_ecr)
        csv_row+= "{},".format(journal)
        csv_row+= "{},".format(compte_gen[0:15])
        csv_row+= "{},".format(libelle[0:40])
        csv_row+= "{},".format(libelle[0:40])
        csv_row+= "{},".format(n_piece[-10:])
        csv_row+= "{0:.2f},".format(montant)
        csv_row+= "{},".format(sens)
        csv_row+= "{},".format(date_ech)
        csv_row+= "{},".format(type_tva)
        csv_row+= "{},".format(currency)
            
        ligne+="{}\n".format(csv_row[:-1])
        
        listrow.append("{}".format(nb_lig))
        listrow.append("{}".format(date_ecr))
        listrow.append("{}".format(journal))
        listrow.append("{}".format(compte_gen[0:15]))
        listrow.append("{}".format(libelle[0:40]))
        listrow.append("{}".format(libelle[0:40]))
        listrow.append("{}".format(n_piece[-10:]))
        listrow.append("{0:.2f}".format(montant))
        listrow.append("{}".format(sens))
        listrow.append("{}".format(date_ech))
        listrow.append("{}".format(type_tva))
        listrow.append("{}".format(currency))
            
        #Analytique
        pourc="100.00"
        if compte_anal:
            csv_row = ">"
            csv_row+= "{},".format(compte_anal) 
            csv_row+= "{},".format(pourc)
            csv_row+= "{},".format(montant)
               
            ligne+="{}\n".format(csv_row[:-1])
        
   
        #return ligne
        
        return {
            'ligne': ligne,
            'listrow': listrow,
        }    
        
    @api.multi
    def transfert_compta(self, **kw):  
        #s = s[ beginning : beginning + LENGTH]
        date_d =  self.date_start[0:4] + self.date_start[5:7] + self.date_start[8:10] 
        date_f =  self.date_end[0:4]+ self.date_end[5:7] + self.date_end[8:10] 
        query_args = {'date_start' : date_d,'date_end' : date_f}
        
        #dirpath2 = os.path.dirname(os.path.realpath(__file__))   # c:\odoo\odoo11\addons_adinfo\hubi\models  
        
        # General Settings
        company_id = self.env['res.company']._company_default_get('hubi.general_settings')
        val_company_id =company_id.id 
        val_name = 'General Settings'
        
        settings = self.env['hubi.general_settings'].search([('name','=', val_name), ('company_id','=', val_company_id)])
        if settings:
            auxiliary_account = settings.auxiliary_accounting
            length_account_gen = settings.length_account_general
            length_account_aux = settings.length_account_auxiliary
            complete_0_gen = settings.complete_0_account_general or False
            complete_0_aux = settings.complete_0_account_general or False
        else:
            auxiliary_account = False
            length_account_gen = 0
            length_account_aux = 0
            complete_0_gen = False
            complete_0_aux = False
        
        csv_path = self.path_account_transfer
        account_file = self.account_file_transfer
        writing_file = self.writing_file_transfer
            
        if csv_path is None:
           csv_path = os.environ.get('LOCALAPPDATA') or os.getcwd()          # c:\odoo\odoo11
        if account_file is None:   
            account_file = 'comptes.txt'
        if writing_file is None:    
            writing_file = 'ecritures.txt'
        
        """    
        csv_path = os.path.normpath(csv_path)    
        if not os.path.exists(csv_path): 
            os.makedirs(csv_path)
        os.chdir(csv_path)
        """
        
        # Account File
        partner_file = io.BytesIO()
        w_p = pycompat.csv_writer(partner_file, delimiter=',')

        #fpc = io.open(account_file, 'w', encoding='utf-8')
        
        csv_p = ""
        ligne_p = ""
        
        sql_p = """SELECT distinct am.partner_id, res_partner.name,
                res_partner.street, res_partner.city, res_partner.zip,
                res_country.code as code_pays, res_country.name as country,
                res_partner.phone, res_partner.mobile, am.company_id
                from account_move as am
                INNER JOIN res_partner on res_partner.id = am.partner_id 
                INNER JOIN res_country on res_country.id = res_partner.country_id 
                WHERE am.state = 'posted' 
                AND to_char(am.date,'YYYYMMDD') BETWEEN %s AND %s
                AND am.company_id = %s
                AND am.journal_id IN %s
                ORDER BY am.partner_id"""
                
        self.env.cr.execute(sql_p, (date_d,  date_f, val_company_id, tuple(self.journal_ids.ids),))
        
        ids_p = [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8]) for r in self.env.cr.fetchall()]
        for partner_id, name, street, city, zip, code_pays, country, phone, mobile in ids_p:
            ret_p = self.ecrire_ligne_comptes_ebp(auxiliary_account,length_account_gen,length_account_aux,complete_0_gen,complete_0_aux,partner_id, name, street, city, zip, code_pays, country, phone, mobile)
            
            ligne_p = ret_p['ligne_p']
            listrow_p = ret_p['listrow_p']
            listrow_ps = ret_p['listrow_ps']
            
            csv_p+= ligne_p
            w_p.writerow(listrow_p)
            if len(listrow_ps) !=0:
                w_p.writerow(listrow_ps)
                        
        #fpc.write(csv_p)
        #fpc.close()
        
        # Transfert Invoices
        compta_file = io.BytesIO()
        w = pycompat.csv_writer(compta_file, delimiter=',')
        
        #fpi = io.open(writing_file, 'w', encoding='utf-8')

        sql = """SELECT aml.id, am.name as move_name, account_journal.code as journal,account_account.code as compte,
                res_partner.name as partner, aml.name as move_line_name,
                to_char(am.date,'DDMMYYYY') as date_ecr,
                to_char(aml.date_maturity,'DDMMYYYY') as date_ech,
                aml.debit, aml.credit, res_currency.name as currency, 
                aml.ref as ref, aaa.code as compte_anal, am.partner_id, aml.company_id
                from account_move_line as aml
                INNER JOIN account_move as am on am.id = aml.move_id
                INNER JOIN account_journal on account_journal.id = am.journal_id
                INNER JOIN res_currency on res_currency.id = am.currency_id
                INNER JOIN res_partner on res_partner.id = am.partner_id 
                INNER JOIN account_account on account_account.id = aml.account_id 
                LEFT JOIN account_analytic_account as aaa on aaa.id = aml.analytic_account_id 
                WHERE am.state = 'posted' 
                AND to_char(am.date,'YYYYMMDD') BETWEEN %s AND %s
                AND  aml.company_id = %s 
                AND am.journal_id IN %s 
                AND aml.transfer_accounting is %s
                ORDER BY account_journal.code, am.id, account_account.code"""
                #AND aml.transfer_accounting is not true

        self.env.cr.execute(sql, (date_d,  date_f, val_company_id, tuple(self.journal_ids.ids),self.re_transfer,))
        
        nb_lig = 0
        csv = ""
        ligne = ""
        ids = [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13]) for r in self.env.cr.fetchall()]
        for line_id, move_name, journal, compte, partner_name, move_line_name, date_ecr, date_ech, debit, credit, currency, ref, compte_anal, partner_id in ids:
            nb_lig +=1
            listrow = list()
            #ligne = self.ecrire_ligne_ebp(auxiliary_account,length_account_gen,length_account_aux,complete_0_gen,complete_0_aux, move_name, journal, compte, partner_name, move_line_name, date_ecr, date_ech, debit, credit, currency, ref, compte_anal, partner_id, nb_lig)
            ret = self.ecrire_ligne_ebp(auxiliary_account,length_account_gen,length_account_aux,complete_0_gen,complete_0_aux, move_name, journal, compte, partner_name, move_line_name, date_ecr, date_ech, debit, credit, currency, ref, compte_anal, partner_id, nb_lig)
            ligne = ret['ligne']
            listrow = ret['listrow']
            
            csv+= ligne
            w.writerow(listrow)
            
            line = self.env['account.move.line'].browse(line_id)
            line.update({'transfer_accounting': True})

        #fpi.write(csv)
        #fpi.close()
        
        #controller_export_csv_order_line.SaleOrderController.transfert_compta_csv_download(self,csv,writing_file)  
        if self.mail_accounting:
            # send EMail
            #return self.send_mail_template()
            attachments_ids = []
            comptavalue = compta_file.getvalue()
            partnervalue = partner_file.getvalue()  
            if comptavalue is not None:
                attachment_w = {
                'name': ("%s" %writing_file),
                'datas_fname': writing_file,
                'datas': base64.encodestring(comptavalue),
                'type': 'binary'
                    }
                id_w = self.env['ir.attachment'].create(attachment_w)
                attachments_ids.append(id_w.id)
 
            if partnervalue is not None:
                attachment_a = {
                'name': ("%s" %account_file),
                'datas_fname': account_file,
                'datas': base64.encodestring(partnervalue),
                'type': 'binary'
                }
                id_a = self.env['ir.attachment'].create(attachment_a)  
                attachments_ids.append(id_a.id)
        
                email_template = self.env.ref('hubi.email_template_accounting_transfer')
                email_template.attachment_ids =  False
        
            email_template.attachment_ids = attachments_ids
        
            ir_model_data = self.env['ir.model.data']
            try:
                template_id = ir_model_data.get_object_reference('hubi', 'email_template_accounting_transfer')[1]
            except ValueError:
                template_id = False
            try:
                compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
            except ValueError:
                compose_form_id = False

            ctx = {
                'default_model': 'wiz.transfertcompta',
                'default_res_id': self.ids[0],
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'default_composition_mode': 'comment',
                'attachment_ids':  attachments_ids,
                'force_email': True
                }
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(compose_form_id, 'form')],
                'view_id': compose_form_id,
                'target': 'new',
                'context': ctx,
            }          
        
        
        
        else:
            #return {'type': 'ir.actions.act_window_close'}
            """
            view_id = self.env["ir.model.data"].get_object_reference("hubi", "wiz_transfert_compta_step2")
            self.message = ("%s %s %s %s") % ("Create Accounting transfer for ",nb_lig, " lines. Sur ", csv_path )
            return {"type":"ir.actions.act_window",
                "view_mode":"form",
                "view_type":"form",
                "views":[(view_id[1], "form")],
                "res_id":self.id,
                "target":"new",
                "res_model":"wiz.transfertcompta"                
                } 
                   
            """
            comptavalue = compta_file.getvalue()
            partnervalue = partner_file.getvalue()
            
            self.write({
                'compta_data': base64.encodestring(comptavalue),            
                'filename': writing_file,
                'partner_data': base64.encodestring(partnervalue),            
                'partner_filename': account_file,

            })
            compta_file.close()
            
            action_writing = {
                'name': 'hubi_transfert_compta',
                'type': 'ir.actions.act_url',
                'url': "web/content/?model=wiz.transfertcompta&id=" + str(self.id) + "&filename_field=filename&field=compta_data&download=true&filename=" + self.filename,
                'target': 'self',
                }
            action_partner = {
                'name': 'hubi_transfert_compta_partner',
                'type': 'ir.actions.act_url',
                'url': "web/content/?model=wiz.transfertcompta&id=" + str(self.id) + "&filename_field=partner_filename&field=partner_data&download=true&filename=" + self.partner_filename,
                'target': 'self',
                }
            action = {
                'name': 'hubi_transfert_compta',
                'type': 'ir.actions.act_url',
                'url': "web/content/?model=wiz.transfertcompta&id=" + str(self.id) + "&filename_field=filename&field=compta_data&download=true&filename=" + self.filename + "&filename_field=partner_filename&field=partner_data&download=true&filename=" + self.partner_filename,
                'target': 'self',
                }

            
            return action_writing
           
            
    @api.multi
    def transfert_compta_folder(self, **kw):  
        #s = s[ beginning : beginning + LENGTH]
        date_d =  self.date_start[0:4] + self.date_start[5:7] + self.date_start[8:10] 
        date_f =  self.date_end[0:4]+ self.date_end[5:7] + self.date_end[8:10] 
        query_args = {'date_start' : date_d,'date_end' : date_f}
        
        #dirpath2 = os.path.dirname(os.path.realpath(__file__))   # c:\odoo\odoo11\addons_adinfo\hubi\models  
        
        # General Settings
        company_id = self.env['res.company']._company_default_get('hubi.general_settings')
        val_company_id =company_id.id 
        val_name = 'General Settings'
        
        settings = self.env['hubi.general_settings'].search([('name','=', val_name), ('company_id','=', val_company_id)])
        if settings:
            auxiliary_account = settings.auxiliary_accounting
            length_account_gen = settings.length_account_general
            length_account_aux = settings.length_account_auxiliary
            complete_0_gen = settings.complete_0_account_general or False
            complete_0_aux = settings.complete_0_account_general or False
        else:
            auxiliary_account = False
            length_account_gen = 0
            length_account_aux = 0
            complete_0_gen = False
            complete_0_aux = False
        
        csv_path = self.path_account_transfer
        account_file = self.account_file_transfer
        writing_file = self.writing_file_transfer
            
        if csv_path is None:
           csv_path = os.environ.get('HOME') or os.getcwd()          # c:\odoo\odoo11
        if account_file is None:   
            account_file = 'comptes.txt'
        if writing_file is None:    
            writing_file = 'ecritures.txt'
            
        csv_path = os.path.normpath(csv_path)    
        if not os.path.exists(csv_path): 
            os.makedirs(csv_path)
        os.chdir(csv_path)
        
        # Tranfer Partners
        #lines = []
        #lines.append((['Account', 'Name', 'Name','Street', 'Zip','City','Country','Interloc','Phone','Mobile']))
        
        fpc = io.open(account_file, 'w', encoding='utf-8')
                
        #csv_p="{}\n".format("'Account', 'Name', 'Name','Street', 'Zip','City','Country','Interloc','Phone','Mobile'")
        #fpc.write(csv_p)
        
        csv_p = ""
        sql_p = """SELECT distinct am.partner_id, res_partner.name,
                res_partner.street, res_partner.city, res_partner.zip,
                res_country.code as code_pays, res_country.name as country,
                res_partner.phone, res_partner.mobile, am.company_id
                from account_move as am
                INNER JOIN res_partner on res_partner.id = am.partner_id 
                INNER JOIN res_country on res_country.id = res_partner.country_id 
                WHERE am.state = 'posted' 
                AND to_char(am.date,'YYYYMMDD') BETWEEN %s AND %s
                AND am.company_id = %s
                AND am.journal_id IN %s
                ORDER BY am.partner_id"""
                
        self.env.cr.execute(sql_p, (date_d,  date_f, val_company_id, tuple(self.journal_ids.ids),))
        
        ids_p = [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8]) for r in self.env.cr.fetchall()]
        for partner_id, name, street, city, zip, code_pays, country, phone, mobile in ids_p:
            ligne = self.ecrire_ligne_comptes_ebp(auxiliary_account,length_account_gen,length_account_aux,complete_0_gen,complete_0_aux,partner_id, name, street, city, zip, code_pays, country, phone, mobile)
            csv_p+= ligne
            
            #partner  = self.env['res.partner'].search([('id', '=',partner_id),  ])

            ## partner = Customer
            #account_customer_id = partner.property_account_receivable_id.id
            #account_customer  = self.env['account.account'].search([('id', '=',account_customer_id),  ])
            #account_gen_customer_code = account_customer.code
            #account_aux_customer_code = partner.auxiliary_account_customer or False
            
            ## partner = Supplier
            #account_supplier_id = partner.property_account_payable_id.id
            #account_supplier  = self.env['account.account'].search([('id', '=',account_supplier_id),  ])
            #account_gen_supplier_code = account_supplier.code
            #account_aux_supplier_code = partner.auxiliary_account_supplier or False
            
            #if auxiliary_account:
            #    account_customer_code = account_aux_customer_code
            #    account_supplier_code = account_aux_supplier_code
            #else:
            #    account_customer_code = account_gen_customer_code
            #    account_supplier_code = account_gen_supplier_code 
            #    if length_account_gen != 0:
            #        if (complete_0_gen):
            #            account_customer_code = account_customer_code.ljust(length_account_gen,'0')
            #            account_supplier_code = account_supplier_code.ljust(length_account_gen,'0')
            #        else:    
            #            account_customer_code = account_customer_code[0:length_account_gen]
            #            account_supplier_code = account_supplier_code[0:length_account_gen]
                    
            #interloc = ""
            #f_name =""
            #f_street =""
            #f_zip =""
            #f_city =""
            #f_country =""
            #f_phone =""
            #f_mobile = ""
                
            #if name:
            #    f_name = name[0:60].replace(',', ' ') 
            #    f_name = tools_hubi.replace_accent(self, f_name)
                     
            #if street:
            #    f_street = street[0:100].replace(',', ' ')
            #if zip:
            #    f_zip = zip[0:5]
            #if city:
            #    f_city = city[0:30].replace(',', ' ') 
            #if country:
            #    f_country = country[0:35]           
            #if phone:
            #    f_phone = phone[0:20].replace(',', ' ')
            #if mobile:
            #    f_mobile = mobile[0:20].replace(',', ' ') 
            
            #if account_customer_code and partner.customer:
            #    csv_p_row = ""
            #    csv_p_row+= "{},".format(account_customer_code[0:15])
            #    csv_p_row+= "{},".format(f_name[0:60])
            #    csv_p_row+= "{},".format(f_name[0:30])
            #    csv_p_row+= "{},".format(f_street[0:100])
            #    csv_p_row+= "{},".format(f_zip[0:5])
            #    csv_p_row+= "{},".format(f_city[0:30])
            #    csv_p_row+= "{},".format(f_country[0:35])
            #    csv_p_row+= "{},".format(interloc)
            #    csv_p_row+= "{},".format(f_phone[0:20])
            #    csv_p_row+= "{},".format(f_mobile[0:20])
           
            #    csv_p+="{}\n".format(csv_p_row[:-1])
            #    #lines.append(([account_customer_code[0:15], f_name[0:60], f_name[0:30], f_street[0:100], f_zip[0:5], f_country[0:35], interloc, f_phone[0:20], f_mobile[0:20]  ]))

            #if account_supplier_code and partner.supplier:
            #    csv_p_row = ""
            #    csv_p_row+= "{},".format(account_supplier_code[0:15])
            #    csv_p_row+= "{},".format(f_name[0:60])
            #    csv_p_row+= "{},".format(f_name[0:30])
            #    csv_p_row+= "{},".format(f_street[0:100])
            #    csv_p_row+= "{},".format(f_zip[0:5])
            #    csv_p_row+= "{},".format(f_city[0:30])
            #    csv_p_row+= "{},".format(f_country[0:35])
            #    csv_p_row+= "{},".format(interloc)
            #    csv_p_row+= "{},".format(f_phone[0:20])
            #    csv_p_row+= "{},".format(f_mobile[0:20])
           
            #    csv_p+="{}\n".format(csv_p_row[:-1])
                #lines.append(([account_supplier_code[0:15], f_name[0:60], f_name[0:30], f_street[0:100], f_zip[0:5], f_country[0:35], interloc, f_phone[0:20], f_mobile[0:20]  ]))
                        
        fpc.write(csv_p)
                
        fpc.close()
        
        #fp = io.open('comptes_odoo.csv', 'w', encoding='utf-8') 
        #with misc.file_open('hubi/csv/comptes_odoo.csv', 'w') as fp:
        #    writer = pycompat.csv_writer(fp, delimiter=',')
        #    data_lines = lines
        #    writer.writerow(data_lines)        

        #with open('comptes_odoo.csv', 'w') as fp:
        #    a = pycompat.csv_writer(fp, delimiter=',')            
        #    data_lines = lines
        #    a.writerows(data_lines)
        
        #output = io.BytesIO()
        #writer = pycompat.csv_writer(output, quoting=1)
        #data_lines = lines
        #writer.writerow(data_lines)

#        import_wizard = self.env['base_import.import'].create({
#            'res_model': 'base_import.tests.models.preview',
#            'file': output.getvalue(),
#            'file_type': 'text/csv',
#        })
#        data, _ = import_wizard._convert_import_data(
#            ['name', 'somevalue'],
#            {'quoting': '"', 'separator': ',', 'headers': True}
#        )

        #self.assertItemsEqual(data, [data_row])
        
        # Transfert Invoices
        fpi = io.open(writing_file, 'w', encoding='utf-8')

        sql = """SELECT aml.id, am.name as move_name, account_journal.code as journal,account_account.code as compte,
                res_partner.name as partner, aml.name as move_line_name,
                to_char(am.date,'DDMMYYYY') as date_ecr,
                to_char(aml.date_maturity,'DDMMYYYY') as date_ech,
                aml.debit, aml.credit, res_currency.name as currency, 
                aml.ref as ref, aaa.code as compte_anal, am.partner_id, aml.company_id
                from account_move_line as aml
                INNER JOIN account_move as am on am.id = aml.move_id
                INNER JOIN account_journal on account_journal.id = am.journal_id
                INNER JOIN res_currency on res_currency.id = am.currency_id
                INNER JOIN res_partner on res_partner.id = am.partner_id 
                INNER JOIN account_account on account_account.id = aml.account_id 
                LEFT JOIN account_analytic_account as aaa on aaa.id = aml.analytic_account_id 
                WHERE am.state = 'posted' 
                AND to_char(am.date,'YYYYMMDD') BETWEEN %s AND %s
                AND  aml.company_id = %s 
                AND am.journal_id IN %s 
                AND aml.transfer_accounting is %s
                ORDER BY account_journal.code, am.id, account_account.code"""
                #AND aml.transfer_accounting is not true

        self.env.cr.execute(sql, (date_d,  date_f, val_company_id, tuple(self.journal_ids.ids),self.re_transfer,))
        #self.env.cr.execute(sql, query_args)
        
        nb_lig = 0
        csv = ""
        ids = [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13]) for r in self.env.cr.fetchall()]
        for line_id, move_name, journal, compte, partner_name, move_line_name, date_ecr, date_ech, debit, credit, currency, ref, compte_anal, partner_id in ids:
            nb_lig +=1
            ligne = self.ecrire_ligne_ebp(auxiliary_account,length_account_gen,length_account_aux,complete_0_gen,complete_0_aux, move_name, journal, compte, partner_name, move_line_name, date_ecr, date_ech, debit, credit, currency, ref, compte_anal, partner_id, nb_lig)
            csv+= ligne

            line = self.env['account.move.line'].browse(line_id)
            line.update({'transfer_accounting': True})

            """
            
            libelle = ""
            n_piece=""
            
            if length_account_gen != 0:  
                if (complete_0_gen):
                    compte_gen = compte.ljust(length_account_gen,'0')
                        
                else:    
                    compte_gen=compte[0:length_account_gen] 
               
            partner  = self.env['res.partner'].search([('id', '=',partner_id),  ])

            # partner = Customer
            account_customer_id = partner.property_account_receivable_id.id
            account_customer  = self.env['account.account'].search([('id', '=',account_customer_id),  ])
            account_gen_customer_code = account_customer.code
            account_aux_customer_code = partner.auxiliary_account_customer or False
            
            # partner = Supplier
            account_supplier_id = partner.property_account_payable_id.id
            account_supplier  = self.env['account.account'].search([('id', '=',account_supplier_id),  ])
            account_gen_supplier_code = account_supplier.code
            account_aux_supplier_code = partner.auxiliary_account_supplier or False
            
            if (compte_gen == account_gen_customer_code ) or (compte_gen == account_gen_supplier_code):
                if auxiliary_account:
                    if (compte_gen == account_gen_customer_code) and (account_aux_customer_code):
                        compte_gen = account_aux_customer_code
                    if (compte_gen == account_gen_supplier_code) and (account_aux_supplier_code):
                        compte_gen == account_aux_supplier_code
            
            if move_line_name =="/":
                if partner_name:
                    libelle = partner_name
            else:
                if move_line_name:
                    libelle = move_line_name  
                    
            libelle = libelle.replace(',', '.') 
            libelle = tools_hubi.replace_accent(self, libelle)
                             
            if move_name:
                n_piece = move_name
                    
            if debit == 0:
                montant = credit
                sens = "C"
            else:         
                montant = debit
                sens = "D"
            type_tva = "" 
            
            csv_row = ""
            csv_row+= "{},".format(nb_lig)
            csv_row+= "{},".format(date_ecr)
            csv_row+= "{},".format(journal)
            csv_row+= "{},".format(compte_gen[0:15])
            csv_row+= "{},".format(libelle[0:40])
            csv_row+= "{},".format(libelle[0:40])
            csv_row+= "{},".format(n_piece[-10:])
            csv_row+= "{0:.2f},".format(montant)
            csv_row+= "{},".format(sens)
            csv_row+= "{},".format(date_ech)
            csv_row+= "{},".format(type_tva)
            csv_row+= "{},".format(currency)
            
            csv+="{}\n".format(csv_row[:-1])
            
            #Analytique
            pourc="100.00"
            if compte_anal:
               csv_row = ">"
               csv_row+= "{},".format(compte_anal) 
               csv_row+= "{},".format(pourc)
               csv_row+= "{},".format(montant)
               
               csv+="{}\n".format(csv_row[:-1])
            """
            
        fpi.write(csv)
        fpi.close()
        
        #controller_export_csv_order_line.SaleOrderController.transfert_compta_csv_download(self,csv,writing_file)  
        if self.mail_accounting:
            return self.send_mail_template()  
        else:
            #return {'type': 'ir.actions.act_window_close'}
            view_id = self.env["ir.model.data"].get_object_reference("hubi", "wiz_transfert_compta_step2")
            self.message = ("%s %s %s") % ("Create Accounting transfer for ",nb_lig, " lines. ")
            return {"type":"ir.actions.act_window",
                "view_mode":"form",
                "view_type":"form",
                "views":[(view_id[1], "form")],
                "res_id":self.id,
                "target":"new",
                "res_model":"wiz.transfertcompta"                
                }        



    @api.multi
    def send_mail_template_old(self):   
    # Find the e-mail template
 #       template = self.env.ref('hubi.Accounting_transfer')
        # You can also find the e-mail template like this:
        # template = self.env['ir.model.data'].get_object('mail_template_demo', 'example_email_template')
 
        # Send out the e-mail template to the user
 #       self.env['mail.template'].browse(template.id).send_mail(self.id)
        
        
        ##su_id = self.env['res.partner'].browse(SUPERUSER_ID)
        #template_id = self.env['ir.model.data'].get_object_reference('hubi',
        #                                                             'Accounting_transfer')[1]
        
        template_id = self.template_id.id
        template_browse = self.env['mail.template'].browse(template_id).send_mail(self.id)
        """
        #email_to = self.env['hr.employee'].browse(emp_id).work_email
        email_to ="isabelle.pasquet@groupeadinfo.com"
        email_from ="isabelle.pasquet@groupeadinfo.com"
        
        if template_browse:
             values = template_browse.generate_email(emp_id, fields=None)
             values['email_to'] = email_to
             values['email_from'] = email_from  #su_id.email
             values['res_id'] = False
             if not values['email_to'] and not values['email_from']:
                 pass
             
             mail_mail_obj = self.env['mail.mail']
             msg_id = mail_mail_obj.create(values)
             if msg_id:
                 mail_mail_obj.send(msg_id)
        """  

class HubiAccountMoveLine(models.Model):
    _inherit = "account.move.line"

    transfer_accounting = fields.Boolean(string='Transfer Accounting', default=False) 

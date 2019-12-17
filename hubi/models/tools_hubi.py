# -*- coding: utf-8 -*-

from odoo import models, fields, api
from ..controllers import ctrl_print

#@api.model
def _default_is_Visible_class(self, valeur): 
    retour = False
    option=self.env['hubi.module_option']

    check_opt=option.search([('name','=', valeur),('company_id','=', self.company_id.id)])
    for check in check_opt:
        retour = check.state
    return retour

#@api.one
def _is_Visible_class(self, origin):
    # Product
    if origin == 'Product':
            self.is_fonction_deporte = False
            self.is_etiquette = False
            self.is_etiq_marenne = False
            self.is_etiq_prod_edition = False
            self.is_etiq_prod_libelle = False
            self.is_etiq_prod_lib_espagnol = False
            self.is_etiq_prod_lib_latin = False 
        
    if origin == 'Product' or origin == 'PriceList' :   
            self.is_etiq_format = False
        
            self.is_tarif_option = False
            self.is_tarif_code_interne = False
            self.is_tarif_ref_client = False
            self.is_tarif_lib_promo = False     

    # Partner
    if origin == 'Partner' :
            self.is_frs = False
            self.is_edi_facture = False
            self.is_edi_transporteur = False
            self.is_bl_valorise = False
            self.is_etiq_lot_auto = False
            self.is_prix_kg = False
            self.is_type_tiers = False
            self.is_etiq_dlc = False
            self.is_etiq_couleur_client = False
            self.is_etiq_ean_128 = False
            ##self.is_etiq_mode = False
            self.is_etiq_type = False
            self.is_export_compta = False
            self.is_fonction_deporte = False
            self.is_regr_prod_fac = False                                                         
       

    if origin == 'Partner' or origin == 'PriceList' :
            self.is_ifls = False
       
    self.is_etiq_mode = False  
             
    option=self.env['hubi.module_option']
         
    check_opt=option.search([('name','=','ETIQ_MODE'),('company_id','=', self.company_id.id)])
    for check in check_opt:
        self.is_etiq_mode = check.state 

    # Product
    if origin == 'Product':
            check_opt=option.search([('name','=','FONCTION_DEPORTE'),('company_id','=', self.company_id.id)])
            for check in check_opt:
                self.is_fonction_deporte = check.state  
            check_opt=option.search([('name','=','ETIQUETTE'),('company_id','=', self.company_id.id)])
            for check in check_opt:
                self.is_etiquette = check.state 
            
            check_opt=option.search([('name','=','ETIQ_MARENNE'),('company_id','=', self.company_id.id)])
            for check in check_opt:
                self.is_etiq_marenne = check.state 
            
            check_opt=option.search([('name','=','ETIQ_PROD_EDITION'),('company_id','=', self.company_id.id)])
            for check in check_opt:
                self.is_etiq_prod_edition = check.state 
            
            check_opt=option.search([('name','=','ETIQ_PROD_LIBELLE'),('company_id','=', self.company_id.id)])
            for check in check_opt:
                self.is_etiq_prod_libelle = check.state 
            
            check_opt=option.search([('name','=','ETIQ_PROD_LIB_ESPAGNOL'),('company_id','=', self.company_id.id)])
            for check in check_opt:
                self.is_etiq_prod_lib_espagnol = check.state 
            
            check_opt=option.search([('name','=','ETIQ_PROD_LIB_LATIN'),('company_id','=', self.company_id.id)])
            for check in check_opt:
                self.is_etiq_prod_lib_latin = check.state   

    if origin == 'Product' or origin == 'PriceList' :
            check_opt=option.search([('name','=','ETIQ_FORMAT'),('company_id','=', self.company_id.id)])
            for check in check_opt:
                self.is_etiq_format = check.state 

            check_opt=option.search([('name','=','TARIF_OPTION'),('company_id','=', self.company_id.id)])
            for check in check_opt:
                self.is_tarif_option = check.state 
            
            check_opt=option.search([('name','=','TARIF_CODE_INTERNE'),('company_id','=', self.company_id.id)])
            for check in check_opt:
                self.is_tarif_code_interne = check.state 
                        
            check_opt=option.search([('name','=','TARIF_REF_CLIENT'),('company_id','=', self.company_id.id)])
            for check in check_opt:
                self.is_tarif_ref_client = check.state 

            check_opt=option.search([('name','=','TARIF_LIB_PROMO'),('company_id','=', self.company_id.id)])
            for check in check_opt:
                self.is_tarif_lib_promo = check.state  

    # Partner
    if origin == 'Partner' or origin == 'PriceList' :
            check_opt=option.search([('name','=','GESTION_IFLS'),('company_id','=', self.company_id.id)])
            for check in check_opt:
                self.is_ifls = check.state

    if origin == 'Partner' :
            check_opt=option.search([('name','=','REF_FRS'),('company_id','=', self.company_id.id)])
            for check in check_opt:
                self.is_frs = check.state
            check_opt=option.search([('name','=','EDI_FACTURE'),('company_id','=', self.company_id.id)])
            for check in check_opt:
                self.is_edi_facture = check.state
            check_opt=option.search([('name','=','EDI_TRANSPORTEUR'),('company_id','=', self.company_id.id)])
            for check in check_opt:
                self.is_edi_transporteur = check.state
            check_opt=option.search([('name','=','BL_VALORISE'),('company_id','=', self.company_id.id)])
            for check in check_opt:
                self.is_bl_valorise = check.state
            check_opt=option.search([('name','=','ETIQ_LOT_AUTO'),('company_id','=', self.company_id.id)])
            for check in check_opt:
                self.is_etiq_lot_auto = check.state
            check_opt=option.search([('name','=','PRIX_KG'),('company_id','=', self.company_id.id)])
            for check in check_opt:
                self.is_prix_kg = check.state
            check_opt=option.search([('name','=','TYPE_TIERS'),('company_id','=', self.company_id.id)])
            for check in check_opt:
                self.is_type_tiers = check.state
            check_opt=option.search([('name','=','ETIQ_DLC'),('company_id','=', self.company_id.id)])
            for check in check_opt:
                self.is_etiq_dlc = check.state
            check_opt=option.search([('name','=','ETIQ_COULEUR_CLIENT'),('company_id','=', self.company_id.id)])
            for check in check_opt:
                self.is_etiq_couleur_client = check.state
            check_opt=option.search([('name','=','ETIQ_EAN_128'),('company_id','=', self.company_id.id)])
            for check in check_opt:
                self.is_etiq_ean_128 = check.state
            check_opt=option.search([('name','=','ETIQ_TYPE'),('company_id','=', self.company_id.id)])
            for check in check_opt:
                self.is_etiq_type = check.state                                                                                                                                    
            check_opt=option.search([('name','=','EXPORT_COMPTA'),('company_id','=', self.company_id.id)])
            for check in check_opt:
                self.is_export_compta = check.state  
            check_opt=option.search([('name','=','FONCTION_DEPORTE'),('company_id','=', self.company_id.id)])
            for check in check_opt:
                self.is_fonction_deporte = check.state  
            check_opt=option.search([('name','=','REGR_PROD_FAC'),('company_id','=', self.company_id.id)])
            for check in check_opt:
                self.is_regr_prod_fac = check.state      
                    
def calcul_cle_code_ean13(self, ean):
    # Calcul cle code ean13
    somme = 0
    coeff = "131313131313"

    for i in range(0,12):
        somme = somme + int(ean[i])*int(coeff[i])

    reste = somme % 10
    if reste == 0:
        cle = 0
    else: 
        cle = 10 - reste
        
    return "%s" % (cle) 

def replace_accent(self,s):
    if s:
        s = s.replace('ê', 'e') \
             .replace('è', 'e') \
             .replace('é', 'e') \
             .replace('à', 'a') \
             .replace('ô', 'o') \
             .replace('ö', 'o') \
             .replace('î', 'i')
    return s                 
                      
def left(aString, howMany):
    if howMany <1:
        return ''
    else:
        return aString[:howMany]

def right(aString, howMany):
    if howMany <1:
        return ''
    else:
        return aString[-howMany:]

def mid(aString, startChar, howMany):
    if howMany < 1:
        return ''
    else:
        return aString[startChar:startChar+howMany]
    
#@api.model
def prepareprintlabel(self, nom_table, id_table):
        #FP20190318 Remplacement l.file par l.text et sl.pds par case ...sl.pds / sl.qte end
        query = """SELECT to_char(sl.packaging_date,'DD/MM/YYYY'), to_char(sl.sending_date,'DD/MM/YYYY'), 
                    pt.etiq_description, pc.complete_name, 
                    hfc.name, hfp.name, pt.etiq_mention, 
                    sl.code_barre, sl.code_128, sl.qte,  
                    case sl.qte when 0 then sl.pds else sl.pds/sl.qte end,
                    sl.nb_mini, p.realname, p.adressip,l.text,
                    t.customer_name_etiq, t.customer_city_etiq, 
                    etab.health_number, etab.company_name_etiq, etab.company_city_etiq, etab.etiq_mention,
                    sl.numlot, sl.color_etiq, pt.etiq_latin, pt.etiq_spanish, pt.name, 
                    l.with_ean128, etab.compteur_ean128, etab.id, dc.name,
                    t.statistics_alpha_1, t.statistics_alpha_2,t.statistics_alpha_3,t.statistics_alpha_4,t.statistics_alpha_5,
                    pt.statistics_alpha_1, pt.statistics_alpha_2,pt.statistics_alpha_3,pt.statistics_alpha_4,pt.statistics_alpha_5
                    , pt.etiq_country1, pt.etiq_country2, sl.date_dluo
                    FROM """ + nom_table + """ sl
                    LEFT JOIN hubi_printer p ON sl.printer_id = p.id 
                    LEFT JOIN hubi_labelmodel l ON sl.label_id = l.id
                    INNER JOIN res_partner t ON t.id = sl.partner_id
                    LEFT JOIN res_partner etab ON etab.id = sl.etabexp_id
                    INNER JOIN product_product prod ON prod.id = sl.product_id
                    INNER JOIN product_template pt ON prod.product_tmpl_id = pt.id
                    INNER JOIN product_category pc ON pt.categ_id = pc.id 
                    LEFT JOIN hubi_family AS hfc ON pt.caliber_id = hfc.id 
                    LEFT JOIN hubi_family AS hfp ON pt.packaging_id = hfp.id 
                    LEFT JOIN delivery_carrier as dc on sl.carrier_id = dc.id 

                    WHERE sl.id=""" + str(id_table)
                    #t.statistics_num_1, t.statistics_num_2,t.statistics_num_3,t.statistics_num_4,t.statistics_num_5,
                    #pt.statistics_num_1, pt.statistics_num_2,pt.statistics_num_3,pt.statistics_num_4,pt.statistics_num_5

        self.env.cr.execute(query)
        
        result = [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], \
                    r[11], r[12], r[13], r[14], r[15], r[16], r[17], r[18], r[19], r[20], \
                    r[21], r[22], r[23], r[24], r[25], r[26], r[27], r[28], r[29], r[30], \
                    r[31], r[32], r[33], r[34], r[35], r[36], r[37], r[38], r[39], r[40], r[41], r[42]) \
                  for r in self.env.cr.fetchall()]
        
        for packaging_date,sending_date,product_description,category_name,caliber_name,packaging_name,etiq_mention,code_barre,code128,qte, pds, \
        nb_mini,printerName,adressip,labelFile,clientname1,clientname2,numsanitaire,etabexp1,etabexp2,etab_mention,\
        lot,color,etiq_latin, etiq_spanish,product_name,with_ean128,compteur_ean128, etab_id, carrier_name, c_st1, \
        c_st2, c_st3, c_st4, c_st5, p_st1, p_st2, p_st3, p_st4, p_st5,etiq_country1,etiq_country2, date_dluo in result:
            if (product_description is not None):
                description_item = product_description
            else:
                description_item = category_name  
                
            if (etiq_mention is not None):
                mention_item = etiq_mention
            else:
                mention_item = etab_mention  
                
            informations = [
                ("dateemb",packaging_date),
                ("dateexp",sending_date),
                ("produit",description_item),
                ("calibre",caliber_name),
                ("conditionnement",packaging_name),
                ("mention",mention_item),
                ("latin",etiq_latin),
                ("spanish",etiq_spanish),
                ("codebarre",code_barre),
                ("codeb128",code128),
                ("qte",int(qte)),
                ("pds",pds),
                ("nb",int(nb_mini)),
                ("numsanitaire",numsanitaire),
                ("client1", clientname1),
                ("client2", clientname2),
                ("etab1", etabexp1),
                ("etab2", etabexp2),
                ("lot", lot),
                ("color", color),
                ("date_dlc", date_dluo),
                
                ("sale_packaging_date",packaging_date),
                ("sale_sending_date",sending_date),
                ("saleline_qty",int(qte)),
                ("saleline_weight",pds),
                ("saleline_no_lot", lot),
                
                ("product_produit",description_item),
                ("product_caliber_name",caliber_name),
                ("product_packaging_name",packaging_name),
                ("product_etiq_mention",mention_item),
                ("product_etiq_latin",etiq_latin),
                ("product_etiq_spanish",etiq_spanish),
                ("product_etiq_country1",etiq_country1),
                ("product_etiq_country2",etiq_country2),
                ("product_barcode",code_barre),
                ("product_barcode128",code128),
                ("product_nbmini",int(nb_mini)),
                ("product_stat1", p_st1),
                ("product_stat2", p_st2),
                ("product_stat3", p_st3),
                ("product_stat4", p_st4),
                ("product_stat5", p_st5),
                
                ("customer_etiq_name", clientname1),
                ("customer_etiq_city", clientname2),
                ("customer_carrier_name", carrier_name),
                ("customer_stat1", c_st1),
                ("customer_stat2", c_st2),
                ("customer_stat3", c_st3),
                ("customer_stat4", c_st4),
                ("customer_stat5", c_st5),
                
                ("etab_health_number",numsanitaire),
                ("etab_etiq_name", etabexp1),
                ("etab__etiq_city", etabexp2),
                
                
                
                ]
            
            if(printerName is not None and printerName != "" and labelFile is not None and labelFile != ""):
                printer = printerName
                #FP20190318 if (adressip is not None and adressip != ""):
                #    printer = "\\\\" + adressip + "\\" + printerName
                #else:
                #    printer = printerName
                    
                ctrl_print.printlabelonwindows(self,printer,labelFile,'[',informations)   

                # Update counter of barcode 128
                if with_ean128:
                    if compteur_ean128:
                        compteur_ean128 += 1
                    else:
                        compteur_ean128 = 2    
                    req = """UPDATE res_partner SET compteur_ean128=%s  where id=%s"""
        
                    params = (compteur_ean128, etab_id)
                    self._cr.execute(req,params)
                    self.env.cr.commit()
    
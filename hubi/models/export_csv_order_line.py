# -*- coding: utf-8 -*-
import csv, sys
from odoo import api, fields, models, _
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception,content_disposition

from . import controller_export_csv_order_line

class sale_order_export_line(models.Model):
    _inherit = 'sale.order'
    _auto = False

    #@http.route('/csv/download/sale_order/<int:order_id>/partner_name/<string:partner_name>', auth='user')
    def sale_order_lines_csv(self, **kw):
        
        order_id = self.id
        partner_name = self.partner_id.name
        #controller_export_csv_order_line.sale_order_lines_csv_download(self,order_id,partner_name,**kw)
        controller_export_csv_order_line.SaleOrderController.sale_order_lines_csv_download(self,order_id,partner_name,**kw)
    #    if partner_name:
    #        csv = http.request.env['sale.order']._csv_download({'order_id': order_id, 'partner_name':partner_name})
    #    else:
    #        csv = http.request.env['sale.order']._csv_download({'order_id': order_id, 'partner_name': False})
    #    filename = 'order_lines_%s_%s.csv'%(order_id,partner_name)

    #    return request.make_response(csv,
    #                                    [('Content-Type', 'application/octet-stream'),
    #                                     ('Content-Disposition', 'attachment; filename="%s"'%(filename))])

    #@api.multi
    def export_lines_to_csv(self):
        return {
            'type' : 'ir.actions.act_url',
            'url': '/csv/download/sale_order/%s/partner_name/%s'%(self.id,'American'),
            'target': 'blank',
        }

    #@api.model
    def _csv_download_data(self,vals):
        order_id = vals.get('order_id')
        partner_name = vals.get('partner_name')

        so = self.env['sale.order'].browse(order_id)
        lines = so.order_line.search([('order_id','=',order_id),('partner_name','ilike',partner_name)])
        
        colonnes = ['Numero_pedido_Dentaltix','Nombre_client','Diretion', 'Code_postal', 'Poblacion','Provincia', 'Pays', 'Téléphone', 'Horario_entrega''Reference', 'Cantidad', 'Envio']
		#colonnes = ['Numero_pedido_Dentaltix','Nombre_client','Diretion', 'Code_postal', 'Poblacion','Provincia', 'Pays', 'Téléphone', 'Horario_entrega', 'Reference', 'Cantidad', 'Envio']
        csv = u','.join(colonnes)
        csv += "\n"

        if len(lines) > 0:
            for ol in lines:
                order_name = so.name if so.name else ''
                client_notes = so.client_notes if so.client_notes else ''
                partner = ol.partner_id if ol.partner_id else ''
                picking_policy = DELIVERY_METHODS[so.picking_policy] if so.picking_policy else 'Directo'
                product_uos_qty = str(int(ol.product_uos_qty)) if ol.product_uos_qty else '0'

                csv_row = u'","'.join(data)
                csv += u"\"{}\"\n".format(csv_row)

        return csv
	
    #@api.model
    def _csv_download(self,vals):
        #query_args = {'id': self.id}
        query_args = {'id': vals['order_id']}
        sql = """SELECT 
                 quote_nullable(name),
                 quote_nullable(date_order),
                 quote_nullable(partner_id),
                 quote_nullable(amount_total)
             FROM
                 sale_order
             WHERE id=%(id)s""" 
        self.env.cr.execute(sql, query_args)
        rows = self.env.cr.fetchall()
        csv = """'Name','Date','Partner','Amount'\n"""
        if rows:
            for row in rows:
                csv_row = ""
                for item in row:
                    csv_row+= "{},".format(item)
                csv+="{}\n".format(csv_row[:-1])
                
        return csv 
     
    def _get_csv_url(self):
        self.csv_url = "/csv/download/{}/".format(self.id)
         

    csv_url = fields.Char(compute=_get_csv_url)
    
    #    sql = """SELECT 
    #             quote_nullable(field_1),
    #             quote_nullable(field_2),
    #             quote_nullable(field_3),
    #             quote_nullable(field_4)
    #         FROM
    #             table_name
    #         WHERE id={}""".format(vals.get(rec_id)) 
    
class SaleOrderController2(http.Controller):
    @http.route('/csv/download/sale_order/<int:order_id>/partner_name/<string:partner_name>', auth='user')
    def sale_order_lines_csv_download2(self, order_id, partner_name, **kw):
        if partner_name:
            csv = http.request.env['sale.order']._csv_download({'order_id': order_id, 'partner_name':partner_name})
        else:
            csv = http.request.env['sale.order']._csv_download({'order_id': order_id, 'partner_name': False})
        filename = 'order_lines_%s_%s.csv'%(order_id,partner_name)

        return request.make_response(csv,
                                        [('Content-Type', 'application/octet-stream'),
                                         ('Content-Disposition', 'attachment; filename="%s"'%(filename))])


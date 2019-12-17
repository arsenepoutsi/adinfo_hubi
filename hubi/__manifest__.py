# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'hubi',
    'version': '1.0',
    'summary': 'hubi',
    'category': 'HUBI',
    'author': 'MIADI',
    'description': """
Gestion HUBI
""",

    'depends': ['base', 'base_setup', 'product', 'mail', 'hubi_bom', 'sale', 'delivery', 'web'],

    'data': ["data/hubi_template_email.xml",

             "views/module_option_views.xml",
             "wizard/wiz_confirm_dialog_views.xml",
             "views/shipper_views.xml",
             "views/table_base_views.xml",
             "views/inherited_partner_views.xml",
             "views/inherited_product_template_views.xml",
             "views/inherited_mrp_bom_views.xml",
             "wizard/wiz_create_productprice_views.xml",
             "wizard/wiz_search_product_views.xml",
             "views/inherited_product_pricelist_views.xml",
             "views/inherited_sale_order_views.xml",
             "views/palletization_views.xml",
             "views/inherited_account_invoice_views.xml",
             "views/inherited_account_payment_views.xml",
             "views/inherited_delivery_carrier_views.xml",
             "views/inherited_packing_preparation_views.xml",
             "views/invoice_stock_move_view.xml",
             # "views/inherited_account_view.xml",
             "reports/account_invoice_report_views.xml",
             "reports/sale_order_report_views.xml",
             "wizard/wiz_inherited_sale_advance_payment_views.xml",
             "wizard/wiz_create_product_from_category_views.xml",
             "wizard/wiz_create_creditnote_ca_views.xml",
             "views/parameter_views.xml",
             "views/printer_views.xml",
             "wizard/wiz_sale_order_print_label_views.xml",
             "wizard/wiz_print_label_sale.xml",
             "wizard/wiz_create_print_label_views.xml",
             "wizard/wiz_print_label.xml",
             "wizard/wiz_transfert_compta_views.xml",
             "wizard/wiz_general_settings_views.xml",
             "views/label_model_views.xml",
             "miadi_etiquette_menu.xml",

             "views/send_email_views.xml",
             "views/inherited_mail_message_view.xml",
             # "views/web_send_email_views.xml",
             "views/web_export_view_view.xml",

             "hubi_menu.xml",
             "reports/partner_list_report.xml",
             "reports/partner_sheet_report.xml",
             "reports/productprice_sheet_report.xml",
             "reports/sale_order_hubi_report.xml",
             "reports/account_invoice_summary_report.xml",
             "reports/account_invoice_hubi_report.xml",
             "reports/sale_carrier_report.xml",
             "reports/hubi_reports.xml",
             "security/hubi_security.xml",
             "security/ir.model.access.csv"

             ],
    'images': [
        'static/src/img/main_1.png',
        'static/src/img/main_2.png',
        'static/src/img/main_screenshot.png'
    ],
    'demo': [  # "data/res.country.state.csv",

        # "data/hubi.module_option.csv",
        # "data/hubi.payment_mode.csv",

        # "data/hubi.family.csv",
        # "data/product.category.csv",
        # "data/res.partner.category.csv",

        # "data/hubi.labelmodel.csv",
        # "data/hubi.printer.csv",
        # "data/hubi.parameter.csv",

        # "data/product_pricelist_demo.xml",
        # "data/product.pricelist.csv",
        # "data/res.partner.title.csv",
        # "data/res.partner.csv",
        # "data/product.template.csv"

    ],

    'qweb': [  # 'static/src/xml/web_send_email_template.xml',
        "static/src/xml/web_export_view_template.xml",
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

# -*- coding: utf-8 -*-


{
    'name': 'hubi BOM',
    'version': '1.0',
    'category': 'hubi BOM',
    'author': 'MIADI',
    'sequence': 14,
    'summary': 'Bill of Materials for HUBI',
    'depends': ['product', 'stock'],
    'description': "Module la gestion des nomenclatures Hubi",
    'data': [
        # 'security/mrp_security.xml',
        # 'security/ir.model.access.csv',
        'data/mrp_data.xml',
        'views/mrp_views_menus.xml',
        'views/mrp_bom_views.xml',
        'views/product_views.xml',
        #'views/mrp_templates.xml',
        # 'report/mrp_report_views_main.xml',
        # 'report/mrp_bom_structure_report_templates.xml',
        # 'report/mrp_bom_cost_report_templates.xml',
    ],
    'application': False,

    'installable': True,
    'auto_install': False,
}

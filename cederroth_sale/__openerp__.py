{
    "name" : "Sale for CEDERROTH",
    "version" : "0.1 ",
    "author" : "Marcin Bereda, Via IT Solutions",
    "website" : "http://www.viait.pl/",
    "category" : "Added functionality - Sale",
    "depends" : ['cederroth_products'],
    'data': ['security/cd_security.xml',
             'security/ir.model.access.csv'
             ],

    "description": """
                    This module is dedicated to CEDERROTH needs
                    """,
    "init_xml": [],
    "update_xml": ['data/cd_promotions_stage_data.xml',
                   'wizard/cd_product_rel_add_wizard_view.xml',
                   'view/cd_promotions_view.xml',
                   'view/res_partner_view.xml',
                   'view/product_view.xml',
                   'view/crm_view.xml',
                   'view/cd_cost_data_view.xml',
                   'view/cd_type_promotions_view.xml',
                   'view/cd_email_template.xml'
                   ],
    "installable": True,
    "active": False,
}
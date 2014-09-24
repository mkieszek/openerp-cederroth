{
    "name" : "Planning for CEDERROTH",
    "version" : "0.1 ",
    "author" : "Marcin Bereda, Via IT Solutions",
    "website" : "http://www.viait.pl/",
    "category" : "Added functionality - Sale",
    "depends" : ['cederroth_sale'],
    'data': ['security/cd_security.xml',
             'security/ir.model.access.csv'
             ],

    "description": """
                    This module is dedicated to CEDERROTH needs
                    """,
    "init_xml": [],
    "update_xml": ['wizard/cd_other_cogs_add_wizard_view.xml',
                   'wizard/cd_product_history_wizard_view.xml',
                   'wizard/cd_export_promo_wizard_view.xml',
                   'view/cd_plan_mark_view.xml',
                   'view/cd_plan_section_view.xml',
                   'view/cd_plan_client_view.xml',
                   'view/cd_plan_product_view.xml',
                   'view/cd_plan_mark_month_view.xml',
                   'view/cd_plan_term_view.xml',
                   'view/cd_sale_data_import_view.xml',
                   'view/cd_report_other_cogs_view.xml',
                   'view/cd_report_ap_view.xml',
                   'view/cd_report_other_mark_month_view.xml',
                   'view/cd_report_plan_client_view.xml',
                   'view/cd_report_plan_client_brand_view.xml',
                   'view/cd_report_forecast_product_view.xml',
                   'view/cd_report_trade_promo_view.xml',
                   'view/cd_report_coop_view.xml',
                   'view/cd_report_plan_section_view.xml'
                   ],
    "installable": True,
    "active": False,
}
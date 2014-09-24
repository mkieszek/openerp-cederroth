#########################################################################
# Copyright (C) 2009  Sharoon Thomas, Open Labs Business solutions      #
# Copyright (C) 2012-Today  Akretion www.akretion.com                   #
#       @author sebastien beau sebastien.beau@akretion.com              #
#                                                                       #
#This program is free software: you can redistribute it and/or modify   #
#it under the terms of the GNU General Public License as published by   #
#the Free Software Foundation, either version 3 of the License, or      #
#(at your option) any later version.                                    #
#                                                                       #
#This program is distributed in the hope that it will be useful,        #
#but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#GNU General Public License for more details.                           #
#                                                                       #
#You should have received a copy of the GNU General Public License      #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.  #
#########################################################################

{
    "name" : "Products for CEDERROTH",
    "version" : "0.1 ",
    "author" : "Marcin Kieszek, Via IT Solutions",
    "website" : "http://www.viait.pl/",
    "category" : "Added functionality - Product attributes",
    "depends" : ["multi_image","product", "stock", "account"],
    'data': ['security/cd_security.xml',
             'security/ir.model.access.csv',
             'data/product_packaging.xml',
             'data/product_category.xml',
             'data/manufacturer_data.xml',
             'data/status_listing.xml',
             'data/cd_res_partner_title.xml',
             ],

    "description": """
    This module is dedicated to CEDERROTH needs
    """,
    "init_xml": [],
    "update_xml": ['wizard/cd_cogs_import_view.xml',
                   'wizard/cd_listing_import_view.xml',
                   'wizard/cd_listing_export.xml',
                   'wizard/cd_csv2products_view.xml',
                   'wizard/cd_change_date_view.xml',
                   'wizard/cd_add_listing_view.xml',
                   'view/res_partner_view.xml',
                   'view/cd_listing_view.xml',
                   'view/res_config_view.xml',
                   'view/product_view.xml',
                   'view/menu.xml',
                   'wizard/cd_export_product_view.xml',
                   ],
    "installable": True,
    "active": False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

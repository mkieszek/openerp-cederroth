# -*- coding: utf-8 -*-
"""
@author: mbereda
"""

import datetime
import pdb

from openerp.osv import fields, osv
from tools.translate import _


class cd_price_list(osv.Model):
    _name = "cd.price.list"
    _description = "Price list"
    
    
    _columns = {
        'product_id' : fields.many2one('product.product', 'Product',required=True),
        'client_id': fields.many2one('res.partner', 'Klient', required=True),
        'price': fields.float('Cena sprzedaży', required=True),
        }
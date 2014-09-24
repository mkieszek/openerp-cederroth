# -*- coding: utf-8 -*-
"""
@author: mbereda
"""

from openerp.osv import fields, osv
from openerp.osv.orm import Model

import pdb

class cd_product_limited(osv.Model):
    _name = "cd.product.limited"
    
    def _get_value(self, cr, uid, ids, name, arg, context=None):
        val={}
        for prod in self.browse(cr, uid, ids):
            cogs = prod.product_id.price_cogs
            val[prod.id] = prod.count*cogs
        return val

    _columns = {
        'product_id': fields.many2one('product.product', 'Produkt', required=True),
        'count': fields.integer('Ilość', required=True),
        'value': fields.function(_get_value, type='float', store=False, string='Wartość', readonly=True),
        
        'plan_client_id': fields.many2one('cd.plan.client', 'Plan Klient', required=True),
    }

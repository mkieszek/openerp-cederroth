# -*- coding: utf-8 -*-
"""
@author: mbereda
"""

from openerp.osv import fields, osv
from openerp.osv.orm import Model

import pdb

class cd_sale(osv.Model):
    _name = "cd.sale"

    def _get_gp_proc(self, cr, uid, ids, name, arg, context=None):
        val={}
        for id in ids:
            amount = 0.00
            sale = self.browse(cr, uid, id)
            if sale.nsh_price != 0.0:
                amount = (sale.nsh_price - sale.price_cogs)/sale.nsh_price
            else:
                amount = 0.00
            val[sale.id] = amount*100
        return val
    
    def _get_value_cogs(self, cr, uid, ids, name, arg, context=None):
        val={}
        for id in ids:
            amount = 0.00
            sale = self.browse(cr, uid, id)
            if sale.count != 0 or sale.product_id.price_cogs != 0.0:
                amount = sale.count*sale.product_id.price_cogs
            else:
                amount = 0.00
            val[sale.id] = amount
        return val
    
    _columns = {
        'product_id': fields.many2one('product.product', 'Produktu', required=True),
        'count': fields.integer('Ilość', required=True),
        'nsh_price': fields.float('Cena sprzedaży NSH', required=True),
        #'price_cogs': fields.related('product_id', 'price_cogs', type="float", store=True, string="Cena COGS", required=True, readonly=True),
        'price_cogs': fields.function(_get_value_cogs, type="float", string='Wartość COGS', readonly=True, store=True),
        'gp_proc': fields.function(_get_gp_proc, type="float", string='GP %', readonly=True, store=True),
        
        'plan_client_id': fields.many2one('cd.plan.client', 'Plan Klient'),
    }

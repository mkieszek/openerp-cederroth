# -*- coding: utf-8 -*-
"""
@author: mbereda
"""

from openerp.osv import fields, osv
from openerp.osv.orm import Model

import pdb

class cd_other_marketing(osv.Model):
    _name = "cd.other.marketing"
    
    def _get_gross_value(self, cr, uid, ids, name, arg, context=None):
        val={}
        for plan in self.browse(cr, uid, ids):
            val[plan.id] = plan.cu_cost*plan.count
        return val
    
    _columns = {
        'product_category_id': fields.many2one('product.category', 'Marka', required=True),
        'pos_name': fields.char('Nazwa POS', size=255, required=True),
        'cu_cost': fields.float('Koszt CU', required=True),
        'count': fields.integer('Ilość', required=True),
        'gross_value': fields.function(_get_gross_value, type='float', string='Wartość brutto', store=False),
        'plan_client_id': fields.many2one('cd.plan.client', 'Plan Klient'),
        'plan_mark_month_id': fields.many2one('cd.plan.mark.month', 'Plan Marketing Miesiąc'),
        }

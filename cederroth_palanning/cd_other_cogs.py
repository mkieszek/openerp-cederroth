# -*- coding: utf-8 -*-
"""
@author: mbereda
"""

from openerp.osv import fields, osv
from openerp.osv.orm import Model

import pdb

AVAILABLE_SATTLED = [('01',"Nie podlega rozliczeniu - Prezentacja"), ('02',"Nie podlega rozliczeniu - Próbki/saszetki"), \
                     ('03',"Nie podlega rozliczeniu - Testery"), ('04',"Nie podlega rozliczeniu - Produkty limitowane"), \
                     ('05',"Podlega rozliczeniu - Akcje lokalne"), ('06',"Podlega rozliczeniu - Przeceny/wymiany")]

class cd_other_cogs(osv.Model):
    _name = "cd.other.cogs"
    
    def _get_value_cogs(self, cr, uid, ids, name, arg, context=None):
        val={}
        for gratis in self.browse(cr, uid, ids):
            val[gratis.id]=gratis.price_cogs*gratis.count
        return val
    
    _columns = {
        'product_id': fields.many2one('product.product', 'Produkt', required=True),
        'count': fields.integer('Ilość', required=True),
        'plan_client_id': fields.many2one('cd.plan.client', 'Plan Klient'),
        'plan_mark_month_id': fields.many2one('cd.plan.mark.month', 'Plan Marketing Miesiąc'),
        'settled': fields.selection(AVAILABLE_SATTLED, 'Rozliczenie', required=True, readonly=False),
        'price_cogs' : fields.related('product_id','price_cogs',type='float',string="Cogs", readonly=True, store=True),
        'value' : fields.function(_get_value_cogs, type="float", string='Wartość COGS', readonly=True, store=True),
    }

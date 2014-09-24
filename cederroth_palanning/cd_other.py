# -*- coding: utf-8 -*-
"""
@author: mbereda
"""

from openerp.osv import fields, osv
from openerp.osv.orm import Model

import pdb

AVAILABLE_TARGETS = [('01',"Listingi"), 
                     #('02',"Hostessy"), wyłączone 
                     ('03',"Programy lojalnościowe"), 
                     #('04',"Merchandising"), wyłączone
                     ('05',"Inne"), 
                     ('06', 'Akcje pozabudżetowe - Trade promo'),
                     ('07', 'Akcje pozabudżetowe - COOP'),
                     ('08', 'Szkolenia'),
                     ('c01',"Nie podlega rozliczeniu - Reprezentacja"), 
                     ('c02',"Nie podlega rozliczeniu - Próbki/saszetki"),
                     ('c03',"Nie podlega rozliczeniu - Testery"), 
                     ('c04',"Nie podlega rozliczeniu - Produkty limitowane"),
                     ('c05',"Podlega rozliczeniu - Akcje lokalne"),
                     ('c06',"Podlega rozliczeniu - Przeceny/wymiany")]

class cd_other(osv.Model):
    _name = "cd.other"
    
    def _get_value(self, cr, uid, ids, name, arg, context=None):
        val={}
        for other in self.browse(cr, uid, ids):            
            val[other.id] = other.amount*other.count
        return val

    _columns = {
        'product_category': fields.many2one('product.category', 'Marka produktu', domain="[('parent_id','=',False)]", required=True),
        'target': fields.selection(AVAILABLE_TARGETS, 'Cel', required=True),
        'amount': fields.float('Koszt', required=True),
        'count': fields.integer('Ilość', required=True),
        'value': fields.function(_get_value, string='Wartość', type="float", store=False, readonly=True),
        
        'plan_client_id': fields.many2one('cd.plan.client', 'Plan Klient'),
        'plan_mark_month_id' : fields.many2one('cd.plan.mark.month', 'Plan Marketing Miesiąc'),
        'note' : fields.char('Uwagi'),  
    }

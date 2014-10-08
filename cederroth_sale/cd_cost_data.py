# -*- coding: utf-8 -*-
"""
@author: mbereda
"""

from openerp.osv import fields, osv
import pdb

COST_TYPE = [('01',"Other Mark"), ('02',"COOP"), ('03',"Trade promo"), ('04', 'Other COGS')]

class cd_cost_data(osv.Model):
    _name = "cd.cost.data"
    _description = "Rodzaj kosztu"
    
    _columns = {
        'name': fields.char('Tytuł', required=True),
        'cost_type': fields.selection(COST_TYPE,'Typ kosztu', required=True),
        'cost_cu' :  fields.float('Koszt CU'),
        'pos' : fields.boolean('POS'),
    }
    
    """def write(self, cr, uid, ids, vals, context=None):
        pdb.set_trace()
        if 'cost_type' in vals:
            vals_cost={'cost_type' : vals['cost_type']}
            cd_cost_promotions_obj = self.pool.get('cd.cost.promotions')
            cd_cost_promotions_ids = cd_cost_promotions_obj.search(cr, uid, [('cost_data_id','in', ids)])
            cd_cost_promotions_obj.write(cr, uid, cd_cost_promotions_ids, vals_cost)
        
        super(cd_cost_data, self).write(cr, uid, ids, vals, context=context)
        return True"""

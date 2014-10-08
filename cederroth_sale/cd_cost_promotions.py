# -*- coding: utf-8 -*-
"""
@author: mbereda
"""

from openerp.osv import fields, osv
import cd_cost_data
import pdb

class cd_cost_promotions(osv.Model):
    _name = "cd.cost.promotions"
    _inherit = 'mail.thread'
    _description = "Koszty akcji promocyjnych"
    
    def _get_value_amount(self, cr, uid, ids, name, arg, context=None):
        val={}
        for cost in self.browse(cr, uid, ids):
            amount = cost.cu_cost * cost.count
            val[cost.id] = amount
        return val
    
    _columns = {
        'name': fields.char('Tytuł'),
        'amount': fields.function(_get_value_amount, type="float", string='Wartość', readonly=True, store=True),
        'cost_data_id': fields.many2one('cd.cost.data', 'Koszt', required=True),
        'cost_type': fields.related('cost_data_id', 'cost_type', string='Typ kosztu', readonly=True, type="selection", store=False,
                selection=cd_cost_data.COST_TYPE),
        'promotions_id': fields.many2one('cd.promotions', "Akcje promocyjne"),
        'cu_cost': fields.float('Koszt CU', readonly=False),
        'count': fields.integer('Ilość', required=True),
        'pos' : fields.related('cost_data_id', 'pos', string="POS", readonly=True, type="boolean"),
    }
    
    def create(self, cr, uid, data, context=None):
        #pdb.set_trace()
        cost_cu = self.pool.get('cd.cost.data').browse(cr, uid, data['cost_data_id']).cost_cu
        data['cu_cost'] = cost_cu
        data['amount'] = cost_cu * data['count']
        id = super(cd_cost_promotions, self).create(cr, uid, data)
        return id

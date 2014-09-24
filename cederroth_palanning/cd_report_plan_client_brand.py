# -*- coding: utf-8 -*-
'''
@author: mbereda
'''

from openerp.osv import fields, osv
from openerp.osv.orm import Model
from openerp import tools

import pdb

class cd_report_plan_client_brand(osv.Model):
    _name = "cd.report.plan.client.brand"    
    
    _columns = {
        'plan_client_id': fields.many2one('cd.plan.client', 'Plan Klient'),
        'year': fields.integer('Year'),
        'month' : fields.char('Month'),
        'section_id' : fields.many2one('crm.case.section', 'Kanał'),
        'client_id' : fields.many2one('res.partner','Klient'),
        'create_date': fields.date('Data akceptacji'),
        
        'product_category_id': fields.many2one('product.category', 'Marka'),
        'forecast': fields.float('Forecast'),
        'plan_value': fields.float('Estymacja'),
        'exec_value': fields.float('Zrealizowana wartość'),
        'plan_luz': fields.float('Estymacja standard'),
        'plan_promo': fields.float('Estymacja promo'),
        'estimation_news': fields.float('Estymacja nowości'),
    }
    
    def open_plan_client(self, cr, uid, ids, context=None):
        plan_client_id = self.browse(cr, uid, ids[0]).plan_client_id.id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Plan Klient', 
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'cd.plan.client',
            'res_id': plan_client_id,
            'target': 'self',
        }

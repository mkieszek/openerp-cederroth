# -*- coding: utf-8 -*-
"""
@author: mbereda
"""

from openerp.osv import fields, osv
from openerp.osv.orm import Model
from openerp.addons.mail.mail_message import decode
from datetime import timedelta
import datetime

import pdb

AVAILABLE_MONTHS = [('01',"Styczeń"), ('02',"Luty"), ('03',"Marzec"), ('04',"Kwiecień"), ('05',"Maj"), ('06',"Czerwiec"), 
          ('07',"Lipiec"), ('08',"Sierpień"), ('09',"Wrzesień"), ('10',"Październik"), ('11',"Listopad"), ('12',"Grudzień")]

class cd_plan_mark_month(osv.Model):
    _name = "cd.plan.mark.month"
    _inherit = 'mail.thread'
    _description = 'Plan Marketing Month'
    
    def _get_mark_ids(self, cr, uid, ids, name, arg, context=None):
        val={}
        for plan in self.browse(cr, uid, ids):
            plan_mark_obj = self.pool.get('cd.plan.mark')
            plan_mark_ids = plan_mark_obj.search(cr, uid, [('month','=',plan.month),('year','=',plan.year)])
            val[plan.id] = plan_mark_ids
        return val
    
    def _get_blocked(self, cr, uid, ids, name, arg, context=None):
        val={}
        today = datetime.date.today()
        for plan in self.browse(cr, uid, ids):
            #mark_start = datetime.datetime.strptime(plan.start_plan,"%Y-%m-%d").date()
            mark_stop = datetime.datetime.strptime(plan.stop_plan,"%Y-%m-%d").date()
            if mark_stop > today:
                blocked_edit = False
            else:
                blocked_edit = True
            val[plan.id] = {'blocked_edit': blocked_edit, 'blocked_date': True}
        return val
    
    _columns = {
        'plan_month_ids' : fields.one2many('cd.plan.mark', 'plan_mark_month_id', 'Plany Marketingowe'),
        'year': fields.integer("Rok", required=True, group_operator='min'),
        'month': fields.selection(AVAILABLE_MONTHS, 'Miesiąc', required=True),
        
        'other_cogs_ids': fields.one2many('cd.other.cogs', 'plan_mark_month_id', 'Other COGS'),
        'other_marketing_ids': fields.one2many('cd.other.marketing', 'plan_mark_month_id', 'Other Marketing'),
        'other_ids':  fields.one2many('cd.other', 'plan_mark_month_id', 'Other'),
        'blocked_edit': fields.function(_get_blocked, type='boolean', string='Blokowana edycji', store=False, multi='blocked_edit'),
        'blocked_date': fields.function(_get_blocked, type='boolean', string='Blokowana data', store=False, multi='blocked_date'),
        
        #'start_plan': fields.related('plan_term_id', 'mark_start', type='date', string='Rozpoczęcie planowania marketingu', readonly=True),
        'stop_plan': fields.related('plan_term_id', 'mark_stop', type='date', string='Koniec planowania marketingu', readonly=True),
        'plan_term_id': fields.many2one('cd.plan.term', 'Plan terminy')
    }
    
    _defaults = {
        'year': lambda s, cr, uid, c: datetime.date.today().year,
    }
    
    def name_get(self, cr, uid, ids, context=None):
        """Overrides orm name_get method"""
        if not isinstance(ids, list) :
            ids = [ids]
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['month', 'year'], context)
        for record in reads:
            month = str(record['month'])
            year = str(record['year'])
            res.append((record['id'], 'Data: ' + month + ' - ' + year))
        return res

    def create(self, cr, uid, data, context=None):
        plan_term_obj = self.pool.get('cd.plan.term')
        cd_config_obj = self.pool.get('cd.config.settings')
        cd_config_id = cd_config_obj.search(cr, uid, [])
        config = cd_config_obj.browse(cr, uid, cd_config_id[-1])
        vals_term = {
                    'year': data['year'],
                    'month': data['month'],
                    'mark_start': datetime.date(data['year'], int(data['month']), 1)-timedelta(weeks=config.start_mark),
                    'mark_stop': datetime.date(data['year'], int(data['month']), 1)-timedelta(weeks=config.stop_mark),
                    'sale_start': datetime.date(data['year'], int(data['month']), 1)-timedelta(weeks=config.start_sale),
                    'sale_stop': datetime.date(data['year'], int(data['month']), 1)-timedelta(weeks=config.stop_sale),
                     }
        plan_term_id = plan_term_obj.create(cr, uid, vals_term)
        
        vals_list = []
        if self.search(cr, uid, [('month','=',data['month']),('year','=',data['year'])]):
            raise osv.except_osv(decode('Ostrzeżenie'), decode('Plan Makteting Miesiąc na wybrany miesiąc już jest w systemie'))
        
        plan_mark_obj = self.pool.get('cd.plan.mark')
        if 'plan_month_ids' in data:
            for vals in data['plan_month_ids']:
                vals_list.append(vals[2])
            del data['plan_month_ids']
        
        data['plan_term_id'] = plan_term_id
            
        plan_id = super(cd_plan_mark_month, self).create(cr, uid, data, context=context)
        
        #Usunięcie dodawania Administratora do obserwarotów
        self.message_unsubscribe(cr, uid, [plan_id], [3], context=None)
                
        if vals_list:
            for val in vals_list:
                val['year'] = data['year']
                val['month'] = data['month']
                val['plan_mark_month_id'] = plan_id
                plan_mark_obj.create(cr, uid, val)
        
        return plan_id
    
    def write(self, cr, uid, ids, data, context=None):
        plan = self.browse(cr, uid, ids[0])
        plan_mark_obj = self.pool.get('cd.plan.mark')
        if 'plan_month_ids' in data:
            i = 0
            for vals in data['plan_month_ids']:
                i += 1
                if vals[1] == False:
                    vals[2]['month'] = plan.month
                    vals[2]['year'] = plan.year
                    vals[2]['plan_mark_month_id'] = plan.id
                    plan_mark_obj.create(cr, uid, vals[2])
        
                    del data['plan_month_ids'][i-1]
                    
        plan_id = super(cd_plan_mark_month, self).write(cr, uid, ids, data, context=context)
        
        return plan_id
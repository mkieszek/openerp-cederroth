# -*- coding: utf-8 -*-


import time
from openerp.report import report_sxw
import pdb
import datetime

class report_promo_salesman(report_sxw.rml_parse):
    _name = 'report.promo.salesman'

    def set_context(self, objects, data, ids, report_type=None):
        #pdb.set_trace()
        
        today = datetime.date.today()
        data['today'] = today
        cd_promo_obj = self.pool.get('cd.promotions')
        
        promo_ids = cd_promo_obj.search(self.cr, self.uid, [('start_date', '<=', today),('stop_date','>=', today)])
        
        promo_objects = cd_promo_obj.browse(self.cr, self.uid, promo_ids)
        
        return super(report_promo_salesman, self).set_context(promo_objects, data, promo_ids, report_type=report_type)
    
    def __init__(self, cr, uid, name, context=None):
        #pdb.set_trace()
        if context is None:
            context = {}
        super(report_promo_salesman, self).__init__(cr, uid, name, context=context)
        
        self.localcontext.update( {
            'time': time,
            'get_today': self._get_today,
            'get_communication_form': self._get_communication_form,
            'get_monitor_merchend': self._get_monitor_merchend,
            'get_tasks_ph': self._get_tasks_ph,
            'get_task_merchand': self._get_task_merchand,
            'get_display': self._get_display,
            'get_pos': self._get_pos,
            'get_products': self._get_products
        })
        self.context = context
        
        
    def _get_today(self, data):
        return data['today']
    
    def _get_communication_form(self, promo):
        communication_form = ''
        for item in promo.communication_ids:
            if communication_form != '':
                communication_form += ', '
            communication_form += item.name
        return communication_form
    
    def _get_monitor_merchend(self, promo):
        monit_merch = 'Nie'
        if promo.monitor_merchand == True:
            monit_merch = 'Tak'
        return monit_merch
    
    def _get_tasks_ph(self, promo):
        task_ph = ''
        for task in promo.task_sale_ids:
            if task_ph != '':
                task_ph += ', '
            task_ph += task.name
        return task_ph
    
    def _get_task_merchand(self, promo):
        task_merch = ''
        for task in promo.task_merchandising_ids:
            if task_merch != '':
                task_merch += ', '
            task_merch += task.name
        return task_merch
        
    def _get_display(self, promo):
        display = ''
        for disp in promo.display_ids:
            if display != '':
                display += ', '
            display += disp.name
        return display
    def _get_pos(self, promo):
        pos_str = ''
        for pos in promo.cost_promotions_ids:
            if pos.pos:
                if pos_str != '':
                    pos_str += ', '
                pos_str += pos.cost_data_id.name
        return pos_str
    
    def _get_products(self, promo):
        if promo.product_rel_ids:
            return promo.product_rel_ids
        else:
            return False
    
report_sxw.report_sxw('report.cd.report_promo_salesman', 'cd.promotions', 'cederroth_palanning/report/report_promo_salesman.rml', parser=report_promo_salesman)
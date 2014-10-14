# -*- coding: utf-8 -*-


import time
from openerp.report import report_sxw
import pdb
import datetime
class report_promo_board(report_sxw.rml_parse):
    _name = 'report.promo.board'

    def set_context(self, objects, data, ids, report_type=None):
        pdb.set_trace()
        
        today = datetime.date.today()
        data['today'] = today
        cd_promo_obj = self.pool.get('cd.promotions')
        
        promo_ids = cd_promo_obj.search(self.cr, self.uid, [('start_date', '<=', today),('stop_date','>=', today)])
        
        promo_objects = cd_promo_obj.browse(self.cr, self.uid, promo_ids)
        
        return super(report_promo_board, self).set_context(promo_objects, data, promo_ids, report_type=report_type)
    
    def __init__(self, cr, uid, name, context=None):
        pdb.set_trace()
        if context is None:
            context = {}
        super(report_promo_board, self).__init__(cr, uid, name, context=context)
        
        self.localcontext.update( {
            'time': time,
            'get_today': self._get_today
        })
        self.context = context
        
    def _get_today(self, data):
        return data['today']
    
report_sxw.report_sxw('report.cd.report_promo_board', 'cd.promotions', 'cederroth_palanning/report/report_promo_board.rml', parser=report_promo_board)
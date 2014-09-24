# -*- coding: utf-8 -*-
"""
@author: mbereda
"""

from openerp.osv import fields, osv
from openerp.osv.orm import Model

class cd_plan_term(osv.Model):
    _name = "cd.plan.term"
    
    _columns = {
            'year': fields.integer('Rok', required=True, readonly=True),
            'month': fields.char('Miesiąc', required=True, readonly=True),
            'mark_start': fields.date('Rozpoczęcie plan marketing'),
            'mark_stop': fields.date('Zakończenie plan marketing', required=True),
            'sale_start': fields.date('Rozpoczęcie plan sprzedaż'),
            'sale_stop': fields.date('Zakończenie plan sprzedaż', required=True),
    }
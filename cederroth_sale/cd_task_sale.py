# -*- coding: utf-8 -*-
"""
@author: mkieszek
"""

from openerp.osv import fields, osv

class cd_task_sale(osv.Model):
    _name = "cd.task.sale"
    _description = "Zadanie PH"
    
    _columns = {
        'name': fields.char('Nazwa', required=True),
    }

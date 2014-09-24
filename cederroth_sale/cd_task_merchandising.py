# -*- coding: utf-8 -*-
"""
@author: mkieszek
"""

from openerp.osv import fields, osv

class cd_task_merchandising(osv.Model):
    _name = "cd.task.merchandising"
    _description = "Zadanie Merchandising"
    
    _columns = {
        'name': fields.char('Nazwa', required=True),
    }

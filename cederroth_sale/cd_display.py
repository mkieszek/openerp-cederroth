# -*- coding: utf-8 -*-
"""
@author: mkieszek
"""

from openerp.osv import fields, osv

class cd_display(osv.Model):
    _name = "cd.display"
    _description = "Ekspozycja"
    
    _columns = {
        'name': fields.char('Tytuł', required=True),
    }

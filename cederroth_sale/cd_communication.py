# -*- coding: utf-8 -*-
"""
@author: mkieszek
"""

from openerp.osv import fields, osv

class cd_communication(osv.Model):
    _name = "cd.communication"
    _description = "Forma komunikacji"
    
    _columns = {
        'name': fields.char('Nazwa', required=True),
    }

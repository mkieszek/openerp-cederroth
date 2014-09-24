# -*- coding: utf-8 -*-
'''
@author: mbereda
'''

from openerp.osv import fields, osv

class cd_type_promotion(osv.Model):
    _name = "cd.type.promotions"
    
    _columns = {
        'name': fields.char('Typ', required=True),
    }
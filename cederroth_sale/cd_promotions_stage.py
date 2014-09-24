# -*- coding: utf-8 -*-
"""
@author: Marcin Bereda
"""

from openerp.osv import fields, osv
import time
import datetime
from openerp import tools
from openerp.osv.orm import except_orm
from openerp.tools.translate import _
from dateutil.relativedelta import relativedelta

AVAILABLE_STATES = [
    ('draft', 'New'),
    ('canceled', 'Cancelled'),
    ('open', 'In Progress'),
    ('pending', 'Pending'),
    ('done', 'Closed')
]

class cd_promotions_stage(osv.Model):
     _name = 'cd.promotions.stage'
     _description = 'Promotions Stage'
     _columns = {
        'name': fields.char('Name', required=True),
        'sequence': fields.integer('Sequence', help="Used to order the note stages"),
        'state' : fields.selection(AVAILABLE_STATES, 'State', required=True),
        'probability': fields.float('Success Rate (%)',group_operator="avg"),
        'fold' : fields.boolean('Fold by defualt')
     }


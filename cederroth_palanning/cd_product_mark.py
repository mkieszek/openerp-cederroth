# -*- coding: utf-8 -*-
"""
@author: mbereda
"""

from openerp.osv import fields, osv
from openerp.osv.orm import Model
from openerp.addons.mail.mail_message import decode
import pdb

class cd_product_mark(Model):
    _name = "cd.product.mark"
    
    _columns = {
        'product_id': fields.many2one('product.product',"Produkt", required=True, ondelete="cascade", readonly=False),
        'plan_mark_id': fields.many2one('cd.plan.mark',"Plan Makretingowy", required=True, ondelete="cascade"),
    }
    
    
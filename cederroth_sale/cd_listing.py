# -*- coding: utf-8 -*-
import pdb

from openerp.osv.orm import Model
from openerp.osv import fields

class product_product(Model):
    _inherit = "cd.listing"
    _columns = {
        #'cd_product2promotions': fields.many2one('cd.product2promotions', "PROM")
    }
# -*- coding: utf-8 -*-
import pdb

from openerp.osv.orm import Model
from openerp.osv import fields

class product_product(Model):
    _inherit = "product.product"
    _columns = {
        'price_cogs': fields.float('Cena COGS'),
        'sugest_price_ret': fields.float("Sugerowana cena detaliczna"),
        'sugest_price_prom': fields.float("Sugerowana cena promocyjna"),
        #'cd_product2promotions': fields.many2one('cd.product2promotions', "Dodawanie produktów"),
        'cd_promotions_id' : fields.many2many('cd.promotions', 'Promotions'),
    }
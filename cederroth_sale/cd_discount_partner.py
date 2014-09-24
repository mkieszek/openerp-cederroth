# -*- coding: utf-8 -*-
'''
@author: mbereda
'''

from openerp.osv import fields, osv

class cd_discount_partner(osv.Model):
    _name="cd.discount.partner"
    
    def _get_discount_back(self, cr, uid, ids, name, arg, context=None):
        val={}
        
        for discount in self.browse(cr, uid, ids):
            back_coop = discount.discount_back_coop
            back_trade_promo = discount.discount_back_trade_promo
            
            back = back_coop + back_trade_promo
            val[discount.id] = back
        return val
    
    _columns = {
        'product_category': fields.many2one('product.category','Marka', domain="[('parent_id','=',False)]", required=True),
        'discount_front': fields.float('Rabat frontowy (%)', required=True),
        'discount_back': fields.function(_get_discount_back, type='float', string='Rabat backowy (%)', store=True),
        'discount_promo': fields.float('Rabat promocyjny', required=True),
        'client_id': fields.many2one('res.partner', 'Klient'),
        'discount_back_coop': fields.float('Rabat backowy COOP (%)', required=True),
        'discount_back_trade_promo': fields.float('Rabat backowy Trade Promo (%)', required=True),
        
    }
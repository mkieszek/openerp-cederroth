# -*- coding: utf-8 -*-

from openerp.osv.orm import Model
from openerp.osv import fields

class res_partner(Model):
    _inherit = "res.partner"
    
    def _get_discount_back(self, cr, uid, ids, name, arg, context=None):
        val={}
        
        for partner in self.browse(cr, uid, ids):
            back_coop = partner.discount_back_coop
            back_trade_promo = partner.discount_back_trade_promo
            
            back = back_coop + back_trade_promo
            val[partner.id] = back
        return val
    
    _columns = {
        'discount_front': fields.float('Rabat frontowy (%)', required=True),
        'discount_back_coop': fields.float('Rabat backowy COOP (%)', required=True),
        'discount_promo': fields.float('Rabat promocyjny (%)', required=True),
        'ph_user_id': fields.many2one('res.users', "Opiekun PH"),
        'discount_partner_ids': fields.one2many('cd.discount.partner', 'client_id', 'Rabaty'),
        'discount_back_trade_promo': fields.float('Rabat backowy Trade Promo (%)', required=True),
        'discount_back' : fields.function(_get_discount_back, type='float', string='Rabat backowy (%)', store=True),
        'bok_user_id' : fields.many2one('res.users', 'Pracownik BOK'),
    }
    
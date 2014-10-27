# -*- coding: utf-8 -*-
"""
@author: mbereda
"""

import datetime
import pdb

from openerp.osv import fields, osv
from tools.translate import _

class cd_price_list(osv.Model):
    _name = "cd.price.list"
    _description = "Price list"
    
    
    _columns = {
        'product_id' : fields.many2one('product.product', 'Product',required=True),
        'client_id': fields.many2one('res.partner', 'Klient', required=True),
        'price': fields.float('Cena sprzedaży', required=True),
        }
    
    def create(self, cr, uid, data, context=None):
        prod_id = super(cd_price_list, self).create(cr, uid, data, context=context)
        #pobierz wszystkie aktywne listingi dla klienta i tego produktu
        cd_listing = self.pool.get('cd.listing')
        
        cd_listing_ids = cd_listing.search(cr, uid, [('client_id','=', data['client_id']),('product_id','=',data['product_id']),('status_l','=','0')])
        
        #dla wybranych listingów zmień cenę na ndata['ową
        val_price = {'price_sale': data['price']}
        cd_listing.write(cr, uid, cd_listing_ids, val_price)

        return prod_id
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'price' in vals:
             cd_listing = self.pool.get('cd.listing')
             cd_price_list_obj = self.browse(cr, uid, ids[0])
             cd_listing_ids = cd_listing.search(cr, uid, [('client_id','=', cd_price_list_obj.client_id.id),
                                                          ('product_id','=', cd_price_list_obj.product_id.id),
                                                          ('status_l','=','0')])
             val_price = {'price_sale': vals['price']}
             cd_listing.write(cr, uid, cd_listing_ids, val_price)
        return super(cd_price_list, self).write(cr, uid, ids, vals, context=None)
        
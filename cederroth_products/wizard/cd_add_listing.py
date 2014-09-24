# -*- coding: utf-8 -*-
"""
@author: mbereda
"""

from openerp.osv import fields, osv
from openerp.osv.orm import Model
from openerp.addons.mail.mail_message import decode

import pdb

class cd_add_listing(osv.Model):
    _name = "cd.add.listing"
    
    _columns = {        
        'client_id': fields.many2one('res.partner', 'Klient', domain="[('is_company','=',True),('parent_id','=',False)]", required=True),
        'format_id': fields.many2one('cd.client.format', 'Format', domain="[('client_id','=',client_id)]", required=False),
        'on_top': fields.boolean('On top'),
        'old_product_id': fields.many2one('product.product', 'Zastępowany Produkt', domain="[('listing.fclient_id','=',format_id)]"),
        'end_date': fields.date('Data wycofania'),
        'new_product_id': fields.many2one('product.product', 'Nowy Produkt', required=True),
        'start_date': fields.date('Data aktywacji', required=True),
        'price': fields.float('Cena katalogowa', required=True),
    }
    
    _defaults = {
        'on_top' : False
    }
    
    def add_listing(self, cr, uid, ids, context=None):
        listing_obj = self.pool.get('cd.listing')
        w = self.browse(cr, uid, ids)[0]
        
        listing_search = [
                          ('product_id','=',w.new_product_id.id),
                          ('status_l','=','1'),
                          ('client_id','=',w.client_id.id)
                          ]
        if w.format_id:
            listing_search.append(('fclient_id','=',w.format_id.id))
        #else:
            #format_ids = [format.id for format in w.client_id.cformat]
            #listing_search.append(('fclient_id','in',format_ids))
        
        #Blokowanie wprowadzenia listingu który już istnieje
        if listing_obj.search(cr, uid, listing_search):
            raise osv.except_osv(decode('Ostrzeżenie'), decode('Ten listing już istnieje.')) 
        
        create_vals = {
                'product_id': w.new_product_id.id,
                'client_id': w.client_id.id,
                
                'change_date': w.start_date,
                'status_l': '1',
                'price_sale': w.price,
                }
        
        format_ids = []
        if w.format_id:
            format_ids = [w.format_id.id]
        else:
            format_ids = [format.id for format in w.client_id.cformat]
        
        if format_ids:
            for format_id in format_ids:
                create_vals['fclient_id'] = format_id
                listing_obj.create(cr, uid, create_vals, context=None)
        else:
            listing_obj.create(cr, uid, create_vals, context=None)
        
        if w.on_top == False:
            write_vals = {}
            write_vals = {
                    'change_date': w.end_date,
                    'status_l': '2',
                    }
            if w.format_id:
                listing_id = listing_obj.search(cr, uid, [('product_id','=',w.old_product_id.id),('fclient_id','=',w.format_id.id)])
            else:
                listing_id = listing_obj.search(cr, uid, [('product_id','=',w.old_product_id.id)])
                
            listing_obj.write(cr, uid, listing_id, write_vals, context=None)
        
        return True
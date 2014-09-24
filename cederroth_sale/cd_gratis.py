# -*- coding: utf-8 -*-
'''
Created on 15 maj 2014

@author: pczorniej
'''

from openerp.osv import fields, osv
from openerp.addons.mail.mail_message import decode

import pdb

DISTRIBUTION = [('01',"WM"), ('02',"FV")]

class cd_gratis(osv.Model):
    _name = "cd.gratis"
    """
    def _get_value(self, cr, uid, ids, name, arg, context=None):
        val={}
        pdb.set_trace()
        listing_obj = self.pool.get('cd.listing')
        for gratis in self.browse(cr, uid, ids):
            if gratis.distribution == '01':
                if gratis.product_id.price_cogs != 0 or gratis.product_id.vat_2010 or gratis.product_id.vat_2010.amount != None:
                    price_cogs = gratis.product_id.price_cogs
                    vat = gratis.product_id.vat_2010.amount
                    price_cogs2=price_cogs*(1+vat)
                else:
                    price_cogs2= 0.0
            else:
                price_cogs2=gratis.product_id.price_cogs
                
            client = gratis.promotions_id.client_id
            
            listing_ids = listing_obj.search(cr, uid, [('product_id','=', gratis.product_id.id),('client_id','=',client.id)])
            if not listing_ids:
                listing_ids = listing_obj.search(cr, uid, [('product_id','=',gratis.product_id.id)])
            price = 0.0
            if listing_ids:
                price = listing_obj.browse(cr, uid, listing_ids[0]).price_sale
                
            front_price = round(price - (price*(client.discount_front/100)), 2) if price and price != 0 and client.discount_front and client.discount_front != 0 and gratis.distribution=='02' else 0
            nsh_price = price-0.01-front_price
            
            pdb.set_trace()
            val[gratis.id] = {
                              'price_cogs': price_cogs2,
                              'front_price': front_price,
                              'value_discount': gratis.count*(front_price-nsh_price),
                              'nsh_price': nsh_price,
                              }
            
        return val
    """
    def _get_price_cogs(self, cr, uid, ids, name, arg, context=None):
        #pdb.set_trace()
        val={}
        for gratis in self.browse(cr, uid, ids):
            if gratis.distribution == '01':
                if gratis.product_id.vat_2010 and gratis.product_id.vat_2010.amount != None:
                    price_cogs = gratis.product_id.price_cogs
                    vat = gratis.product_id.vat_2010.amount
                    val[gratis.id]=price_cogs*(1+vat)
                else:
                    val[gratis.id]= gratis.product_id.price_cogs
            else:
                val[gratis.id]=gratis.product_id.price_cogs
        return val
    
    def _get_front_price(self, cr, uid, ids, name, arg, context=None):
        val={}
        for gratis in self.browse(cr, uid, ids):
            client = gratis.promotions_id.client_id
            if client.discount_front and client.discount_front != 0 and gratis.distribution == '02':
                listing_obj = self.pool.get('cd.listing')
                listing_ids = listing_obj.search(cr, uid, [('client_id','=',client.id),('product_id','=',gratis.product_id.id)])
                if not listing_ids:
                    listing_ids = listing_obj.search(cr, uid, [('product_id','=',gratis.product_id.id)])
                if listing_ids:
                    listing = listing_obj.browse(cr, uid, listing_ids[0])
                    val[gratis.id] = round(listing.price_sale - (listing.price_sale*(client.discount_front/100)), 2)
                else:
                    val[gratis.id] = 0.0
            else:
                val[gratis.id] = 0.0
        return val
    
    def _get_value_discount(self, cr, uid, ids, name, arg, context=None):
        val={}
        for gratis in self.browse(cr, uid, ids):
            if gratis.front_price == 0.0:
                val[gratis.id] = 0.0
            else:
                val[gratis.id] = gratis.count*(gratis.front_price-gratis.nsh_price)
            
        return val
    
    def _get_value_cogs(self, cr, uid, ids, name, arg, context=None):
        val={}
        for gratis in self.browse(cr, uid, ids):
            val[gratis.id]=gratis.price_cogs*gratis.count
        return val
    
    _columns = {
        'product_id': fields.many2one('product.product','Produkty', required=True),
        'movex_code' : fields.related('product_id','default_code',type='char',string="MOVEX", readonly=True),
        'product_vat' : fields.related('product_id','vat_2010',type='many2one', relation='account.tax', string="VAT", readonly=True),
        'price_cogs': fields.function(_get_price_cogs, type="float", string='Cena COGS', readonly=True, store=True),
        'count' : fields.integer('Ilość', required=True),
        'value_cogs' : fields.function(_get_value_cogs, type="float", string='Wartość COGS', readonly=True, store=True),
        'distribution' : fields.selection(DISTRIBUTION,'Dystrybucja', required=True),
        'nsh_price': fields.float('Cena NSH'),
        'discount_prom': fields.float('Rabat Promo'),
        'prom_price': fields.float('Cena Promo'),
        'front_price': fields.function(_get_front_price, type="float", string='Cena front', readonly=True, store=True),
        'value_discount': fields.function(_get_value_discount, type="float", string='Wartość rabatu promo', readonly=True, store=True),
        'promotions_id': fields.many2one('cd.promotions', "Akcje promocyjne"),
    }
    
    _defaults = {
                 'nsh_price': 0.01,
                 }
    
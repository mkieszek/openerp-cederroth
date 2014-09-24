# -*- coding: utf-8 -*-
"""
Created on Mon Oct  7 12:33:48 2013

@author: pczorniej
"""

import datetime
import pdb

from openerp.osv import fields, osv
from tools.translate import _

LISTING_STATUS = [('0','Aktywny'),('1','Do wprowadzenia'),('2','Do zdjęcia'),('3','Nie aktywny')]

class cd_listing(osv.Model):
    _name = "cd.listing"
    _description = "Product Listing"
    
    
    _columns = {
        'product_id' : fields.many2one('product.product', 'Product',required=True),
        'categ_id': fields.related('product_id','categ_id', type="many2one", relation="product.category", store=True,string="Category", readonly=True),
        'priorytet': fields.related('product_id','priorytet', type="integer", store=True,string="Priorytet", readonly=True),
        'product_mark': fields.related('product_id','product_mark', type="many2one", relation="product.category", store=False,string="Marka", readonly=True),
        'client_id' : fields.many2one('res.partner', 'Client',required=True ),
        'price_sale' : fields.float('Sale price'),
        'status_l' : fields.selection(LISTING_STATUS,'Status',required=True ),
        'change_date' : fields.date('Date of change',required=True),
        'fclient_id' : fields.many2one('cd.client.format','Client format',domain="[('client_id','=',client_id)]"),
        'movex': fields.related('product_id','default_code', type="char", store=True,string="MOVEX", readonly=True),
        
        }
 
    def change_status_all(self, cr, uid, context=None):
        
        listing_ids = self.pool.get('cd.listing').search(cr, uid, [('status_l','in',['1','2'])])
        
        now = datetime.datetime.now()
        today = now.strftime("%Y-%m-%d")
        today = datetime.datetime.strptime(today,"%Y-%m-%d")

        
        for listing in self.browse(cr, uid, listing_ids, context=context): 
            change = listing.change_date
            change = datetime.datetime.strptime(change,"%Y-%m-%d")
            vals = {}
            if listing.status_l == '1':
                if today > change:
                    vals['status_l']='0'
            elif listing.status_l == '2':
                if today > change:
                    vals['status_l']='3'
                  
            if vals :
                self.pool.get('cd.listing').write(cr, uid, listing.id, vals, context)
                body_product = _('<b>Listing changed for client: </b>%s<li> to status: %s</li>')%(listing.client_id.name, LISTING_STATUS[int(vals['status_l'])][1])
                product=self.pool.get('product.product')
                product.message_post(cr, uid, listing.product_id.id, body=body_product, context=context)
                
                body_client = _('<b>Listing changed for product: </b>%s<li> to status: %s</li>')%(listing.product_id.name, LISTING_STATUS[int(vals['status_l'])][1])
                client=self.pool.get('res.partner')
                client.message_post(cr, uid, listing.client_id.id, body=body_client, context=context)
                
        return True        

    def create(self, cr, uid, data, context=None):
        #pdb.set_trace()
        listing_id = super(cd_listing, self).create(cr, uid, data, context=context)
        
        partner_obj = self.pool.get('res.users')
        partner = partner_obj.search(cr, uid, [('id','=',uid)], context=context)
        partner_id = partner_obj.browse(cr, uid, partner)[0].partner_id.id
        self.pool.get('product.product').message_subscribe(cr, uid, [data['product_id']], [partner_id], context=context)
        
        return listing_id
# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 09:48:26 2013

@author: mbereda
"""

from openerp.osv import osv,fields
from tools.translate import _
import pdb
import datetime

class cd_changedate(osv.Model):
    _name = 'cd.changedate'
    
    _columns = {
            'product_id': fields.many2one('product.product','Product', readonly=True),       
            'availability_date': fields.date('available date'),
    }

        
    def change_date(self, cr, uid, product_id, context=None):
        

        
        w = self.browse(cr, uid, product_id, context=context)[0]
        
        product_id = context and context.get('active_id', False) or False
        
        values = {
            'availability_date': w.availability_date,
            }
            
        product=self.pool.get('product.product')
        product.write(cr, uid, [product_id], values, context=context)
        
        #pdb.set_trace()
        prod_id=product.browse(cr, uid, product_id, context=context)
        

        

        body_product = _('<b>Availability date changed for product: </b>[%s] %s<li> to date: %s</li>')%(prod_id.default_code, prod_id.name, w.availability_date)
        product.message_post(cr, uid, product_id, body=body_product, context=context)
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 16:17:17 2013

@author: mkieszek
"""
from openerp import tools
from openerp.osv import fields, osv




class cd_product_image(osv.Model):
    _name="cd.product.image"

    _columns = {
        'name': fields.char('Name', required=True),
        'image': fields.binary('Image', required=True),
        'product_id': fields.many2one('product.product', 'Product'),
     }
    
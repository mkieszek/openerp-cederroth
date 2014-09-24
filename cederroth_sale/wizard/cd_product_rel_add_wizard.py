# -*- coding: utf-8 -*-
'''
Created on 13 cze 2014

@author: sony
'''

from openerp.osv import osv,fields
from openerp.addons.mail.mail_message import decode
import pdb

class cd_product_rel_add_wizard(osv.osv_memory):
    _name = 'cd.product.rel.add.wizard'
    _description = 'Add products to promotion'
    
    _columns = {
                'product_ids': fields.many2many('product.product', string='Products'),       
                }
    
    def create(self, cr, uid, data, context=None):
        product_rel_obj = self.pool.get('cd.product.rel')
        product_obj = self.pool.get('product.product')
        
        for product_id in data['product_ids'][0][2]:
            product = product_obj.browse(cr, uid, product_id)
            if product_rel_obj.search(cr, uid, [('product_id','=',product_id),('promotions_id','=',context['active_id'])]):
                raise osv.except_osv(decode('Ostrzeżenie'), decode('Produkt: %s został już dodany.')%product.name)
            vals = {}
            vals = {
                    'product_id': product_id,
                    'promotions_id': context['active_id'],
                    
                    }
            product_rel_obj.create(cr, uid, vals, context=None)
                
        return False
    
    def add_products(self, cr, uid, ids, context=None):
        res = { 'type': 'ir.actions.client', 'tag': 'reload' }
        return res

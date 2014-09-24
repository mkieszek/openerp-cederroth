# -*- coding: utf-8 -*-
'''
Created on 27 kwi 2014

@author: sony
'''

import datetime
import base64
import pdb

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
    
from openerp.osv import osv, fields

LISTING_STATUS = [('0','Aktywny'),('1','Do wprowadzenia'),('2','Do zdjęcia'),('3','Nie aktywny')]
COL_TYPE = [(0, 'MOVEX'),(1, 'CENA'),(2, 'EAN'), (3, 'Format')]
class cd_cogs_import(osv.osv_memory):
    _name = 'cd.cogs.import'
    _description = "Import COGS"
    _columns = {
                'file_import': fields.binary('Import file', readolny=True),
                }
    
    def cogs_import(self, cr, uid, ids, context=None):
        #import z pliku
        #pdb.set_trace()
        record = self.browse(cr, uid, ids, context=context)[0]
        
        csvfile = StringIO(base64.b64decode(record.file_import))
        product_obj = self.pool.get('product.product')
        
        for row in csvfile:
            row = row.replace('\r\n', '')
            row_tab = row.split(";")
            movex = row_tab[0]
            try:
                cogs = float(row_tab[1].replace(',','.'))
            except ValueError:
                cogs = 0.0
            
            product_id = product_obj.search(cr, uid, [('default_code','=', movex)])
            
            if product_id:
                product_obj.write(cr, uid, product_id, {'price_cogs': cogs})
            
            
        return True
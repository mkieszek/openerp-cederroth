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
class cd_listing_import(osv.osv_memory):
    _name = 'cd.listing.import'
    _description = "Import listingu"
    _columns = {
                'name' : fields.char('Name'),
                'state': fields.selection([('choose', 'choose'),('get', 'get')]),
                'file_import': fields.binary('Import file', readolny=True),
                'listing_count': fields.integer('Listing count'),
                'client_id': fields.many2one('res.partner', 'Customer', required=True),
                'movex_col' : fields.integer('MOVEX col'),
                'ean_col': fields.integer('EAN col'),
                'price_col': fields.integer('Price col'),
                'format_col': fields.integer('Format col')
                }
    _defaults = { 
        'state': 'choose',
        'name': 'lang.tar.gz',
    }
    
    def create(self, cr, uid, vals, context=None):
        
        export = super(cd_listing_import, self).create(cr, uid, vals, context=context)
        return export
    
    def listing_import(self, cr, uid, ids, context=None):
        #import z pliku
        #pdb.set_trace()
        record = self.browse(cr, uid, ids, context=context)[0]
        
        csvfile = StringIO(base64.b64decode(record.file_import))
        
        client = record.client_id
        client_id = client.id
        
        partner_obj = self.pool.get('res.partner')
        product_obj = self.pool.get('product.product')
        listing_obj = self.pool.get('cd.listing')
        format_obj = self.pool.get('cd.client.format')
        
        change_date = datetime.datetime.now()
        listing_count = 0
        
        client = partner_obj.browse(cr, uid, client_id)
        
        listing_ids = listing_obj.search(cr, uid, [('client_id','=', client_id)])
        if listing_ids:
            listing_obj.write(cr, uid, listing_ids, {'status_l' : '3'})
        
        error_products = ''
        #pdb.set_trace()
        
        for row in csvfile:
            product_id = 0
            price = 0.0
            format = 0
            format_id = 0
            
            row = row.replace('\r\n', '')
            row_tab = row.split(";") 
            
            #poprawianie kodów movex w produktach
            p_id = 0
            if record.movex_col != 0:
                product_movex = row_tab[record.movex_col - 1].strip()
                p_id = product_obj.search(cr, uid, [('default_code', '=', product_movex)])
                if not p_id:
                    product_movex = product_movex.lstrip("0")
                    p_id = product_obj.search(cr, uid, [('default_code', 'ilike', '%'+product_movex)])
                    #if p_id:
                    #    p_vals = {'default_code' : row_tab[record.movex_col - 1].strip()}
                    #    product_obj.write(cr, uid, p_id, p_vals)
            
            if record.movex_col != 0:
            #    product_movex = row_tab[record.movex_col - 1].strip()
            #    product_id = product_obj.search(cr, uid, [('default_code', '=', product_movex)])
                product_id = p_id
            else:
                product_ean = row_tab[record.ean_col - 1].strip()
                product_id = product_obj.search(cr, uid, [('ean13', '=', product_ean)])
                
            #pdb.set_trace()
            price = row_tab[record.price_col - 1].replace(',', '.').strip()
            
            if record.format_col != 0:
                format = row_tab[record.format_col - 1].strip()
                format_id = format_obj.search(cr, uid, [('client_id', '=', client_id),('name', '=', format)])
                
            #client_id = partner_obj.search(cr, uid, [('ref','=', client_movex)])
            
            if product_id:
                if format_id != 0:
                    listing_id = listing_obj.search(cr, uid, [('client_id', '=', client_id),('product_id','=',product_id[0]),('fclient_id','=',format_id)])
                    if listing_id:
                        listing_vals = {'price_sale': price,'status_l' : '0'}
                        listing_obj.write(cr, uid, listing_id, listing_vals)
                    else:
                        listing_vals = {'product_id' : product_id[0],
                                        'client_id': client_id,
                                        'price_sale' : price,
                                        'status_l' : '0',
                                        'change_date' : change_date,
                                        'fclient_id': format_id}
                        listing_obj.create(cr, uid, listing_vals)
                        
                    listing_count = listing_count + 1
                else:
                    if client.cformat:
                        for client_format in client.cformat:
                            listing_id = listing_obj.search(cr, uid, [('client_id', '=', client_id),('product_id','=',product_id[0]),('fclient_id','=',client_format.id)])
                            if listing_id:
                                listing_vals = {'price_sale': price,'status_l' : '0'}
                                listing_obj.write(cr, uid, listing_id, listing_vals)
                            else:
                                listing_vals = {'product_id' : product_id[0],
                                                'client_id': client_id,
                                                'price_sale' : price,
                                                'status_l' : '0',
                                                'change_date' : change_date,
                                                'fclient_id': client_format.id}
                                listing_obj.create(cr, uid, listing_vals)
                    else:
                        listing_id = listing_obj.search(cr, uid, [('client_id', '=', client_id),('product_id','=',product_id[0])])
                        if listing_id:
                            listing_vals = {'price_sale': price,'status_l' : '0'}
                            listing_obj.write(cr, uid, listing_id, listing_vals)
                        else:
                            listing_vals = {'product_id' : product_id[0],
                                            'client_id': client_id,
                                            'price_sale' : price,
                                            'status_l' : '0',
                                            'change_date' : change_date
                                            }
                            listing_obj.create(cr, uid, listing_vals)
                    listing_count = listing_count + 1
            else:
                if record.movex_col != 0:
                    error_products += product_movex + ', '
                else:
                    error_products += product_ean + ', '

                
                #pdb.set_trace()
        print 'brak produktów - ' + error_products
        #pdb.set_trace()
        return True

# -*- coding: utf-8 -*-
'''
Created on 16 maj 2014

@author: sony
'''

from openerp.osv import fields, osv
from openerp.osv.orm import Model
from datetime import timedelta
from openerp.addons.mail.mail_message import decode
import calendar
import datetime
import pdb
import xlrd
import os
import re

class cd_sale_data_import(osv.Model):
    _name = "cd.sale.data.import"
    _description = "Sale data import"
    
    _columns = {
                'filename' : fields.char('Nazwa pliku', size=255),
                'import_file' : fields.binary('Plik do importu', required=True),
                'date_from': fields.datetime('Data od', required=True),
                'date_to': fields.datetime('Data do', required=True),
                'sale_data_ids': fields.one2many('cd.sale.data', 'sale_import_id', 'Dane'),
                'create_uid': fields.many2one('res.users', 'Twórca'),
                'create_date': fields.datetime('Data utworzenia'),
    }
    
    def create(self, cr, uid, data, context=None):        
        date_from = data['date_from']
        date_to = data['date_to']
        if date_from > date_to:
            raise osv.except_osv(decode('Ostrzeżenie'), decode('Niepoprawne wypełnione pola Data'))
        
        if self.search(cr, uid, [('date_to','>',date_from),('date_from','<',date_from)]) or self.search(cr, uid, [('date_to','>',date_to),('date_from','<',date_to)]):
            raise osv.except_osv(decode('Ostrzeżenie'), decode('Nie można dodać importu w tym okresie'))
        
        import_id = super(cd_sale_data_import, self).create(cr, uid, data, context=context)
        self.import_xls(cr, uid, [import_id], context)
        return import_id
    
    def unlink(self, cr, uid, ids, context=None):
        sale_data_obj = self.pool.get('cd.sale.data')
        sale_data_ids = sale_data_obj.search(cr, uid, [('sale_import_id','in',ids)])
        sale_data_obj.unlink(cr, uid, sale_data_ids, context=context)
        
        import_id = super(cd_sale_data_import, self).unlink(cr, uid, ids, context=context)
        
        return import_id
    
    def import_file(self, file):
        return True
    
    def import_xls(self, cr, uid, ids, context=None):
        #pdb.set_trace()
        w = self.browse(cr, uid, ids, context=context)[0]
        """
        if w.import_file == False:
            return False
        
        file_name = "/home/shares/openerp_files/import/" + w.filename
        """
        fh = open(w.filename, "wb")
        #pdb.set_trace()
        fh.write(w.import_file.decode('base64'))
        fh.close()
                    
        workbook = xlrd.open_workbook(w.filename)
        worksheet = workbook.sheet_by_name('Sheet1')
        num_rows = worksheet.nrows - 1
        num_cells = worksheet.ncols - 1
        curr_row = 1
        
        client_obj = self.pool.get('res.partner')
        product_obj = self.pool.get('product.product')
        plan_product_obj = self.pool.get('cd.plan.product')
        sale_data_obj = self.pool.get('cd.sale.data')
        bom_obj = self.pool.get('mrp.bom')
        listing_obj = self.pool.get('cd.listing')
                
        set_key = {}
        set_movex = []
        
        bom_ids = bom_obj.search(cr, uid, [('bom_id','=',False)])
        for bom in bom_obj.browse(cr, uid, bom_ids):
            set_key[bom.product_id.default_code] = bom.id
            set_movex.append(bom.product_id.default_code)
            
        while curr_row < num_rows:
            curr_row += 1
            row = worksheet.row(curr_row)
            year = int(row[0].value)
            month = int(row[1].value)
            
            retailer_tab = row[2].value.split(' ')
            retailer_movex = retailer_tab[0]
            retailer_name = ""
            for n in retailer_tab[1:]:
                retailer_name += n
            
            item_tab = row[4].value.split(' ')
            item_movex = item_tab[0]
            if item_movex in set_movex:
                bom_ids = bom_obj.search(cr, uid, [('bom_id','=',set_key[item_movex])])
                for bom in bom_obj.browse(cr, uid, bom_ids):
                    listing_ids = listing_obj.search(cr, uid, [('client_id.ref','=',retailer_movex),('product_id','=',bom.product_id.id)])
                    if listing_ids:
                        listing_price = listing_obj.browse(cr, uid, listing_ids)[0].price_sale

                        sale_value = {
                                      'year': year,
                                      'month' : month,
                                      'retailer' : retailer_movex,
                                      'item' : bom.product_id.default_code,
                                      'net_value' : listing_price*bom.product_qty,
                                      'qty': bom.product_qty,
                                      'sale_import_id': w.id,
                                      }
                        sale_data_obj.create(cr, uid, sale_value,)
            else:
                item_name = ""
                for n in item_tab[1:]:
                    item_name += n
                
                net_value = row[5].value
                qty = row[6].value

                sale_value = {
                              'year': year,
                              'month' : month,
                              'retailer' : retailer_movex,
                              'item' : item_movex,
                              'net_value' : net_value,
                              'qty': qty,
                              'sale_import_id': w.id,
                              }
                sale_data_obj.create(cr, uid, sale_value,)
            
            
            #if client_id and product_id:
                
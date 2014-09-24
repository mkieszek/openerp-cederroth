# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 15:21:58 2013

@author: mkieszek
"""
import csv
import itertools
import logging
import operator
import base64

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import psycopg2

from openerp.osv import osv, fields
from openerp.tools.translate import _
import pdb

class cd_csv2products(osv.Model):
    _name = 'cd.csv2products'
    
    _columns = {
        'csv': fields.binary('CSV file')    
    }
    
    
    def import_file(self, cr, uid, ids, context=None):
        
        #pdb.set_trace()
        record = self.browse(cr, uid, ids, context=context)[0]
        csvfile = StringIO(base64.b64decode(record.csv))

        i = 0 
        
        while 1:
            row = csvfile.readline()
            row_tab = row.split(";") 
            if not row:
                break
            
            
            categ_ids = self.pool.get('product.category').search(cr, uid, [('name','ilike',row_tab[0])], context=context)            
            
            vals_product = {}
            
           
            
            vals_product["categ_id"] = categ_ids and categ_ids[0] or False
            vals_product["name"] = row_tab[1]
            vals_product["name_40"] = row_tab[2]
            vals_product["name_20_1"] = row_tab[3]
            vals_product["name_20_2"] = row_tab[4]
            vals_product["paragon_18"] = row_tab[5]
            
            order_ids = self.pool.get('product.ul').search(cr, uid, [('name','ilike',row_tab[6])], context=context)
            vals_product["order_ul"] = order_ids and order_ids[0] or False
            
            manufacturer_ids = self.pool.get('res.partner').search(cr, uid, [('name','ilike',row_tab[7])], context=context)
            vals_product["manufacturer_id"] = manufacturer_ids and manufacturer_ids[0] or False

           #taxes_ids = self.pool.get('account.tax').search(cr, uid, [('name','ilike',row_tab[9]),('tax_code_id','=',3)], context=context)
           #vals_product["taxes_id"] = taxes_ids[0]
            
            #vals_product["vat_2010"] = row_tab[10]
            
            vals_product["pkwiu2008"] = row_tab[11]
            #vals_product["availability_date"] = row_tab[12]
            vals_product["shelf_life"] = row_tab[13]
            vals_product["name_en"] = row_tab[14]
            vals_product["hts_code"] = row_tab[15]
            
            vals_product["pkwiu1997"] = row_tab[17]
            vals_product["default_code"] = row_tab[18]
            vals_product["nr_dostawcy"] = row_tab[19]
            vals_product["grupa_ekg"] = row_tab[20]
            
            
            
            pack_types = self.pool.get('cd.pack.type').search(cr, uid, [('name','ilike',row_tab[21])], context=context)
            if pack_types :              
                vals_product["pack_type"] = pack_types and pack_types[0]
            else :
                new_packtype_id = self.pool.get('cd.pack.type').create(cr, uid, {"name":row_tab[21]}, context=context)
                vals_product["pack_type"] = new_packtype_id
                
                
            country_ids = self.pool.get('res.country').search(cr, uid, [('name','ilike',row_tab[22])], context=context)
            vals_product["origin_country"] = country_ids and country_ids[0]
            
            vals_product["etykieta_regalowa_15"] = row_tab[23]
            vals_product["etykieta_regalowa_4"] = row_tab[24]
            vals_product["kod_cn"] = row_tab[25]
            vals_product["kod_eu_factor"] = row_tab[26]
            vals_product["kod_eu_unit"] = row_tab[27]
            vals_product["temp_min"] = row_tab[28]
            vals_product["temp_max"] = row_tab[29]
            
            alcohol = row_tab[30]
            alcohol = alcohol[:-1]
            
            
            try:
                alcohol = float(alcohol)/100
                vals_product["alcohol"] = alcohol
            except:
                pass
            
            vals_product["height"] = row_tab[32]
            vals_product["width"] = row_tab[33]
            vals_product["length"] = row_tab[34]
            vals_product["weight_net"] = row_tab[35]
            vals_product["weight"] = row_tab[36]
            vals_product["ean"] = row_tab[37]
            vals_product["volume"] = row_tab[38]
            
            
            product_id = self.pool.get('product.product').create(cr, uid, vals_product, context=context)
            
            
            vals_box = {}
            vals_box["product_id"] = product_id
            
            ul_ids = self.pool.get('product.ul').search(cr, uid, [('type', 'ilike', 'box')])
            vals_box["ul"] = ul_ids and ul_ids[0] or False
            
            vals_box["height"] = row_tab[39]
            vals_box["width"] = row_tab[40]
            vals_box["length"] = row_tab[41]
            vals_box["weight_ul"] = row_tab[42]
            vals_box["qty"] = row_tab[43]
            vals_box["ean_code"] = row_tab[44]
            vals_box["rows"] = row_tab[45]
            vals_box["ul_qty"] = row_tab[46]
            vals_box["weight"] = row_tab[47]
            self.pool.get('product.packaging').create(cr, uid, vals_box, context=context)
            
            
            vals_pallet = {}
            vals_pallet["product_id"] = product_id  
            
            ul_ids = self.pool.get('product.ul').search(cr, uid, [('type', 'ilike', 'pallet')])
            vals_pallet["ul"] = ul_ids and ul_ids[0] or False
            
            vals_pallet["height"] = row_tab[48]
            vals_pallet["width"] = row_tab[49]
            vals_pallet["length"] = row_tab[50]
            vals_pallet["weight_ul"] = row_tab[51]
            vals_pallet["box_qty"] = row_tab[52]
            vals_pallet["rows"] = row_tab[53]
            vals_pallet["ul_qty"] = row_tab[54]
            vals_pallet["weight"] = row_tab[55]
            vals_pallet["qty"] = row_tab[56]
            vals_pallet["layer_qty"] = row_tab[57]
            
            self.pool.get('product.packaging').create(cr, uid, vals_pallet, context=context)
            
            vals_pack = {}
            vals_pack["product_id"] = product_id
            
            ul_ids = self.pool.get('product.ul').search(cr, uid, [('type', 'ilike', 'pack')])
            vals_pack["ul"] = ul_ids and ul_ids[0] or False
            
            #vals_pack["height"] = row_tab[58]
            #vals_pack["width"] = row_tab[59]
            #vals_pack["length"] = row_tab[60]
            
            
            i=i+1
            print i
            
    

# -*- coding: utf-8 -*-
'''
Created on 3 kwi 2014

@author: sony
'''
from openerp.osv import osv, fields
from openerp.tools.translate import _
import datetime
import base64
import pdb
from __builtin__ import len

LISTING_STATUS = [('0','Aktywny'),('1','Do wprowadzenia'),('2','Do zdjęcia'),('3','Nie aktywny')]

class cd_listing_export(osv.osv_memory):
    _name = 'cd.listing.export'
    _description = "Listing export"
    _columns = {
                'name' : fields.char('Name'),
                'state': fields.selection([('choose', 'choose'),('get', 'get')]),
                'file_export': fields.binary('Export file', readolny=True),
                }
    _defaults = { 
        'state': 'choose',
        'name': 'lang.tar.gz',
    }
    
    def create(self, cr, uid, vals, context=None):
        
        export = super(cd_listing_export, self).create(cr, uid, vals, context=context)
        return export
    
    def export_listings(self, cr, uid, ids, context=None):
        w = self.browse(cr, uid, ids, context=context)[0]
        export = self.get_listing_report(cr, uid, context['active_ids'])
                    
        out = base64.encodestring(export)
        today_string = datetime.datetime.today().strftime('%Y%m%d')
        file_name = '%s%s.csv' % ('listing_export', today_string)
        self.write(cr, uid, ids, {'file_export': out,
                                  'state': 'get',
                                  'name': file_name}, context=context)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cd.listing.export',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': w.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
    def get_listing_report(self, cr, uid, active_ids):
        
        listing_obj = self.pool.get('cd.listing')
        partner_obj = self.pool.get('res.partner')
        
        client_ids = []
        product_ids = active_ids
        
        listing_list = []
        
        
        #for listing in listing_obj.browse(cr, uid, active_ids):
        #    if listing.product_id.id not in product_ids:
        #        product_ids.append(listing.product_id.id)
        
        #pobieramy klientow trade'u i farmacji
        trade_id = self.pool.get('crm.case.section').search(cr, uid, [('code', 'ilike', 'trade')])
        trade_client_ids = partner_obj.search(cr, uid, [('section_id','in', trade_id)])
        
        farmacja_id = self.pool.get('crm.case.section').search(cr, uid, [('code', 'ilike', 'trade')])
        farmacja_client_ids = partner_obj.search(cr, uid, [('section_id','in', farmacja_id)])
        
        sieci_id = self.pool.get('crm.case.section').search(cr, uid, [('code', 'ilike', 'sieci')])
        sieci_client_ids = partner_obj.search(cr, uid, [('section_id','in', sieci_id)], order='name')
        
        header_line = {
                       'product_id': 'Produkt',
                       'trade': 'Trade',
                       'farmacja': 'Farmacja',
                       }
        for client in partner_obj.browse(cr, uid, sieci_client_ids):
            if client.cformat:
                str_id = str(client.id)
                for format in client.cformat:
                    header_line[str_id+'-'+str(format.id)] = client.name + ' - ' + format.name
            else:
                header_line[str(client.id)] = client.name
        
        
        
        for product_id in product_ids:
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            
            listing_line = {'product_id': (product.default_code or '')  + ' ' + product.name}
                        
            trade_listing_ids = listing_obj.search(cr, uid, [('product_id', '=', product_id),('client_id','in', trade_client_ids)])
            trade_count = len(trade_client_ids)
            listing_line['trade'] = trade_count
            
            farmacja_listing_ids = listing_obj.search(cr, uid, [('product_id', '=', product_id),('client_id','in', farmacja_client_ids)])
            farmacja_count = len(farmacja_listing_ids)
            listing_line['farmacja'] = farmacja_count
            
            for client in partner_obj.browse(cr, uid, sieci_client_ids):                
                listing_ids = listing_obj.search(cr, uid, [('product_id', '=', product_id),('client_id','=', client.id)])
                
                for listing in listing_obj.browse(cr, uid, listing_ids):
                    if listing.fclient_id:
                        listing_line[str(client.id)+'-'+str(listing.fclient_id.id)] = LISTING_STATUS[int(listing.status_l)][1]
                    else:
                        listing_line[str(client.id)] = LISTING_STATUS[int(listing.status_l)][1]
            
            listing_list.append(listing_line)
        
        
        for listing_line in listing_list:
            for key in header_line.iterkeys():
                if key not in listing_line:
                    listing_line[key] = ''
        
		row_format = '"%(product_id)s";"%(trade)s";"%(farmacja)s";'
        
        for key in iter(sorted(header_line.keys())):
            if key not in ['product_id', 'trade', 'farmacja']:
                row_format += '"%('+key+')s";'
        
        row_format = row_format[:-1] + '\n'
        
        header_row = row_format % header_line
        
        result = header_row.encode('cp1250')
        
        try:
            for listing_line in listing_list:
                listing_line['94-44'] = listing_line['94-44'].decode('utf8')
                result += (row_format % listing_line).encode('cp1250')
        except:
            raise
                
        return result
        

# -*- coding: utf-8 -*-
'''
Created on 27 cze 2014

@author: mbereda
'''

from openerp.osv import osv, fields
from openerp.addons.mail.mail_message import decode
from openerp import tools
import pdb

class cd_product_history_wizard(osv.Model):
    _name = 'cd.product.history.wizard'
    _auto = False
    _description = "Product History"
    
    _columns = {
                'product_id': fields.many2one('product.product', 'Produkt', readonly=True),
                'sale_date': fields.char('Data'),
                'count': fields.integer('Ilość'),
                'partner_id': fields.many2one('res.partner', "Partner"),
                }
    
    def init(self, cr, context=None):
        tools.drop_view_if_exists(cr, 'cd_product_history_wizard')
        cr.execute("""
            CREATE OR REPLACE VIEW cd_product_history_wizard AS (

            SELECT csd.id, csd.item, csd.retailer, csd.net_value, csd.qty as count, rp.id as partner_id, pp.id as product_id, to_char(year,'0000')||'-'||to_char(month,'00') as sale_date
                FROM cd_sale_data as csd
                LEFT JOIN res_partner as rp ON rp.ref = csd.retailer
                LEFT JOIN product_product as pp on pp.default_code=csd.item
                WHERE to_char(year,'0000')||'-'||to_char(month,'00') >= (to_char(localtimestamp - interval '18 months', 'YYYY')||'-'||to_char(localtimestamp - interval '18 months', 'MM'))

            )""")

    def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False):
        if 'product_id' in context:
            domain.append(('product_id','=',context['product_id']))
        if 'client_id' in context:
            domain.append(('partner_id','=',context['client_id']))
        res = super(cd_product_history_wizard,self).read_group(cr, uid, domain, fields, groupby, offset=0, limit=None, context=context, orderby=False)
        return res
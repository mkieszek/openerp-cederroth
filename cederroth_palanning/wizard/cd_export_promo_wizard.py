# -*- coding: utf-8 -*-
'''
@author: mbereda
'''
from openerp.osv import osv, fields
from openerp.tools.translate import _
import datetime
import base64
import pdb
from __builtin__ import len
from openerp.addons.mail.mail_message import decode

class cd_export_promo(osv.osv_memory):
    _name = 'cd.export.promo'
    _description = "Promotions export"
    _columns = {
                'name' : fields.char('Name'),
                'state': fields.selection([('choose', 'choose'),('get', 'get')]),
                'file_export': fields.binary('Export file', readolny=True),
                }
    _defaults = { 
        'state': 'choose',
        'name': 'lang.tar.gz',
    }
        
    def export_promotions(self, cr, uid, ids, context=None):
        w = self.browse(cr, uid, ids, context=context)[0]
        export = self.get_promotions_report(cr, uid, context['active_ids'])
                    
        out = base64.encodestring(export)
        today_string = datetime.datetime.today().strftime('%Y%m%d')
        file_name = '%s%s.csv' % ('promotions_export', today_string)
        self.write(cr, uid, ids, {'file_export': out,
                                  'state': 'get',
                                  'name': file_name}, context=context)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cd.export.promo',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': w.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
        
    def get_promotions_report(self, cr, uid, active_ids):
        promo_obj = self.pool.get('cd.promotions')
        promo_ids = active_ids
        
        header_line = {
                       'client_id': 'Klient',
                       'create_uid': 'Odpowiedzialny',
                       'count_all' : ('Ilość sklepów').decode('utf-8'),
                       'count_promo': ('Ilość sklepów objętych promocją').decode('utf-8'),
                       'brand': 'Marka',
                       'product_line': 'Linia produktowa',
                       'product': 'Produkt',
                       'promo_type' : 'Typ promocji',
                       'promo_m': 'Mechanizm promocji',
                       'detal_price': 'Spodziewana cena detaliczna',
                       'communication_form' : 'Forma komunikacji',
                       'discount_from': 'Rabaty od',
                       'promo_from': 'Promocja od',
                       'promo_to' : 'Promocja do',
                       'distribution': 'Zatowarowanie',
                       'state': 'Status',
                       'exposition': 'Dodatkowa ekspozycja',
                       'exposition_count': ('Ilość sklepów z dodatkową ekspozycją').decode('utf-8'),
                       'ph_task': 'Zadania PH',
                       'monit_merchandising': 'Monitoring Merchandising',
                       'task_merchandising': 'Zadania Merchandising',
                       'pos': 'POS',
                       'gross_sales': 'Gross sales',
                       'discount_front': 'Rabat front',
                       'discount_front_contract': 'Rabat promo kontraktowy',
                       'discount_front_budg': ('Rabat promo pozabudżetowy').decode('utf-8'),
                       'nsh': 'NSH',
                       'trade_promo': 'Trade promo',
                       'nsv': 'NSV',
                       'cogs': 'COGS',
                       'other_cogs': 'Other COGS',
                       'gp': 'GP',
                       'gpp': 'GP %',
                       'coop': 'COOP',
                       'other_mark': 'Other Marketing',
                       'contrib': 'Contrib.',
                       'contrib_p': 'Contrib. %',
                       }
        promo_list = []
        for promo in promo_obj.browse(cr, uid, promo_ids):
            communication_form = ''
            count_all = 0
            
            format_ids = self.pool.get('cd.client.format').search(cr, uid, [('client_id', '=', promo.client_id.id)])
            for format in self.pool.get('cd.client.format').browse(cr, uid, format_ids):
                count_all += format.shops;
                
            for item in promo.communication_ids:
                if communication_form != '':
                    communication_form += ', '
                communication_form += item.name
                    
            for product in promo.product_rel_ids:
                promotion_rules = ''
                if product.promotions_id.promotion_rules:
                    promotion_rules = (product.promotions_id.promotion_rules)
                monit_merch = 'Nie'
                if product.promotions_id.monitor_merchand == True:
                    monit_merch = 'Tak'
                
                task_ph = ''
                for task in product.promotions_id.task_sale_ids:
                    if task_ph != '':
                        task_ph += ', '
                    task_ph += task.name                    
                task_merch = ''
                for task in product.promotions_id.task_merchandising_ids:
                    if task_merch != '':
                        task_merch += ', '
                    task_merch += task.name
                display = ''
                for disp in product.promotions_id.display_ids:
                    if display != '':
                        display += ', '
                    display += disp.name
        
                pos_str = ''
                for pos in product.promotions_id.cost_promotions_ids:
                    if pos.pos:
                        if pos_str != '':
                            pos_str += ', '
                        pos_str += pos.cost_data_id.name
                promo_line = {
                              'client_id': product.promotions_id.client_id.name,
                              'create_uid': product.promotions_id.create_uid.name,
                              'count_all' : count_all,
                              'count_promo': product.promotions_id.promo_format_count,
                              'brand': product.promotions_id.product_category.name,
                              'product_line': product.product_id.categ_id.name or '',
                              'product': product.product_id.name,
                              'promo_type' : promo.type_promotions_id.name,
                              'promo_m': promotion_rules,
                              'detal_price': product.retail_price,
                              'communication_form': communication_form,
                              'discount_from': product.promotions_id.discount_from,
                              'promo_from': product.promotions_id.start_date,
                              'promo_to' : promo.stop_date,
                              'distribution' : promo.distribution or '',
                              'state': product.promotions_id.stage_id.name,
                              'exposition': display,
                              'exposition_count': product.promotions_id.display_count,
                              'ph_task': task_ph,
                              'monit_merchandising': monit_merch,
                              'task_merchandising': task_merch,
                              'pos': pos_str,
                              'gross_sales': product.promotions_id.gross_sales or 0.0,
                              'discount_front': product.promotions_id.discount_front or 0.0,
                              'discount_front_contract': product.promotions_id.discount_promo_contract or 0.0,
                              'discount_front_budg': product.promotions_id.discount_promo_budget or 0.0,
                              'nsh': product.promotions_id.nsh or 0.0,
                              'trade_promo': product.promotions_id.trade_promo or 0.0,
                              'nsv': product.promotions_id.nsv or 0.0,
                              'cogs': product.promotions_id.cogs or 0.0,
                              'other_cogs': product.promotions_id.other_cogs or 0.0,
                              'gp': product.promotions_id.gp or 0.0,
                              'gpp': product.promotions_id.gpp or 0.0,
                              'coop': product.promotions_id.coop or 0.0,
                              'other_mark': product.promotions_id.other_marketing or 0.0,
                              'contrib': product.promotions_id.contrib or 0.0,
                              'contrib_p': product.promotions_id.contribp or 0.0,
                              }
                promo_list.append(promo_line)

        for promo_line in promo_list:
            for key in header_line.iterkeys():
                if key not in promo_line:
                    promo_line[key] = ''

        row_format = '"%(client_id)s";"%(create_uid)s";"%(count_all)s";"%(count_promo)s";"%(brand)s";"%(product_line)s";"%(product)s";"%(promo_type)s";"%(promo_m)s";"%(detal_price)s";"%(communication_form)s";"%(discount_from)s";"%(promo_from)s";"%(promo_to)s";"%(distribution)s";"%(state)s";"%(exposition)s";"%(exposition_count)s";"%(ph_task)s";"%(monit_merchandising)s";"%(task_merchandising)s";"%(pos)s";"%(gross_sales)s";"%(discount_front)s";"%(discount_front_contract)s";"%(discount_front_budg)s";"%(nsh)s";"%(trade_promo)s";"%(nsv)s";"%(cogs)s";"%(other_cogs)s";"%(gp)s";"%(gpp)s";"%(coop)s";"%(other_mark)s";"%(contrib)s";"%(contrib_p)s";'
        
        for key in iter(sorted(header_line.keys())):
            if key not in ['client_id', 'create_uid', 'count_all', 'count_promo', 'brand', 'product_line', 'product', 'promo_type', 'promo_m', 'detal_price', 'communication_form', 'promo_from', 'discount_from', 'promo_to','distribution', 'state',
                            'exposition', 'exposition_count', 'ph_task', 'monit_merchandising', 'task_merchandising', 'pos', 'gross_sales', 'discount_front', 'discount_front_contract', 'discount_front_budg', 
                            'nsh', 'trade_promo', 'nsv', 'cogs', 'other_cogs', 'gp', 'gpp', 'coop', 'other_mark', 'contrib', 'contrib_p']:
                row_format += '"%('+key+')s";'
        
        row_format = row_format[:-1] + '\n'
        
        header_row = row_format % header_line
        
        result = header_row.encode('cp1250')
        
        try:
            for promo_line in promo_list:
                promo_line = promo_line
                result += (row_format % promo_line).encode('cp1250')
        except:
            raise
        
        return result
        

# -*- encoding: utf-8 -*-
#########################################################################
# Copyright (C) 2009  Sharoon Thomas, Open Labs Business solutions      #
# Copyright (C) 2011 Akretion Sébastien BEAU sebastien.beau@akretion.com#
#                                                                       #
#This program is free software: you can redistribute it and/or modify   #
#it under the terms of the GNU General Public License as published by   #
#the Free Software Foundation, either version 3 of the License, or      #
#(at your option) any later version.                                    #
#                                                                       #
#This program is distributed in the hope that it will be useful,        #
#but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#GNU General Public License for more details.                           #
#                                                                       #
#You should have received a copy of the GNU General Public License      #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.  #
#########################################################################
import os
import shutil
import logging
import pdb

from openerp.addons.mail.mail_message import decode
from openerp.osv.orm import Model
from openerp.osv import fields, osv

class product_product(Model):
    _inherit = "product.product"
    

    def _product_count(self, cr, uid, ids, product, arg, context=None):
        
        res = dict(map(lambda x: (x,{'product_count': 0}), ids))

        try:
            for product in self.browse(cr, uid, ids, context):
                i=0
                all = 0
                ul_box = self.pool.get('product.ul').search(cr, uid, [('type', 'ilike', 'box')])
                box_id = self.pool.get('product.packaging').search(cr, uid, [('product_id', '=', product.id),('ul','=', ul_box)])
                ul_pallet = self.pool.get('product.ul').search(cr, uid, [('type', 'ilike', 'pallet')])
                pallet_id = self.pool.get('product.packaging').search(cr, uid, [('product_id', '=', product.id),('ul','=', ul_pallet)])
                box = 0
                if box_id:
                    box = self.pool.get('product.packaging').browse(cr, uid, box_id)[0]
                pallet = 0
                if pallet_id:
                    pallet = self.pool.get('product.packaging').browse(cr, uid, pallet_id)[0]              
                
                all = all+1
                if product.name_40 :
                    i=i+1
                all = all+1    
                if product.name_20_1 :
                    i=i+1
                all = all+1
                if product.name_20_2 :
                    i=i+1
                all = all+1
                if product.paragon_18 :
                    i=i+1              
                all = all+1
                if product.order_ul :
                    i=i+1
                all = all+1
                if product.pkwiu2008 :
                    i=i+1
                all = all+1
                if product.shelf_life :
                    i=i+1
                all = all+1
                if product.name_en :
                    i=i+1
                all = all+1
                if product.hts_code :
                    i=i+1
                all = all+1
                if product.default_code :
                    i=i+1
                all = all+1
                if product.nr_dostawcy_kaufland :
                    i=i+1
                all = all+1
                if product.nr_dostawcy_makro_real:
                    i=i+1
                all = all+1
                if product.nr_dostawcy_auchan:             
                    i=i+1
                all = all+1
                if product.nr_dostawcy_selgros:             
                    i=i+1
                all = all+1
                if product.grupa_ekg :
                    i=i+1
                all = all+1             
                if product.pack_type :
                    i=i+1     
                all = all+1
                if product.origin_country :
                    i=i+1      
                all = all+1
                if product.etykieta_regalowa_15 :
                    i=i+1
                all = all+1             
                if product.etykieta_regalowa_4 :
                    i=i+1
                all = all+1             
                if product.kod_cn :
                    i=i+1
                all = all+1             
                if product.kod_eu_factor :
                    i=i+1
                all = all+1                                 
                if product.kod_eu_unit :
                    i=i+1
                all = all+1                                 
                if product.temp_min :
                    i=i+1
                all = all+1                                 
                if product.temp_max :
                    i=i+1
                all = all+1                      
                if product.height :
                    i=i+1
                all = all+1                                 
                if product.width :
                    i=i+1
                all = all+1                                 
                if product.length :
                    i=i+1
                all = all+1                                 
                if product.weight_net :
                    i=i+1
                all = all+1                                                     
                if product.weight :
                    i=i+1
                all = all+1                                                     
                if product.ean :
                    i=i+1
                all = all+1                                                     
                if product.volume :
                    i=i+1
                all = all+1                                                     
                if box != 0 and box.height :
                    i=i+1     
                all = all+1                                                                              
                if box != 0 and box.width :
                    i=i+1     
                all = all+1                                                                              
                if box != 0 and box.length :
                    i=i+1     
                all = all+1                                                                              
                if box != 0 and box.weight_ul :
                    i=i+1     
                all = all+1                                                                              
                if box != 0 and box.qty :
                    i=i+1        
                all = all+1                                                                      
                if box != 0 and box.ean_code :
                    i=i+1     
                all = all+1                                                                                                        
                if box != 0 and box.rows :
                    i=i+1     
                all = all+1                                                                                                        
                if box != 0 and box.ul_qty :
                    i=i+1         
                all = all+1                                                                                                                            
                if box != 0 and box.weight :
                    i=i+1  
                all = all+1                                                                                                                            
                if box != 0 and pallet.height :
                    i=i+1
                all = all+1                                                                                                                                                
                if pallet != 0 and pallet.width :
                    i=i+1  
                all = all+1                                                                                                                                                
                if pallet != 0 and pallet.length :
                    i=i+1  
                all = all+1                                                                                                                                                
                if pallet != 0 and pallet.weight_ul :
                    i=i+1  
                all = all+1                                                                                                                                                
                if pallet != 0 and pallet.box_qty :
                    i=i+1    
                all = all+1                                                                                                                          
                if pallet != 0 and pallet.rows :
                    i=i+1  
                all = all+1                                                                                                                                                
                if pallet != 0 and pallet.ul_qty :
                    i=i+1  
                all = all+1                                                                                                                                                
                if pallet != 0 and pallet.weight :
                    i=i+1  
                all = all+1                                                                                                                                                
                if pallet != 0 and pallet.qty :
                    i=i+1  
                all = all+1                                                                                                                                                
                if pallet != 0 and pallet.layer_qty :
                    i=i+1
                    
                j=float(i)/all
                
                if j*10 < 0.94:
                    res[product.id] = '0{:.0%}'.format(j)
                else:
                    res[product.id] = '{:.0%}'.format(j)
        except:
            pass
        return res
    
    
    _columns = {
        'name_40':fields.char('Nazwa handlowa 40 znaków', size=40),
        'name_20_1': fields.char('Etykieta produktowa linia 1', size=20),
        'name_20_2': fields.char('Etykieta produktowa linia 2', size=20),
        'name_30_auchan': fields.char('Etykieta produktowa 30 znaków', size=30, help="Max 30 znaków w tym gram/obj"),
        'name_35_carrefour': fields.char('Nazwa porduktu 35 znaków', size=35, help="Nazwa produktu nie może przekroczyć 35 znaków, a także musi zawierać wagę lub pojemność sztuki"),
        'paragon_18': fields.char('Opis paragon', size=18),
        'order_ul': fields.many2one('product.ul', 'Jednostka zamawiania'),
        'vat_2010': fields.many2one('account.tax', 'VAT 2010'),
        'pkwiu2008': fields.char('PKWiU 2008', size=64),
        'pkwiu1997': fields.char('PKWiU 1997', size=64),
        'shelf_life': fields.integer('Trwałość (dni)'),
        'hts_code': fields.char('Kod HTS', size=64),
        'typ_etykiety': fields.char('Typ etykiety', size=64),
        'zrodlo_dostawy': fields.char('Źródło dostawy', size=64),
        'magazyn': fields.char('Magazyn', size=64),
        'grupa_warunkow': fields.char('Grupa warunków', size=64),
        'etykieta_regalowa_15': fields.char('Etykieta regałowa', size=15),
        'kod_cn': fields.char('Kod CN (taryfy celnej)', size=64),
        'kod_eu_factor': fields.char('Kod EU Factor (taryfy celnej)', size=64),
        'kod_eu_unit': fields.char('Kod EU Unit (taryfy celnej)', size=64),
        'temp_min': fields.float('Temperatura przechowywania min'),
        'temp_max': fields.float('Temperatura przechowywania max'),
        'alcohol': fields.float('Zawartość alkoholu (0/000)'),
        'typ_artykulu': fields.char('Typ artykułu', size=64),
        'height': fields.float('Wysokość szt. (cm)'),
        'width': fields.float('Szerokość szt. (cm)'),
        'length': fields.float('Głębokość szt. (cm)'),
        'origin_country': fields.many2one('res.country', 'Kraj pochodzenia'),
        'nr_dostawcy_kaufland': fields.char('Nr dostawcy', size=64),
        'nr_dostawcy_makro_real': fields.char('Nr dostawcy', size=64),
        'nr_dostawcy_auchan': fields.char('Nr dostawcy', size=64),
        'nr_dostawcy_selgros': fields.char('Nr dostawcy', size=64),
        'grupa_ekg': fields.char('Grupa EKG', size=64),
        'grupa_warunkow_kaufland': fields.char('Grupa warunków', size=64),
        'min_log_superpharm': fields.float('Min. logistyczne produktu'),
        'manufacturer_id' : fields.many2one('res.partner','Manufacturer'),
        'availability_date' : fields.date('Availability date',readonly=True),
        'name_en': fields.char('Nazwa angielska', size=255),#bylo 30 znakow ale powiekszylem bo nie miescily sie
        'pack_type': fields.many2one('cd.pack.type','Pack type'),
        'etykieta_regalowa_4': fields.char('Etykieta regałowa 4 znaki', size=4),
        'ean': fields.float('Kod EAN'),
        'product_count' : fields.function(_product_count, string="Wypełnione", type='char', store=True),
        'listing' : fields.one2many('cd.listing','product_id', 'Listing'),
        'rodzaj_makro': fields.char('Rodzaj', help="Kolor / smak / kształt"),
        'index_producenta_hebe': fields.integer('Index producenta'),
        'kod_kr_clinique': fields.integer('Kod KR'),
        'sku_clinique': fields.integer('SKU'),
        'index_ob': fields.char('Index OB'),
        'default_code_name': fields.char('Nazwa MOVEX', size=255),
        'priorytet': fields.integer('Priorytet'),
        'product_mark': fields.many2one('product.category','Marka', required=True),
        'price_list_ids': fields.one2many('cd.price.list', 'product_id', 'Cennik'),
         }
         
    _defaults = {
        'grupa_ekg': '40',
        'nr_dostawcy_kaufland': '10052366',
        'typ_etykiety': 'PL03',
        'zrodlo_dostawy': '4 magazyn centralny',
        'magazyn': 'W',
    }
    
    def name_get(self, cr, user, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not len(ids):
            return []
        def _name_get(d):
            name = d.get('name','')
            code = d.get('default_code',False)
            if code:
                name = name
                #wyłączenie nazwy z movexem
                #name = '[%s] %s' % (code,name)
            if d.get('variants'):
                name = name
                #wyłączenie nazwy z movexem
                #name = name + ' - %s' % (d['variants'],)
            return (d['id'], name)

        partner_id = context.get('partner_id', False)

        result = []
        for product in self.browse(cr, user, ids, context=context):
            sellers = filter(lambda x: x.name.id == partner_id, product.seller_ids)
            if sellers:
                for s in sellers:
                    mydict = {
                              'id': product.id,
                              'name': s.product_name or product.name,
                              'default_code': s.product_code or product.default_code,
                              'variants': product.variants
                              }
                    result.append(_name_get(mydict))
            else:
                mydict = {
                          'id': product.id,
                          'name': product.name,
                          'default_code': product.default_code,
                          'variants': product.variants
                          }
                result.append(_name_get(mydict))
        return result
         
    def create(self, cr, uid, data, context=None):
        prod_id = super(product_product, self).create(cr, uid, data, context=context)
        
        
        packages = self.pool.get('product.packaging').browse(cr, uid, [1,2,3,4])
        #box_id = 0
        #pallet_id = 1
        #for pack in packaages:
        #    if pack.ul.type == "box":
        #        box_id = pack.id
        #    elif pack.ul.type == "pallet":
        #        pallet_id = pack.id
        pallet_id = self.pool.get('product.ul').search(cr, uid, [('name','ilike','Paleta')])
        box_id = self.pool.get('product.ul').search(cr, uid, [('name','ilike','Karton')])
        
        if box_id :         
        
            vals_box = {
                    'product_id': prod_id,
                    'ul': box_id[0],
                    'rows': 1
                    }
            self.pool.get('product.packaging').create(cr, uid, vals_box, context=context)
        
        if pallet_id : 
            
            vals_pallet = {
                    'product_id': prod_id,
                    'ul': pallet_id[0],
                    'rows': 1
                    }   
            self.pool.get('product.packaging').create(cr, uid, vals_pallet, context=context)
        
        if 'product_manager' in data and data['product_manager'] != False:
            user = self.pool.get('res.users').browse(cr, uid, data['product_manager'])
            self.message_subscribe(cr, uid, [prod_id], [user.partner_id.id], context=context)
        
        users_obj = self.pool.get('res.users')
        group_id = self.pool.get('res.groups').search(cr,uid,[('name','in',['KAM', 'Finances', 'Logistics', 'Trade Marketing Specialist', 'Trade Marketing Manager'])])
        user_ids = users_obj.search(cr,uid,[('groups_id','in',group_id),('id','!=',1)])
        users = users_obj.browse(cr, uid, user_ids)
        mail_to = ''
        for user in users:
            if user.email and user.email != '':
                mail_to += user.email+', '
        prod = self.browse(cr, uid, prod_id)
        if mail_to != '':
            create_uid = users_obj.browse(cr, uid, uid)
            cd_config_obj = self.pool.get('cd.config.settings')
            cd_config_id = cd_config_obj.search(cr, uid, [])
            if cd_config_id:
                cd_crm = cd_config_obj.browse(cr, uid, cd_config_id[-1]).cd_crm
            else:
                raise osv.except_osv(decode('Błąd'), decode('Przed dodaniem produktu należy podać adres CRM.'))
            url = ("http://%s/?db=%s#id=%s&view_type=form&model=product.product")%(cd_crm, cr.dbname, prod_id)
            vals = (prod.name, create_uid.name, url)
            subject = 'Dodano nowy produkt'
            body = decode("Dodano nowy produkt o nazwie: %s<br/>Produkt dodał użytkownik: %s<br/><a href='%s'>Link do produktu</a>") % vals
            self.send_mail(cr, uid, body, subject, mail_to)
        
        return prod_id
    
    def write(self, cr, uid, ids, vals, context=None):
        """if 'state' in vals and vals['state'] != False:
            prod = self.browse(cr, uid, ids)[0]
            
            states = [('',''),
            ('draft', 'W przygotowaniu'),
            ('sellable','Normalny'),
            ('end','Zamknięto produkcję'),
            ('obsolete','Zdezaktualizowany')]
            old_state = ''
            new_state = ''
            for state in states:
                if vals['state'] == state[0]:
                    new_state = state[1]
                if prod.state == state[0]:
                    old_state = state[1]
            
            subject='Zmieniono status'
            body = '%s --> %s'%(old_state, new_state)
            self.message_post(cr, uid, ids, body=body, subject=subject, type='email', 
                        parent_id=False, attachments=None, context=context, content_subtype='html')"""
            
        prod_id = super(product_product, self).write(cr, uid, ids, vals, context=None)
        if 'product_manager' in vals and vals['product_manager'] != False:
            user = self.pool.get('res.users').browse(cr, uid, vals['product_manager'])
            self.message_subscribe(cr, uid, ids, [user.partner_id.id], context=context)
        
        """if 'priorytet' in vals and vals['priorytet'] != 0:
            users_obj = self.pool.get('res.users')
            group_id = self.pool.get('res.groups').search(cr,uid,[('name','=','KAM')])
            user_ids = users_obj.search(cr,uid,[('groups_id','in',group_id),('id','!=',1)])
            users = users_obj.browse(cr, uid, user_ids)
            mail_to = ''
            for user in users:
                if user.email and user.email != '':
                    mail_to += user.email+', '
            prod = self.browse(cr, uid, ids[0])
            if mail_to != '':
                create_uid = users_obj.browse(cr, uid, uid)
                cd_config_obj = self.pool.get('cd.config.settings')
                cd_config_id = cd_config_obj.search(cr, uid, [])
                if cd_config_id:
                    cd_crm = cd_config_obj.browse(cr, uid, cd_config_id[-1]).cd_crm
                else:
                    raise osv.except_osv(decode('Błąd'), decode('Przed dodaniem produktu należy podać adres CRM.'))
                
                url = ("http://%s/?db=%s#id=%s&view_type=form&model=product.product")%(cd_crm, cr.dbname, ids[0])
                vals = (prod.name, create_uid.name, url)
                subject = 'Zmieniono priorytet produktu'
                body = decode("Zmieniono priorytet produktu o nazwie: %s<br/>Zmiany dokonał użytkownik: %s<br/><a href='%s'>Link do produktu</a>") % vals
                self.send_mail(cr, uid, body, subject, mail_to)
        """
        return prod_id

    def send_mail(self, cr, uid, body, subject, mail_to, context=None):
        #pdb.set_trace()
        users_obj = self.pool.get('res.users')
        uid_id = users_obj.browse(cr, uid, uid)
        if uid_id.email:
            email_from = uid_id.partner_id.name+"<"+uid_id.partner_id.email+">"
                
            vals = {'email_from': email_from,
                    'email_to': mail_to,
                    'state': 'outgoing',
                    'subject': subject,
                    'body_html': body,
                    'auto_delete': True}
                    
            self.pool.get('mail.mail').create(cr, uid, vals, context=context)
        else:
            uid_id = users_obj.browse(cr, uid, 1)
            if uid_id.email:
                email_from = uid_id.partner_id.name+"<"+uid_id.partner_id.email+">"
                    
                vals = {'email_from': email_from,
                        'email_to': mail_to,
                        'state': 'outgoing',
                        'subject': subject,
                        'body_html': body,
                        'auto_delete': True}
                        
                self.pool.get('mail.mail').create(cr, uid, vals, context=context)
        
    def send_data_reminder(self, cr, uid):
        users_obj = self.pool.get('res.users')
        
        
        cd_config_obj = self.pool.get('cd.config.settings')
        cd_config_id = cd_config_obj.search(cr, uid, [])
        
        if cd_config_id:
            cd_crm = cd_config_obj.browse(cr, uid, cd_config_id[-1]).cd_crm
        else:
            raise osv.except_osv(decode('Błąd'), decode('Przed dodaniem produktu należy podać adres CRM.'))
        url = ("http://%s/?db=%s")%(cd_crm, cr.dbname)
        
        group_id = self.pool.get('res.groups').search(cr,uid,[('name','in',['Logistics','Finances','Cederroth Data manager', 'Sales Manager', 'KAM'])])
        if group_id:
            user_ids = users_obj.search(cr,uid,[('groups_id','in',group_id),('id','!=',1)])
            users = users_obj.browse(cr, uid, user_ids)
            mail_to = ''
            
            for user in users:
                if user.email and user.email != '':
                    mail_to += user.email+', '
            
            all_product_ids = self.search(cr, uid, [('product_count', '!=', '100%'),('state','=', 'draft')])
            if mail_to != '':
                create_uid = users_obj.browse(cr, uid, uid)
                
                vals = (len(all_product_ids), url)
                subject = 'OpenERP - Potrzebne dane produktowe'
                body = decode("W systemie OpenERP jest %s produktów, które wymagaja uzupelnienia danych.<br/><a href='%s'>Link do systemu</a>") % vals
                self.send_mail(cr, uid, body, subject, mail_to)
        
        #wyslac wiadomosci do marketingu
        mail_to = ''
        group_id = self.pool.get('res.groups').search(cr,uid,[('name','=','Marketing')])
        if group_id:
            user_ids = users_obj.search(cr,uid,[('groups_id','in',group_id),('id','!=',1)])
            
            for user_id in user_ids:
                product_ids = self.search(cr, uid, [('product_manager','=', user_id),('product_count', '!=', '100%'),('state','=', 'draft')])
                if product_ids:
                    user = users_obj.browse(cr, uid, user_id)
                    vals = (len(product_ids), url)
                    body = decode("W systemie OpenERP jest %s produktów wymagajacych uzupelnienia przez Ciebie danych.<br/> <a href='%s'>Link do systemu</a>") % vals
                    self.send_mail(cr, uid, body, subject, user.email)
        return True
        
    def copy_brand(self, cr, uid, context=None):
        product_ids = self.search(cr, uid, [])
        for product in self.browse(cr, uid, product_ids):
            vals = {}
            if product.categ_id.parent_id:
                if product.categ_id.parent_id.parent_id:
                    vals['product_mark'] = product.categ_id.parent_id.parent_id.id
                else:
                    vals['product_mark'] = product.categ_id.parent_id.id
            else:
                vals['product_mark'] = product.categ_id.id
            self.write(cr, uid, [product.id], vals, context=None)

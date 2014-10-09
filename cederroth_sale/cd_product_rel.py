# -*- coding: utf-8 -*-
"""
@author: mbereda
"""

from openerp.osv import fields, osv
from openerp.osv.orm import Model
from openerp.addons.mail.mail_message import decode
import pdb
import datetime

class cd_product_rel(Model):
    _name = "cd.product.rel"
    """   
    def _get_nsh_price(self, cr, uid, ids, name, arg, context=None):
        #pdb.set_trace()        
        val={}
        listing_obj = self.pool.get('cd.listing')
        
        for product_rel in self.browse(cr, uid, ids, context=context):
            discount_front = product_rel.promotions_id.client_id.discount_front
            client_id = product_rel.promotions_id.client_id.id
            product_id = product_rel.product_id.id
            listing_ids = listing_obj.search(cr, uid, [('client_id','=',client_id),('product_id','=', product_id)])
            price = 0.0
            if listing_ids:
                price = listing_obj.browse(cr, uid, listing_ids[0]).price_sale
            
            if price and price != 0 and discount_front and discount_front != 0:
                val[product_rel.id] = round(price - (price*(discount_front/100)), 2)
            else:
                val[product_rel.id] = 0
        
        return val
    
    def _get_list_price(self, cr, uid, ids, name, arg, context=None):
        val = {}
        listing_obj = self.pool.get('cd.listing')
        
        for product_rel in self.browse(cr, uid, ids, context=context):
            client_id = product_rel.promotions_id.client_id.id
            product_id = product_rel.product_id.id
            listing_ids = listing_obj.search(cr, uid, [('client_id','=',client_id),('product_id','=', product_id)])
            if listing_ids:
                val[product_rel.id] = listing_obj.browse(cr, uid, listing_ids[0]).price_sale
            else:
                val[product_rel.id] = 0.0
        return val
    
    def _get_value_nsh(self, cr, uid, ids, name, arg, context=None):
        val = {}
        for id in ids:
            product = self.browse(cr, uid, id)
            val[id] = product.prom_price * product.amount_product        
        return val
    """
    def _get_product_rel_vals(self, cr, uid, ids, name, arg, context=None):
        val = {}
        listing_obj = self.pool.get('cd.listing')
        for product_rel in self.browse(cr, uid, ids, context=context):
            list_price = 0.0
            nsh_price = 0.0
            value_nsh = product_rel.prom_price * product_rel.amount_product
            if 'listing_price' in name or 'nsh_price' in name:
                client_id = product_rel.promotions_id.client_id.id
                product_id = product_rel.product_id.id
                            
                listing_ids = listing_obj.search(cr, uid, [('client_id','=',client_id),('product_id','=', product_id)])
                
                if listing_ids:
                    list_price = listing_obj.browse(cr, uid, listing_ids[0]).price_sale
                    discount_front = product_rel.promotions_id.client_id.discount_front
                    if 'nsh_price' in name:
                        discount_dict = {}
                        for discount in product_rel.promotions_id.client_id.discount_partner_ids:
                            discount_dict[discount.product_category.id] = [discount.discount_front]
                        if product_rel.product_id.product_mark.id in discount_dict:
                            discount = discount_dict[product_rel.product_id.product_mark.id]
                            nsh_price = list_price-(list_price*(discount[0]/100))
                        else:
                            nsh_price = list_price-(list_price*(discount_front/100))
            val[product_rel.id] = {'list_price' : list_price,
                                   'nsh_price' : nsh_price,
                                   'value_nsh' : value_nsh}
        return val
        
    _columns = {
        'product_id': fields.many2one('product.product',"Produkt", required=True, ondelete="cascade", readonly=True),
        'promotions_id': fields.many2one('cd.promotions',"Akcje promocyjne", required=True, ondelete="cascade"),
        'product_name': fields.related('product_id', 'name', type="char", string="Name", readonly=True),
        'default_code': fields.related('product_id', 'default_code', type="char", string="MOVEX", readonly=True),
        'sugest_price_ret': fields.related('product_id', 'sugest_price_ret', type="float", string="Sug. cena det.", readonly=True, help="Sugerowana cena detaliczna"),
        'sugest_price_prom': fields.related('product_id', 'sugest_price_prom', type="float", string="Sug. cena prom.", readonly=True, help="Sugerowana cena promocyjna"),
        'list_price': fields.function(_get_product_rel_vals, type="float", string="Cena kat.", readonly=True, help="Cena katalogowa", store=True, multi='product_vals'), 
        'price_cogs': fields.related('product_id', 'price_cogs', type="float", string="Cena COGS", readonly=True, store=True),
        'state_prom': fields.related('promotions_id', 'state', type="char", string="Status promocji", readonly=True),
        'sequence_prom': fields.related('promotions_id', 'sequence', type="char", string="Status promocji", readonly=True),
        'discount_prom': fields.float("Rabat prom.(%)", help="Rabat promocyjny"),
        'amount_product': fields.integer("Plan. ilość", help="Planowana ilość"),
        'amount_sold': fields.integer("Sprzed. ilość", help="Sprzedana ilość"),
        'prom_price': fields.float('Cena NSH', help="Cena NSH"),
        'retail_price': fields.float('Cena det.', help="Cena detaliczna"),
        'nsh_price': fields.function(_get_product_rel_vals, type="float", string='Cena front', readonly=True, store=True, multi='product_vals'),
        'value_nsh': fields.function(_get_product_rel_vals, type="float", string='Wartość NSH', readonly=True, store=False, multi='product_vals'),
        'stage_id' : fields.related('promotions_id', 'stage_id', type="many2one", relation="cd.promotions.stage", string="Status", readonly=True),
        'client_id' : fields.related('promotions_id', 'client_id', type="many2one", relation="res.partner", string="Klient", readonly=True, store=True),
        'discount_from' : fields.related('promotions_id', 'discount_from', type="date", string="Rabat od", readonly=True, store=True),
        'discount_to' : fields.related('promotions_id', 'discount_to', type="date", string="Rabat do", readonly=True, store=True),
        'promotion_creat_uid': fields.related('promotions_id', 'create_uid', type="many2one", relation="res.users", string="Utworzył", readonly=True),
        'client_movex': fields.related('client_id', 'ref', type="char", string="MOVEX", readonly=True),
        'movex_date_confirm': fields.date('Data wprowadzenia'),
        'product_movex': fields.related('product_id', 'default_code', type="char", string="MOVEX", readonly=True),
        'bok_user_id' : fields.related('client_id', 'bok_user_id', type="many2one", relation="res.users", string="Pracownik BOK", readonly=True, store=True),
        'sequence': fields.related('stage_id', 'sequence', type="integer"),
        'state': fields.selection([('new',"new"), ('done',"done")], 'Status MOVEX'),
    }
    
    _defaults = {
        'state': 'new',
    }
    
    _order = "discount_from desc, id"
    
    def create(self, cr, uid, data, context=None):
        promotions_obj = self.pool.get('cd.promotions')
        product_obj = self.pool.get('product.product')
        
        promotions = promotions_obj.browse(cr, uid, data['promotions_id'])
        product = product_obj.browse(cr, uid, data['product_id'])
        
        for brand in promotions.client_id.discount_partner_ids:
            if brand.product_category.id == product.product_mark.id:
                data['discount_prom'] = brand.discount_promo
                continue
        if 'discount_prom' not in data:
            data['discount_prom'] = promotions.client_id.discount_promo
            
        poduct_rel_id = super(cd_product_rel, self).create(cr, uid, data, context=context)
        self.on_change_discount_prom(cr, uid, [poduct_rel_id], data['discount_prom'])
        return poduct_rel_id
    def write(self, cr, uid, ids, vals, context=None):
        for id in ids:
            data = self._calculate_price(cr, uid, id)
            vals2 = dict(vals.items() + data.items())
            if 'prom_price' in vals:
                discount_prom = self.on_change_prom_price(cr, uid, ids, vals['prom_price'], context)['value']['discount_prom']
                vals2['prom_price'] = vals['prom_price']
                #vals2['discount_prom'] = discount_prom
            super(cd_product_rel, self).write(cr, uid, id, vals2, context=context)
        return True
    
    def confirm_movex(self,cr,uid,ids,context=None):
        movex_date_confirm = datetime.datetime.now().strftime("%Y-%m-%d 00:01:00")
        self.write(cr, uid, ids, {'state': 'done', 'movex_date_confirm': movex_date_confirm})
    
    def on_change_discount_prom(self, cr, uid, ids, discount_prom, context=None):
        product = self.browse(cr, uid, ids[0])
        nsh_price = product.nsh_price
        vals ={}
        prom_price = nsh_price-nsh_price*float(discount_prom)/100
        vals['prom_price'] = prom_price
        #self.write(cr, uid, product.id, vals, context=None)
        
        sugest_price_prom = 0.00
        if product.sugest_price_prom:
            sugest_price_prom = product.sugest_price_prom
        if prom_price < sugest_price_prom:
            return {'value':vals, 'warning':{'title':'Ostrzeżenie','message':'Cena promocyjna jest niższa od sugerowanej ceny promocyjnej.'}}
        else:
            return {'value':vals}
    
    def on_change_prom_price(self, cr, uid, ids, prom_price, context=None):
        product = self.browse(cr, uid, ids[0])
        nsh_price = product.nsh_price
        vals ={}
        vals['discount_prom'] = int((nsh_price-prom_price)/nsh_price*100)
        #self.write(cr, uid, product.id, vals, context=None)
        
        return {'value': vals}
    
    def _calculate_price(self, cr, uid, id):
        
        vals = {}
        list_price = 0
        product_rel = self.browse(cr, uid, id)
        listing_obj = self.pool.get('cd.listing')
        
        
        if product_rel.list_price == 0:
            listing_ids = listing_obj.search(cr, uid, [('client_id','=',product_rel.promotions_id.client_id.id),('product_id','=', product_rel.product_id.id), ('status_l','=','0')])
            
            if listing_ids:
                list_price = listing_obj.browse(cr, uid, listing_ids[0]).price_sale
                vals['list_price'] = list_price
        else:
            list_price = product_rel.list_price
        
        discount_front = product_rel.promotions_id.client_id.discount_front
        discount_dict = {}
        for discount in product_rel.promotions_id.client_id.discount_partner_ids:
            discount_dict[discount.product_category.id] = [discount.discount_front]
        if product_rel.product_id.product_mark.id in discount_dict:
            discount = discount_dict[product_rel.product_id.product_mark.id]
            nsh_price = list_price-(list_price*(discount[0]/100))
        else:
            nsh_price = list_price-(list_price*(discount_front/100))
        vals['nsh_price'] = nsh_price
        
        prom_price = nsh_price - (nsh_price*(product_rel.discount_prom/100))
        vals['prom_price'] = prom_price
        
        value_nsh = prom_price * product_rel.amount_product
        vals['value_nsh'] = value_nsh
        
        return vals

    
    # -*- coding: utf-8 -*-
"""
@author: mbereda
"""

from openerp.osv import fields, osv
from openerp.osv.orm import Model
from openerp.addons.mail.mail_message import decode
from datetime import timedelta, datetime
import datetime
import calendar
import pdb

AVAILABLE_MONTHS = [('01',"Styczeń"), ('02',"Luty"), ('03',"Marzec"), ('04',"Kwiecień"), ('05',"Maj"), ('06',"Czerwiec"), 
          ('07',"Lipiec"), ('08',"Sierpień"), ('09',"Wrzesień"), ('10',"Październik"), ('11',"Listopad"), ('12',"Grudzień")]

class cd_plan_product(osv.Model):
    _name = "cd.plan.product"
    _rec_name = "plan_name"
    _description = "Plan produkt"
    """
    def _get_nsh_listing_price(self, cr, uid, ids, name, arg, context=None):
        val={}
        listing_obj = self.pool.get("cd.listing")
        for plan_product in self.browse(cr, uid, ids):
            listing_ids = listing_obj.search(cr, uid, [('client_id','=',plan_product.plan_client_id.client_id.id),('product_id','=',plan_product.product_id.id)])
            listing_price = listing_obj.browse(cr, uid, listing_ids)[0].price_sale
            discount_front = plan_product.plan_client_id.client_id.discount_front
            
            val[plan_product.id] = {'listing_price': listing_price, 'nsh_price': listing_price-(listing_price*(discount_front/100))}
        return val
    """
    def _get_product_list(self, cr, uid, ids, name, arg, context=None):
        val={}
        listing_obj = self.pool.get("cd.listing")
        for plan_product in self.browse(cr, uid, ids):
            listing_ids = listing_obj.search(cr, uid, [('client_id','=',plan_product.plan_client_id.client_id.id),('status_l','=','0')])
            listings = listing_obj.read(cr, uid, listing_ids,['product_id'])
            
            product_list = []
            for listing in listings:
                product_list.append(listing['product_id'][0])
            val[plan_product.id] = [[6, False, product_list]]
        return val
    """
    def _get_sum_plan_count_value(self, cr, uid, ids, name, arg, context=None):
        val={}
        for plan_product in self.browse(cr, uid, ids):
            val[plan_product.id] = {'sum_plan_count': 0, 
                                    'sum_plan_value': 0}
        return val
        
    def _get_sum_exec_count(self, cr, uid, ids, name, arg, context=None):
        val={}
        for id in ids:
            plan_product = self.browse(cr, uid, id)
            val[id] = plan_product.promo_exec_count + plan_product.execute_count
        return val
    
    def _get_sum_exec_value(self, cr, uid, ids, name, arg, context=None):
        val={}
        for id in ids:
            plan_product = self.browse(cr, uid, id)
            val[id] = plan_product.promo_exec_value + plan_product.execute_value
        return val

    def _get_promo_count_value(self, cr, uid, ids, name, arg, context=None):
        val={}
        product_rel_obj = self.pool.get('cd.product.rel')
        for plan_product in self.browse(cr, uid, ids):
            product = plan_product.product_id
            start_date = datetime.date(plan_product.year,int(plan_product.month),1)
            stop_date = self.add_months(datetime.date(plan_product.year,int(plan_product.month),1),1)
            product_rel_ids = product_rel_obj.search(cr, uid, [('product_id','=',product.id),('promotions_id.client_id.id','=',plan_product.plan_client_id.client_id.id),('promotions_id.discount_from','>=',start_date),('promotions_id.discount_from','<',stop_date)])
            
            val[plan_product.id] = {'promo_exec_count': 0, 'promo_exec_value': 0.0, 'promo_plan_count': 0.0, 'promo_plan_value': 0.0}
            if product_rel_ids:
                product_rel = product_rel_obj.browse(cr, uid, product_rel_ids)[0]
                val[plan_product.id] = {'promo_exec_count': product_rel.amount_sold, 'promo_exec_value': product_rel.prom_price * product_rel.amount_sold, 
                                        'promo_plan_count': product_rel.amount_product, 'promo_plan_value': product_rel.prom_price * product_rel.amount_product}
        return val
    
    def _get_plan_exec_value(self, cr, uid, ids, name, arg, context=None):
        val={}
        for plan in self.browse(cr, uid, ids):
            val[plan.id] = {'plan_value': plan.nsh_price*plan.plan_count, 'execute_value': plan.nsh_price*plan.execute_count}
        return val
    
    def _get_new_product(self, cr, uid, ids, name, arg, context=None):
        val={}
        listing_obj = self.pool.get('cd.listing')
        date_new = self.add_months(datetime.date.today(),-3)
        for plan in self.browse(cr, uid, ids):
            listing_ids = listing_obj.search(cr, uid, [('product_id','=',plan.product_id.id),('client_id','=',plan.plan_client_id.client_id.id),('change_date','>',date_new)])
            if listing_ids:
                val[plan.id] = 'Nowość'
            else:
                val[plan.id] = ''
        return val
    """
    
    def _get_product_new(self, cr, uid, ids, name, arg, context=None):
        val={}
        listing_obj = self.pool.get("cd.listing")
        date_new = self.add_months(datetime.date.today(),-3)
        for plan_product in self.browse(cr, uid, ids):
            new_product = ''
            listing_ids = listing_obj.search(cr, uid, [('product_id','=',plan_product.product_id.id),('client_id','=',plan_product.plan_client_id.client_id.id),('change_date','>',date_new)])
            if listing_ids:
                new_product = 'Nowość'
            else:
                new_product = ''
            val[plan_product.id] = new_product
        return val
    
    def _get_plan_product_vals(self, cr, uid, ids, name, arg, context=None):
        val = {}
        listing_obj = self.pool.get("cd.listing")
        product_rel_obj = self.pool.get('cd.product.rel')
        for plan_product in self.browse(cr, uid, ids):
            plan_value = 0.0
            execute_value = 0.0
            sum_plan_count = 0.0
            sum_plan_value = 0.0
            nsh_price = 0.0
            listing_price = 0.0
            promo_exec_count = 0
            promo_plan_count = 0
            promo_exec_value = 0.0
            promo_plan_value = 0.0
            new_product = ''
            contribp = 0.0

            #słownik z dodatkowymi rabatami
            discount_dict = {}
            for discount in plan_product.plan_client_id.client_id.discount_partner_ids:
                discount_dict[discount.product_category.id] = [discount.discount_front, discount.discount_back, discount.discount_promo]
            
            if 'nsh_price' in name or 'listing_price' in name or 'plan_value' in name or 'sum_plan_value' in name or 'gpp' in name or 'execute_value' in name:
                listing_ids = listing_obj.search(cr, uid, [('client_id','=',plan_product.plan_client_id.client_id.id),('product_id','=',plan_product.product_id.id),('status_l','=','0')])
                if listing_ids:
                    listing_price = listing_obj.browse(cr, uid, listing_ids)[0].price_sale
            
            if 'nsh_price' in name or 'plan_value' in name or 'sum_plan_value' in name or 'gpp' in name or 'execute_value' in name:
                if plan_product.product_id.product_mark.id in discount_dict:
                    discount = discount_dict[ plan_product.product_id.product_mark.id]
                    nsh_price = listing_price-(listing_price*(discount[0]/100))
                else:
                    discount_front = plan_product.plan_client_id.client_id.discount_front
                    nsh_price = listing_price-(listing_price*(discount_front/100))
                
            if 'promo_exec_count' in name or 'promo_plan_count' in name or 'promo_exec_value' in name or 'promo_plan_value' in name or 'sum_plan_value' in name or 'sum_plan_count' in name:
                product_rel_ids = product_rel_obj.search(cr, uid, [('product_id','=',plan_product.product_id.id),('promotions_id.client_id.id','=',plan_product.plan_client_id.client_id.id),('promotions_id.start_year','=',str(plan_product.year)),('promotions_id.start_month','=',plan_product.month), ('promotions_id.sequence','not in',[40,90])])
                
                if product_rel_ids:
                    for product_rel in product_rel_obj.browse(cr, uid, product_rel_ids):
                        promo_exec_count += (product_rel.amount_sold if 'promo_exec_count' in name else 0.0)
                        promo_plan_count += (product_rel.amount_product if 'promo_plan_count' in name or 'sum_plan_count' in name else 0.0)
                        promo_exec_value += (product_rel.prom_price * product_rel.amount_sold if 'promo_exec_value' in name else 0.0)
                        promo_plan_value += (product_rel.prom_price * product_rel.amount_product if 'promo_plan_value' in name or 'sum_plan_value' in name else 0.0)
                
            if 'plan_value' in name or 'sum_plan_value' in name:
                plan_value = nsh_price * plan_product.plan_count
            if 'execute_value' in name:
                execute_value = nsh_price * plan_product.execute_count
            if 'sum_plan_count' in name:
                sum_plan_count = promo_plan_count + plan_product.plan_count
            if 'sum_plan_value' in name:
                sum_plan_value = promo_plan_value + plan_value
            if 'gpp' in name and nsh_price != 0:
                client = plan_product.plan_client_id.client_id
                nsh = nsh_price
                if plan_product.product_id.product_mark.id in discount_dict:
                    discount = discount_dict[ plan_product.product_id.product_mark.id]
                    nsv = nsh - nsh*(discount[2]/100)
                    gp = nsv - plan_product.product_id.price_cogs
                    contrib = gp - nsh*(client.discount_back_coop/100)
                else:
                    nsv = nsh - nsh*(client.discount_back_trade_promo/100)
                    gp = nsv - plan_product.product_id.price_cogs
                    contrib = gp - nsh*(client.discount_back_coop/100)
                if nsv != 0.0:
                    contribp = 100 - ((nsv-contrib)/nsv)*100
                

            val[plan_product.id] = {'plan_value': plan_value, 
                            'execute_value': execute_value,
                            'sum_plan_count': sum_plan_count, 
                            'sum_plan_value': sum_plan_value,
                            'listing_price': listing_price,
                            'nsh_price' : nsh_price,
                            'promo_exec_count' : promo_exec_count,
                            'promo_plan_count' : promo_plan_count,
                            'promo_exec_value' : promo_exec_value,
                            'promo_plan_value' : promo_plan_value,
                            'new_product' : new_product,
                            'gpp': contribp,
                            }
        return val
    
    _columns = {
        'plan_name': fields.char("Nazwa Estymacji", size=255, required=False),
        'year': fields.integer("Rok", required=True, group_operator='min'),
        'month': fields.selection(AVAILABLE_MONTHS, 'Miesiąc', required=True),
        'start_date': fields.date('Data rozpoczęcia'),
        'stop_date': fields.date('Data zakończenia'),
        'plan_client_id': fields.many2one('cd.plan.client', 'Plan Klient', required=True, ondelete='cascade'),
        'product_id': fields.many2one('product.product', 'Produkt', required=True),
        'default_code' : fields.related('product_id', 'default_code', type="char", string="MOVEX", store=False, readonly=True),
        'plan_value': fields.function(_get_plan_product_vals, type='float', string='Standard estymacja wartość', store=False, help="Planowana wartość bez akcji promocyjnej", multi='pp_vals'),
        'execute_value': fields.function(_get_plan_product_vals, type='float', string='Standard wykon wartość', store=False, help="Wykonana wartość bez akcji promocyjnej", multi='execute_value'),
        'sum_plan_count': fields.function(_get_plan_product_vals, type='integer', string='Razem estymacja ilość', store=False, help="Suma planowanej ilości razem z akcjami promocyjnymi", multi='pp_vals'),
        'sum_plan_value': fields.function(_get_plan_product_vals, type='float', string='Razem estymacja wartość', store=False, help="Suma planowanej wartości razem z akcjami promocyjnymi", multi='pp_vals'),
        #'sum_exec_count': fields.function(_get_sum_exec_count, type='integer', string='Razem wykon ilość', store=False, help="Suma wykonanej ilości razem z akcjami promocyjnymi"),
        #'sum_exec_value': fields.function(_get_sum_exec_value, type='float', string='Razem wykon wartość', store=False, help="Suma wykonanej wartości razem z akcjami promocyjnymi"),
        'sum_exec_count': fields.integer('Total zrealizowanej ilość', help="Suma zrealizowanej ilości razem z akcjami promocyjnymi"),
        'sum_exec_value': fields.float(string='Total zrealizowanej wartość', help="Suma zrealizowanej wartości razem z akcjami promocyjnymi"),
        'listing_price': fields.function(_get_plan_product_vals, type="float", string='Cena listing', readonly=True, store=False, multi='listing_price'),
        'nsh_price': fields.function(_get_plan_product_vals, type="float", string='Cena NSH', readonly=True, store=False, multi='pp_vals'),
        'execute_count': fields.integer('Standard zrealizowana ilość', help="Zrealizowana ilość bez akcji promocyjnej", readonly=True),
        'plan_count': fields.integer('Standard estymacja ilość', help="Planowana ilość bez akcji promocyjnej"),
        'promo_plan_count': fields.function(_get_plan_product_vals, type='integer', string='Promo estymacja ilość', store=False, help="Planowana ilość produktu z akcji promocyjnej", multi='pp_vals'),
        'promo_exec_count': fields.function(_get_plan_product_vals, type='integer', string='Promo zrealizowana ilość', store=False, help="Zrealizowana ilość produktu z akcji promocyjnej", multi='promo_exec_count'),
        'promo_plan_value': fields.function(_get_plan_product_vals, type='float', string='Promo estymacja wartość', store=False, help="Planowana wartość produktu z akcji promocyjnej", multi='pp_vals'),
        'promo_exec_value': fields.function(_get_plan_product_vals, type='float', string='Promo zrealizowana wartość', store=False, help="Zrealizowana wartość produktu z akcji promocyjnej", multi='promo_exec_value'),
        'gpp': fields.function(_get_plan_product_vals, type='float', string='Contrib. %', store=True, multi='pp_vals'),
        'product_list_ids' : fields.function(_get_product_list, relation='product.product', type='many2many', string='Produkty klienta', store=False,),
        #'client_id':fields.related('plan_client_id', 'client_id', type="many2one", relation="res.partner", string="Client", store=False),
        'new_product': fields.function(_get_product_new, type='char', string='', store=True, readonly=True),
        'propo_count': fields.integer('Śr. ilość miesiąc', readonly=True),
        'section_id' : fields.related('product_id', 'categ_id', type="many2one", relation="product.category", string="Kategoria", store=True, readonly=True),
        'price_cogs' : fields.related('product_id', 'price_cogs', type="float", string="Cena COGS", store=True, readonly=True),
    }
    
    _defaults = {
        'year': lambda s, cr, uid, c: datetime.date.today().year,
    }
    
    def create(self, cr, uid, data, context=None):
        start_date = datetime.date(data['year'], int(data['month']), 1)
        stop_date = (self.add_months(start_date,1)) - timedelta(days=1)
        data['start_date'] = start_date
        data['stop_date'] = stop_date
        
        plan_id = super(cd_plan_product, self).create(cr, uid, data, context=context)
        
        return plan_id
    
    def add_months(self, sourcedate,months):
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month / 12 
        month = month % 12 + 1
        day = min(sourcedate.day,calendar.monthrange(year,month)[1])
        return datetime.date(year,month,day)
    
    def onchange_product_list(self, cr, uid, ids, plan_client_id, context=None):
        plan_client = self.pool.get('cd.plan.client').browse(cr, uid, plan_client_id)
        listing_obj = self.pool.get("cd.listing")
        listing_ids = listing_obj.search(cr, uid, [('client_id','=',plan_client.client_id.id)])
        listings = listing_obj.read(cr, uid, listing_ids,['product_id'])
        vals = {}
        product_list = []
        for listing in listings:
            product_list.append(listing['product_id'][0])
        vals['product_list_ids'] = [[6, False, product_list]]
        if product_list:
            return {'value': vals}
        else:
            return {'value':vals, 'warning':{'title':'Ostrzeżenie','message':'Wybrany klient nie posiada Listingów.'}}
       
    def open_product_history(self, cr, uid, ids, context=None):
        plan = self.browse(cr, uid, ids)[0]
        context['product_id'] = plan.product_id.id
        context['client_id'] = plan.plan_client_id.client_id.id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Historia sprzedaży produktu', 
            'view_type': 'form',
            'view_mode': 'graph',
            'res_model': self.pool.get('cd.product.history.wizard')._name,
            'target': 'new',
            'context': context,
        }
        
    
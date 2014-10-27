# -*- coding: utf-8 -*-
"""
@author: mbereda
"""

from openerp.osv import fields, osv
from openerp.osv.orm import Model
from openerp.addons.mail.mail_message import decode
from datetime import timedelta
from openerp import SUPERUSER_ID
import calendar
import datetime
import psycopg2
import pdb

AVAILABLE_MONTHS = [('01',"Styczeń"), ('02',"Luty"), ('03',"Marzec"), ('04',"Kwiecień"), ('05',"Maj"), ('06',"Czerwiec"), 
          ('07',"Lipiec"), ('08',"Sierpień"), ('09',"Wrzesień"), ('10',"Październik"), ('11',"Listopad"), ('12',"Grudzień")]

AVAILABLE_STATE = [('01',"W trakcie"), ('02',"Wykonany"), ('03',"Zaakceptowany")]

class cd_plan_client(osv.Model):
    _name = "cd.plan.client"
    _inherit = 'mail.thread'
    _rec_name = "plan_name"
    _description = "Plan Klienta"
    
    def _get_product_list(self, cr, uid, ids, name, arg, context=None):
        val={}
        listing_obj = self.pool.get("cd.listing")
        for plan in self.browse(cr, uid, ids):
            plan_product_ids = []
            for product in plan.plan_product_ids:
                plan_product_ids.append(product.product_id.id)
            listing_ids = listing_obj.search(cr, uid, [('client_id','=',plan.client_id.id),('status_l','=','0'),('product_id.id','not in',plan_product_ids)])
            listings = listing_obj.read(cr, uid, listing_ids,['product_id'])
            
            product_list = []
            for listing in listings:
                product_list.append(listing['product_id'][0])
            val[plan.id] = [[6, False, product_list]]
        return val
    
    def _get_exec_value(self, cr, uid, ids, name, arg, context=None):
        val={}
        for plan in self.browse(cr, uid, ids):
            amount = 0.0
            for product in plan.plan_product_ids:
                amount += product.sum_exec_value
            
            val[plan.id] = amount
        return val
    
    def _get_blocked_uid(self, cr, uid, ids, name, arg, context=None):
        val={}
        #pdb.set_trace()
        groups_obj = self.pool.get('res.groups')
        for plan in self.browse(cr, uid, ids):
            if not groups_obj.search(cr, uid, [('users','=',uid),'|',('name','=','Department Director'),('name','=','Sales Director')]):
                val[plan.id] = True
            else:
                val[plan.id] = False
        return val
    
    def _get_plan_plan(self, cr, uid, ids, name, arg, context=None):
        val={}
        for plan in self.browse(cr, uid, ids):
            amount = 0.0
            for product in plan.plan_product_ids:
                amount += product.sum_plan_value
            val[plan.id] = amount
        return val
    
    def _get_forecast(self, cr, uid, ids, name, arg, context=None):
        val={}
        for plan in self.browse(cr, uid, ids):
            amount = 0.0
            for brand in plan.plan_client_brand_ids:
                amount += brand.forecast
            val[plan.id] = amount
        return val
    
    def _get_gp(self, cr, uid, ids, name, arg, context=None):
        
        val={}
        cd_rep_tradep_obj = self.pool.get('cd.report.trade.promo')
        cd_rep_ap_obj = self.pool.get('cd.report.ap')
        cd_rep_coop_obj = self.pool.get('cd.report.coop')
        cd_report_other_cogs_obj = self.pool.get('cd.report.other.cogs')
        cd_report_other_marketing_obj = self.pool.get('cd.report.other.mark.month')
        
        for plan in self.browse(cr, uid, ids):
            nsh_total = 0.0 # gross sale - rabaty front - rabaty promo
            gpp_total = 0.0 
            nsv_total = 0.0 # nsh_total - trade promo - listing
            nsh_promo = 0.0
            gross_sale = 0.0
            disc_front_total = 0.0
            disc_front_promo = 0.0
            trade_promo = 0.0
            other_cogs = 0.0
            other_listings = 0.0
            other_marketing = 0.0
            product_cogs = 0.0
            discount_pormo = 0.0
            cm_total = 0.0
            cmp_total = 0.0
            coop_value = 0.0
            gross_sale_promo = 0.0
            nsh_p_nsh_t = 0.0
            trade_promo_listing = 0.0
            gp_total = 0.0
        
            #pdb.set_trace()
            if 'nsh_total' in name or 'gpp_total' in name or 'nsv_total' in name or 'gross_sale' in name or 'disc_front_total' in name or 'product_cogs' in name or 'cmp_total' in name or 'cm_total' in name:
                if 'nsv_total' in name or 'disc_front_total' in name or 'nsh_total' in name or 'gp_total' in name:
                    discount_dict = {}
                    for discount in plan.client_id.discount_partner_ids:
                        discount_dict[discount.product_category.id] = [discount.discount_front, discount.discount_back]
                        
                for product in plan.plan_product_ids:
                    if 'nsv_total' in name or 'disc_front_total' in name or 'nsh_total' in name or 'gp_total' in name:
                        if product.product_id.product_mark.id in discount_dict:
                            discount = discount_dict[product.product_id.product_mark.id]
                            disc_front_total += product.listing_price*product.sum_plan_count * (discount[0]/100)
                            #disc_front_promo += product.listing_price*product.promo_plan_count * (discount[0]/100)
                        else:
                            disc_front_total += product.listing_price*product.sum_plan_count*(plan.client_id.discount_front/100)  
                            #disc_front_promo += product.listing_price*product.promo_plan_count * (plan.client_id.discount_front/100)
                    if 'gross_sale' in name or 'nsh_total' in name or 'nsh_promo' in name or 'nsv_total' or 'gp_total' in name:
                        gross_sale += product.listing_price * product.sum_plan_count
                        #gross_sale_promo += product.listing_price * product.promo_plan_count
                    if 'product_cogs' in name or 'cmp_total' in name or 'gp_total' in name:
                        product_cogs += product.product_id.price_cogs * product.sum_plan_count 
            
            if 'discount_pormo' in name or 'nsv_total' in name or 'cmp_total' in name or 'cm_total' in name or 'gp_total' in name:
                vals_ap = [
                           ('client_id','=',plan.client_id.id),
                           ('month','=',plan.month),
                           ('year','=',str(plan.year))
                           ]
                promotions_ids = cd_rep_ap_obj.search(cr, uid, vals_ap)
                for promotion in cd_rep_ap_obj.browse(cr, uid, promotions_ids):

                    discount_pormo += (promotion.discount_promo_contract + promotion.discount_promo_budget)
                        
            if 'nsh_total' in name or 'nsv_total' in name or 'nsh_p_nsh_t' in name or 'cmp_total' in name or 'cm_total' in name or 'gp_total' in name:
                nsh_total = gross_sale - disc_front_total - discount_pormo
            #if 'nsh_promo' in name or 'nsh_p_nsh_t' in name:
            #    nsh_promo = gross_sale_promo - disc_front_promo
            
            
            if 'nsh_p_nsh_t' in name:
                if nsh_total > 0:
                    nsh_p_nsh_t = (nsh_promo/nsh_total)*100         
            
            if 'trade_promo' in name or 'nsv_total' in name or 'trade_promo_listing' in name or 'cmp_total' in name or 'cm_total' in name:
                vals_trade = [
                              ('client_id','=',plan.client_id.id),
                              ('month','=',plan.month),
                              ('year','=',plan.year)
                              ]
                trade_ids = cd_rep_tradep_obj.search(cr, uid, vals_trade)
                for trade in cd_rep_tradep_obj.browse(cr, uid, trade_ids):
                    trade_promo += trade.value
                    
                trade_promo_listing += trade_promo

            if 'other_listings' in name or 'nsv_total' in name or 'trade_promo_listing' in name or 'cmp_total' in name or 'cm_total' in name or 'gp_total' in name:
                for other in plan.other_ids:
                    if other.target == '01':
                        other_listings += other.value
                trade_promo_listing += other_listings

            if 'nsv_total' in name or 'cmp_total' in name or 'cm_total' in name or 'gp_total' in name or 'trade_promo_listing' in name:
                nsv_total = nsh_total - trade_promo - other_listings
            
            
            if 'other_cogs' in name or 'gp_total' in name or 'cm_total' in name or 'gpp_total' in name:
                vals_other_cogs = [
                           ('client_id','=',plan.client_id.id),
                           ('month','=',plan.month),
                           ('year','=',plan.year)
                           ]
                other_cogs_ids = cd_report_other_cogs_obj.search(cr, uid, vals_other_cogs)
                
                for report_other_cogs in cd_report_other_cogs_obj.browse(cr, uid, other_cogs_ids):
                    other_cogs += report_other_cogs.value
            
                gp_total = nsv_total - product_cogs - other_cogs
                
                if nsv_total > 1:
                    gpp_total = gp_total/nsv_total*100

            if 'other_marketing' in name or 'cm_total' in name:
                vals_other_marketing = [
                           ('client_id','=',plan.client_id.id),
                           ('month','=',plan.month),
                           ('year','=',plan.year)
                           ]
                other_marketing_ids = cd_report_other_marketing_obj.search(cr, uid, vals_other_marketing)
                
                for item in cd_report_other_marketing_obj.browse(cr, uid, other_marketing_ids):
                    other_marketing += item.value

            if 'coop' in name or 'cm_total' in name or 'cmp_total' in name:
                vals_coop = [
                           ('client_id','=',plan.client_id.id),
                           ('month','=',plan.month),
                           ('year','=',str(plan.year))
                           ]
                coop_ids = cd_rep_coop_obj.search(cr, uid, vals_coop)
                for coop in cd_rep_coop_obj.browse(cr, uid, coop_ids):
                    coop_value += coop.value

            if 'cm_total' in name or 'cmp_total' in name:
                cm_total = gp_total - coop_value - other_marketing
            if 'cmp_total' in name:
                if nsv_total > 0:
                    cmp_total = cm_total/nsv_total*100
            
                
            val[plan.id] = {
                            'gpp_total': gpp_total,
                            'gp_total': gp_total,
                            'nsh_total': nsh_total,
                            'nsh_promo': nsh_promo,
                            'nsv_total': nsv_total,
                            
                            'gross_sale': gross_sale,
                            'disc_front_total': disc_front_total,
                            'trade_promo': trade_promo,
                            'other_cogs': other_cogs,
                            'other_listings': other_listings,
                            'other_marketing': other_marketing,
                            'product_cogs': product_cogs,
                            'discount_pormo': discount_pormo,
                            'cm_total': cm_total,
                            'cmp_total': cmp_total,
                            'coop': coop_value,
                            'nsh_p_nsh_t': nsh_p_nsh_t,
                            'trade_promo_listing': trade_promo_listing,
                            }
        return val
    
    def _get_plan(self, cr, uid, ids, name, arg, context=None):
        val={}
        for plan in self.browse(cr, uid, ids):
            plan_luz = 0.0
            plan_promo = 0.0
            exec_value = 0.0
            for brand in plan.plan_client_brand_ids:
                exec_value += brand.exec_value
                plan_luz += brand.plan_luz
                plan_promo += brand.plan_promo
            val[plan.id] = {
                            'exec_value': exec_value,
                            'plan_luz': plan_luz, 
                            'plan_promo': plan_promo,
                            }
        return val

    def _get_plan_mark(self, cr, uid, ids, name, arg, context=None):
        val={}
        mark_obj = self.pool.get('cd.plan.mark')
        for plan in self.browse(cr, uid, ids):
            mark_ids = mark_obj.search(cr, uid, [('year','=',plan.year),('month','=',plan.month)])
            val[plan.id] = mark_ids
        return val
    
    def _get_plan_value(self, cr, uid, ids, name, arg, context=None):
        val={}
        for plan in self.browse(cr, uid, ids):
            plan_value = 0.0
            get_value = 0.0
            plan_plan = 0.0
            
            val[plan.id] = {
                            'plan_value': plan_value,
                            'get_value': get_value, 
                            'plan_plan': plan_plan,
                            }
        return val
    
    def _get_budget_mark(self, cr, uid, ids, name, arg, context=None):
        val={}
        for plan in self.browse(cr, uid, ids):
            bud_cm = 0.0
            bud_nsh = 0.0
            for brand in plan.plan_client_brand_ids:
                bud_cm += brand.contrib
                bud_nsh += brand.forecast
                
            val[plan.id] = {
                            'bud_cm': bud_cm,
                            'plan_value': bud_nsh,
                            }
        return val
        
    _columns = {
        'plan_name': fields.char("Nazwa Planu", size=255, required=False),
        'state_id': fields.selection(AVAILABLE_STATE, 'Status'),
        'year': fields.integer("Rok", required=True, group_operator='min', readonly=False),
        'month': fields.selection(AVAILABLE_MONTHS, 'Miesiąc', required=True, readonly=False),
        'start_date': fields.date('Data rozpoczęcia'),
        'stop_date': fields.date('Data zakończenia'),
        'client_id': fields.many2one('res.partner', 'Klient', required=True, domain="[('is_company', '=', True)]"),
        #'bud_cm': fields.float('Budżet Contrib.'),
        'bud_cm': fields.function(_get_budget_mark, type='float', string='Budżet Contrib.', store=False, readonly=True, multi="budget_mark"),
        'plan_value': fields.function(_get_budget_mark, type='float', string='Budżet NSH', store=False, readonly=True, multi="budget_mark"),
        #'plan_value': fields.function(_get_forecast, type='float', string='Budżet NSH', store=False, required=True, readonly=False),
        #'plan_value': fields.float('Budżet NSH', required=True, readonly=False),
        'get_value': fields.function(_get_exec_value, type='float', string='Zrealizowana wartość', store=False, readonly=True),
        'plan_section_id': fields.many2one('cd.plan.section', 'Plan Departament', required=True, ondelete='cascade'), #domain="[('section_id.user_id.id','=',uid)]"
        'plan_product_ids': fields.one2many('cd.plan.product', 'plan_client_id', 'Plan Produkt'),
        'product_id': fields.many2one('product.product', "Wybierz produkt"),
        'product_list_ids' : fields.function(_get_product_list, relation='product.product', type='many2many', string='Produkty klienta', store=False),
        'blocked' : fields.related('plan_section_id', 'blocked', type='boolean', string='Blokowanie edycji', readonly=True),
        'blocked_uid' : fields.function(_get_blocked_uid, type='boolean', string='Zablokowane', store=False),
        'create_uid': fields.many2one('res.users', 'Twórca'),
        'plan_plan': fields.function(_get_plan_plan, type='float', string='Estymacja NSH', store=False, readonly=True),
        'gpp_total': fields.function(_get_gp, type='float', string='Estym GP %', store=False, readonly=True, multi='summation', group_operator="avg"),
        #'gpp_promo': fields.function(_get_gp, type='float', string='GP % promo', store=False, readonly=True,multi='summation', group_operator="avg"),
        'gp_total': fields.function(_get_gp, type='float', string='Estym GP', store=False, readonly=True, multi='summation'),
        #'gp_promo': fields.function(_get_gp, type='float', string='GP promo', store=False, readonly=True, multi='summation'),
        'nsh_total': fields.function(_get_gp, type='float', string='Estym NSH Total', store=False, readonly=True, multi='summation'),
        'nsh_promo': fields.function(_get_gp, type='float', string='NSH Promo', store=False, readonly=True, multi='summation'),
        #'cost_total': fields.function(_get_gp, type='float', string='Koszt total', store=False, readonly=True, multi='summation'),
        #'cost_promo': fields.function(_get_gp, type='float', string='Koszt promo', store=False, readonly=True, multi='summation'),
        #'percentage': fields.function(_get_gp, type='float', string='Estym promo / Estym total (%)', store=False, readonly=True, multi='summation', group_operator="avg"),
        'nsv_total': fields.function(_get_gp, type='float', string='Estym NSV total', store=False, readonly=True, multi='summation'),
        
        #nowe
        'gross_sale': fields.function(_get_gp, type='float', string='Estym Gross Sale', store=False, readonly=True, multi='summation'),
        'disc_front_total': fields.function(_get_gp, type='float', string='Estym Rabaty Front', store=False, readonly=True, multi='summation'),
        'trade_promo': fields.function(_get_gp, type='float', string='Estym Trade Promo', store=False, readonly=True, multi='summation'),
        'other_cogs': fields.function(_get_gp, type='float', string='Estym Other COGS', store=False, readonly=True, multi='summation'),
        'other_listings': fields.function(_get_gp, type='float', string='Estym Other (listing)', store=False, readonly=True, multi='summation'),
        'other_marketing': fields.function(_get_gp, type='float', string='Estym Other Marketing', store=False, readonly=True, multi='summation'),
        'product_cogs': fields.function(_get_gp, type='float', string='Estym COGS', store=False, readonly=True, multi='summation'),
        'discount_pormo': fields.function(_get_gp, type='float', string='Estym Rabaty Promo', store=False, readonly=True, multi='summation'),
        'cm_total': fields.function(_get_gp, type='float', string='Estym Contrib.', store=False, readonly=True, multi='summation'),
        'cmp_total': fields.function(_get_gp, type='float', string='Estym Contrib. %', store=False, readonly=True, multi='summation'),
        'coop': fields.function(_get_gp, type='float', string='Estym COOP', store=False, readonly=True, multi='summation'),
        'nsh_p_nsh_t': fields.function(_get_gp, type='float', string='Estym NSH Promo / NSH Total', store=False, readonly=True, multi='summation'),
        'trade_promo_listing': fields.function(_get_gp, type='float', string='Estym Trade Promo + Listing', store=False, readonly=True, multi='summation'),
        
        'other_cogs_ids': fields.one2many('cd.other.cogs', 'plan_client_id', 'Other COGS'),
        'other_marketing_ids': fields.one2many('cd.other.marketing', 'plan_client_id', 'Other Marketing'),
        'product_limited_ids': fields.one2many('cd.product.limited', 'plan_client_id', 'Próbki/produkty limitowane'),
        'other_ids': fields.one2many('cd.other', 'plan_client_id', 'Inne'),
        'sale_ids': fields.one2many('cd.sale', 'plan_client_id', 'Wyprzedaż'),
        'plan_client_brand_ids': fields.one2many('cd.plan.client.brand', 'plan_client_id', 'Plan Marka', readonly=True),
        
        'exec_value': fields.function(_get_plan, type='float', string='Zrealizowana wartość', store=False, readonly=True, multi='exec_value'),
        'plan_luz': fields.function(_get_plan, type='float', string='Estymacja standard', store=False, multi='plan_luz'),
        'plan_promo': fields.function(_get_plan, type='float', string='Estymacja promo', store=False, multi='plan_promo'),
        
        #'start_plan': fields.related('plan_section_id', 'start_plan', type='date', string='Rozpoczęcie planowania', readonly=True),
        'stop_plan': fields.related('plan_section_id', 'stop_plan', type='date', string='Zakończenie planowania', readonly=True),
        
        'plan_mark_ids': fields.related('plan_section_id', 'plan_mark_ids', type='one2many', relation='cd.plan.mark', store=False, readonly=True),
    }
    
    _defaults = {
        'year': lambda s, cr, uid, c: datetime.date.today().year,
    }
    
    def name_get(self, cr, uid, ids, context=None):
        """Overrides orm name_get method"""
        if not isinstance(ids, list) :
            ids = [ids]
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['client_id', 'month', 'year'], context)
        for record in reads:
            client = record['client_id'][1]
            month = record['month']
            year = record['year']
            res.append((record['id'], client + '   ' + str(year) + '-' + str(month)))
        return res
    
    def create(self, cr, uid, data, context=None):
        #pdb.set_trace()
        if self.search(cr, uid, [('year','=',data['year']),('month','=',data['month']),('client_id','=',data['client_id'])]):
            raise osv.except_osv(decode('Ostrzeżenie'), decode('Plan Klient na wybrany miesiąc już jest w systemie'))
        
        start_date = datetime.date(data['year'], int(data['month']), 1)
        stop_date = (self.add_months(start_date,1)) - timedelta(days=1)
        data['start_date'] = start_date
        data['stop_date'] = stop_date
        """
        cd_config_obj = self.pool.get('cd.config.settings')
        cd_config_id = cd_config_obj.search(cr, uid, [])
        cd_plan_prom = cd_config_obj.browse(cr, uid, cd_config_id[-1]).plan_plan_prom
        
        next_date = self.add_months(datetime.date.today(),cd_plan_prom)
        if next_date >= start_date:
            raise osv.except_osv(decode('Ostrzeżenie'), decode('Plan Klient nie może zostać utworzony w tym terminie'))
        """
                    
        plan_id = super(cd_plan_client, self).create(cr, uid, data, context=context)
        
        #Usunięcie dodawania Administratora do obserwarotów
        self.message_unsubscribe(cr, uid, [plan_id], [3], context=None)
        
        plan_client = self.browse(cr, uid, plan_id)
        
        if plan_client.client_id.user_id.partner_id:
            self.message_subscribe(cr, uid, [plan_id], [plan_client.client_id.user_id.partner_id.id], context=context)
        
        self.add_products2(cr, uid, plan_id)
        #print data['month'] + " " + plan_client.client_id.name
        #self.add_products2(cr, uid, plan_id)
        return plan_id
    
    def write(self, cr, uid, ids, data, context=None):
        for id in ids:
            plan_client = self.browse(cr, uid, id)
            
            if 'month' in data or 'year' in data:
                month = ''
                year = 0
                if 'month' in data:
                    month = data['month']
                else:
                    month = plan_client.month
                if 'year' in data:
                    year = data['year']
                else:
                    year = plan_client.year
                if self.search(cr, uid, [('year','=',year),('month','=',month),('section_id','=',plan_client.section_id.id)]):
                    raise osv.except_osv(decode('Ostrzeżenie'), decode('Plan Klient na wybrany miesiąc już jest w systemie'))

                start_date = datetime.date(year, int(month), 1)
                stop_date = (self.add_months(start_date,1)) - timedelta(days=1)
                data['start_date'] = start_date
                data['stop_date'] = stop_date
                """
                cd_config_obj = self.pool.get('cd.config.settings')
                cd_config_id = cd_config_obj.search(cr, uid, [])
                cd_plan_prom = cd_config_obj.browse(cr, uid, cd_config_id[-1]).plan_plan_prom
                
                next_date = self.add_months(datetime.date.today(),cd_plan_prom)
                if next_date >= start_date:
                    raise osv.except_osv(decode('Ostrzeżenie'), decode('Plan Klient nie może zostać utworzony w tym terminie'))
                """
        plan_id = super(cd_plan_client, self).write(cr, uid, ids, data, context=context)
        
        if 'state_id' in data:
            self.copy_data(cr, SUPERUSER_ID, ids[0], context=None)
        
        return plan_id
    
    def copy_data(self, cr, uid, plan_id, context=None):
        
        plan = self.browse(cr, uid, plan_id)
        rclient_obj = self.pool.get('cd.report.plan.client')
        rbrand_obj = self.pool.get('cd.report.plan.client.brand')
        
        if plan.state_id == '02':
            vals_client = {}
            data = self._get_gp(cr, uid, [plan_id], ['nsv_total','nsh_total','gpp_total','gp_total','gross_sale','disc_front_total','other_cogs','product_cogs','discount_pormo','cm_total','cmp_total','coop','nsh_p_nsh_t','trade_promo_listing','other_marketing'], '')
            vals_client = {
                    'plan_client_id': plan.id,
                    'year': plan.year,
                    'month' : plan.month,
                    'section_id' : plan.plan_section_id.section_id.id,
                    'client_id' : plan.client_id.id,
                    
                    'nsh_total': data[plan_id]['nsh_total'],
                    'gpp_total': data[plan_id]['gpp_total'],
                    'gp_total': data[plan_id]['gp_total'],
                    'gross_sale': data[plan_id]['gross_sale'],
                    'disc_front_total': data[plan_id]['disc_front_total'],
                    'other_cogs': data[plan_id]['other_cogs'],
                    'product_cogs': data[plan_id]['product_cogs'],
                    'discount_pormo': data[plan_id]['discount_pormo'],
                    'cm_total': data[plan_id]['cm_total'],
                    'cmp_total': data[plan_id]['cmp_total'],
                    'coop': data[plan_id]['coop'],
                    'nsh_p_nsh_t': data[plan_id]['nsh_p_nsh_t'],
                    'trade_promo_listing': data[plan_id]['trade_promo_listing'],
                    'other_marketing' : data[plan_id]['other_marketing'],
                    'nsv_total' : data[plan_id]['nsv_total'],
                    }
            rclient_obj.create(cr, uid, vals_client, context=None)

            for brand in plan.plan_client_brand_ids:
                vals_brand = {}
                vals_brand = {
                              'plan_client_id': plan.id,
                              'year': plan.year,
                              'month' : plan.month,
                              'section_id' : plan.plan_section_id.section_id.id,
                              'client_id' : plan.client_id.id,
                              
                              'product_category_id': brand.product_category_id.id,
                              'forecast': brand.forecast,
                              'plan_value': brand.plan_value,
                              'exec_value': brand.exec_value,
                              'plan_luz': brand.plan_luz,
                              'plan_promo': brand.plan_promo,
                              'estimation_news': brand.estimation_news,
                              }
                rbrand_obj.create(cr, uid, vals_brand, context=None)
        elif not plan.state_id or plan.state_id == '01':
            rclient_ids = rclient_obj.search(cr, uid, [('plan_client_id','=',plan.id)])
            rclient_obj.unlink(cr, uid, rclient_ids)
            
            rbrand_ids = rbrand_obj.search(cr, uid, [('plan_client_id','=',plan.id)])
            rbrand_obj.unlink(cr, uid, rbrand_ids)
         
        return True
    
    def add_months(self, sourcedate,months):
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month / 12 
        month = month % 12 + 1
        day = min(sourcedate.day,calendar.monthrange(year,month)[1])
        return datetime.date(year,month,day)
    
    def add_product(self, cr, uid, ids, context=None):
        w = self.browse(cr, uid, ids[0])
        data = {}
        data['product_id'] = w.product_id.id
        for product in w.plan_product_ids:
            if product.product_id.id == w.product_id.id:
                raise osv.except_osv(decode('Ostrzeżenie'), decode('Ten produkt został już dodany.'))
        data['plan_client_id'] = ids[0]
        data['plan_value'] = 0.0
        data['year'] = w.year
        data['month'] = w.month
        self.pool.get('cd.plan.product').create(cr, uid, data, context=None)
        vals = {}
        vals['product_id'] = False
        self.write(cr, uid, ids, vals, context=None)
        return {'value': vals}
    
    def _calculate_avg_sales(self, cr, uid, client_movex, product_movex, from_date):
        date_s = self.add_months((datetime.date.today()), -6)
        query = ""
        if date_s.year == from_date.year:
            year = date_s.year
            month = date_s.month
            query = ("SELECT id, item, qty, year, month FROM cd_sale_data where retailer = '%s' and item = '%s' and year=%s and month >= %s")%(client_movex, product_movex, year, month)
        else:
            year = from_date.year
            month = 1
            year2 = date_s.year
            month2 = date_s.month
            query = ("SELECT id, item, qty, year, month FROM cd_sale_data where retailer = '%s' and item = '%s' and ((year=%s and month >= %s) or (year = %s and month >= %s))")%(client_movex, product_movex, year, month, year2, month2)
            
        conn = psycopg2.connect(database=cr.dbname)
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        conn.close()
            
        qty_list = []
        avg_qty = 0
        number = 0
        for data in rows:
            qty_list.append(data[2])
            
        for qty in sorted(qty_list, key=int)[:5]:
            avg_qty = avg_qty + qty
            number = number + 1
        if number > 0:
            avg_qty = avg_qty / number
        
        return avg_qty
        
    def add_products2(self, cr, uid, plan_id, context=None):
        w = self.browse(cr, uid, plan_id)
        if w.client_id.ref == False:
            return True
        plan_product_obj = self.pool.get('cd.plan.product')
        listing_obj = self.pool.get('cd.listing')
        listing_ids = listing_obj.search(cr, uid, [('client_id','=', w.client_id.id),('status_l','=','0')])
        
        listing_products = self._get_listing_dict(cr, uid, listing_ids)
        
        if listing_products:
            
            today = datetime.date.today()
            date_s = self.add_months((datetime.date.today()), -6)
                
            for movex in listing_products:
                query = ""
                if date_s.year == today.year:
                    year = date_s.year
                    month = date_s.month
                    query = ("SELECT id, item, qty, year, month FROM cd_sale_data where retailer = '%s' and item = '%s' and year=%s and month >= %s")%(w.client_id.ref, movex, year, month)
                else:
                    year = today.year
                    month = 1
                    year2 = date_s.year
                    month2 = date_s.month
                    query = ("SELECT id, item, qty, year, month FROM cd_sale_data where retailer = '%s' and item = '%s' and ((year=%s and month >= %s) or (year = %s and month >= %s))")%(w.client_id.ref, movex, year, month, year2, month2)
                    
                conn = psycopg2.connect(database=cr.dbname)
                cur = conn.cursor()
                cur.execute(query)
                rows = cur.fetchall()
                conn.close()
                    
                qty_list = []
                avg_qty = 0
                number = 0
                for data in rows:
                    qty_list.append(data[2])
                    
                for qty in sorted(qty_list, key=int)[:5]:
                    avg_qty = avg_qty + qty
                    number = number + 1
                if number > 0:
                    avg_qty = avg_qty / number
                
                product_vals = {
                                'product_id': listing_products[movex],
                                'year': w.year,
                                'month': w.month,
                                'plan_client_id': w.id,
                                'plan_count': avg_qty,
                                'propo_count': avg_qty,
                                }
                plan_product_obj.create(cr, uid, product_vals)
                
        return True
    
    """
    def add_products(self, cr, uid, plan_id, context=None):
        w = self.browse(cr, uid, plan_id)
        
        if w.client_id.ref:
            listing_obj = self.pool.get('cd.listing')
            listing_ids = listing_obj.search(cr, uid, [('client_id','=', w.client_id.id),('status_l','=','0')])
            
            products_movex = []
            product_ids = []
            sale_data_ids = []
            for listing in listing_obj.browse(cr, uid, listing_ids):
                if listing.product_id.default_code:
                    products_movex.append(listing.product_id.default_code.encode('cp1250'))
                    product_ids.append(listing.product_id.id)
            
            if products_movex:
                sale_data_obj = self.pool.get('cd.sale.data')
                today = datetime.date.today()
                date_s = self.add_months((datetime.date.today()), -6)
                if date_s.year == today.year:
                    year = date_s.year
                    month = date_s.month
                    sale_data_ids = sale_data_obj.search(cr, uid, [('retailer','=', w.client_id.ref),('year','=',year),('month','>=',month),('item','in',products_movex)])
                else:
                    #pdb.set_trace()
                    year = today.year
                    month = 1
                    year2 = date_s.year
                    month2 = date_s.month
                    conn = psycopg2.connect(database=cr.dbname)
                    cur = conn.cursor()
                    query = ("SELECT id, item, qty, year, month FROM cd_sale_data where retailer = '%s' and item in %s and (year=%s and month >= %s) or (year = %s and month >= %s)")%(w.client_id.ref, tuple(products_movex), year, month, year2, month2)
                    cur.execute(query)
                    rows = cur.fetchall()
                    conn.close()
                    
                    for data in rows:
                        sale_data_ids.append(data[0])
                    
                sale_data_list = []
                
                product_obj = self.pool.get('product.product')
                for sale_data in sale_data_obj.browse(cr, uid, sale_data_ids):
                    product_id = product_obj.search(cr, uid, [('default_code','=', sale_data.item)])
                    if product_id:
                        product = product_obj.browse(cr, uid, product_id[0])
                        sale_data_value = {
                                           'product_id': product.id,
                                           'qty': sale_data.qty,
                                           'net_value': sale_data.net_value,
                                           'item': sale_data.item,
                                           'month': sale_data.month,
                                           }
                        sale_data_list.append(sale_data_value)
    
                plan_product_obj = self.pool.get('cd.plan.product')
                created_products = []
                for sale_data in sale_data_list:
                    if sale_data['product_id'] not in created_products:
                        plan_count = self.get_plan_count(cr, uid, sale_data_list, sale_data['product_id'], context=None)
                        product_vals = {}
                        product_vals = {
                                        'product_id': sale_data['product_id'],
                                        'year': w.year,
                                        'month': w.month,
                                        'plan_client_id': w.id,
                                        'plan_count': plan_count,
                                        }
                        plan_product_obj.create(cr, uid, product_vals)
                        created_products.append(sale_data['product_id'])
            
        return True
    """
    def get_plan_count(self, cr, uid, sale_data_list, product_id, context=None):
        product_data = []
        months = []
        max_count = 0
        for sale_data in sale_data_list:
            if sale_data['product_id'] == product_id:
                product_data.append(sale_data)
                if sale_data['month'] not in months:
                    months.append(sale_data['month'])
                if sale_data['qty'] > max_count:
                    max_count = sale_data['qty']
        if len(months) != 6:
            return 0
        sum = 0
        l = 0    
        result = 0
        for data in product_data:
            if data['qty'] != max_count:
                l += 1 
                sum += data['qty']
        if sum == 0 or l == 0:
            result = 0
        else:
            result = sum / l
        return result
    
    def onchange_product_list(self, cr, uid, ids, client_id, context=None):
        listing_obj = self.pool.get("cd.listing")
        listing_ids = listing_obj.search(cr, uid, [('client_id','=',client_id)])
        listings = listing_obj.read(cr, uid, listing_ids,['product_id'])
        
        product_list = []
        for listing in listings:
            product_list.append(listing['product_id'][0])
            
        vals = {}
        vals['product_list_ids'] = [[6,False,product_list]]
        if product_list or client_id == False:
            return {'value': vals}
        else:
            return {'value':vals, 'warning':{'title':'Ostrzeżenie','message':'Wybrany klient nie posiada Listingów.'}}
        
    def onchange_get_year_month(self, cr, uid, ids, plan_section_id, context=None):
        vals = {}
        domain = {}
        plan_section_obj = self.pool.get('cd.plan.section')
        plan_section = plan_section_obj.browse(cr, uid, plan_section_id)
        vals['year'] = plan_section.year
        vals['month'] = plan_section.month
        vals['client_id'] = ''

        partner_obj = self.pool.get('res.partner')
        client_ids = partner_obj.search(cr, uid, [('is_company','=',True),('parent_id','=',False),('section_id','=',plan_section.section_id.id)])
        domain['client_id'] = [('id', 'in', client_ids)]
        
        return {'value': vals, 'domain': domain}
    
    def open_plan_client(self, cr, uid, ids, context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Plan Client', 
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'res_id': ids[0],
            'target': 'self',
        }
        
    def recalculate_plan_products(self, cr, uid, ids, context=None):
        #pdb.set_trace()
        
        client_ref = ''
        w = self.browse(cr, uid, ids[0])
        if w.client_id.ref != False:
            client_ref = w.client_id.ref
        
        plan_product_obj = self.pool.get('cd.plan.product')
        listing_obj = self.pool.get('cd.listing')
        
        plan_product_ids = plan_product_obj.search(cr, uid, [('plan_client_id', '=', w.id)])
        listing_ids = listing_obj.search(cr, uid, [('client_id', '=', w.client_id.id),('status_l','=','0')])
        
        listing_products = self._get_listing_dict(cr, uid, listing_ids)
        
        today = datetime.date.today()
        
        plan_product_obj.unlink(cr, uid, plan_product_ids)
        
        for product_movex in listing_products:
            if w.client_id.ref == False:
                avg_qty = 0
            else:
                avg_qty = self._calculate_avg_sales(cr, uid, client_ref, product_movex, today)
            
            product_vals = {
                        'product_id': listing_products[product_movex],
                        'year': w.year,
                        'month': w.month,
                        'plan_client_id': w.id,
                        'plan_count': avg_qty,
                        'propo_count': avg_qty,
                        }
            plan_product_obj.create(cr, uid, product_vals)
        
        return True
                
            
    def _get_listing_dict(self, cr, uid, listing_ids):
        listing_obj = self.pool.get('cd.listing')
        listing_products = {}
        for listing in listing_obj.browse(cr, uid, listing_ids):
            if listing.product_id.default_code:
                listing_products[listing.product_id.default_code.encode('cp1250')] = listing.product_id.id
        
        return listing_products
        
        
        
        
        

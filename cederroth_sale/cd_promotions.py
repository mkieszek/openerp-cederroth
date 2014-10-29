# -*- coding: utf-8 -*-
"""
@author: mbereda
"""

from openerp.osv import fields, osv
from datetime import timedelta
from openerp.addons.mail.mail_message import decode

import cd_promotions_stage
import datetime
import pdb

class cd_promotions(osv.Model):
    _name = "cd.promotions"
    _inherit = 'mail.thread'
    _description = "Akcje promocyjne"
    _rec_name = "promotions_name"
    
    
    def _get_value_discount_prom(self, cr, uid, ids, name, arg, context=None):
        val={}
        for promotions in self.browse(cr, uid, ids):
            value_dc = 0.0
            value_dp = 0.0
            nsh_promo = 0.0
            
            for product_rel in promotions.product_rel_ids:
                if product_rel.discount_prom > product_rel.promotions_id.discount_promo:
                    nsh_price = product_rel.nsh_price
                    nsh_promo += nsh_price
                    prom_price = nsh_price-nsh_price*float(product_rel.promotions_id.discount_promo)/100
                    value_dc += product_rel.amount_product*(product_rel.nsh_price-prom_price)
                    value_dp += product_rel.amount_product*((product_rel.nsh_price-product_rel.prom_price)-(product_rel.nsh_price-prom_price))
                else:
                    value_dc += product_rel.amount_product*(product_rel.nsh_price-product_rel.prom_price)
                
            for gratis in promotions.gratis_ids:
                if gratis.distribution == '02':
                    value_dc += gratis.value_discount
            val[promotions.id] = {
                                  'value_discount_contract': value_dc,
                                  'value_discount_promo': value_dp,
                                  'nsh_promo': nsh_promo,
                                  }
        return val
    
    def _get_contract_cost(self, cr, uid, ids, name, arg, context=None):
        val={}
        discount_client_obj  = self.pool.get('cd.discount.partner')
        

        for promotions in self.browse(cr, uid, ids):
            amount = 0.00
            
            discount_ids = discount_client_obj.search(cr, uid, [('client_id','=', promotions.client_id.id)])
            discount_dict = {}
            if discount_ids:
                for discount in discount_client_obj.browse(cr, uid, discount_ids):
                    discount_dict[discount.product_category.id] = [discount.discount_front, discount.discount_back]
                    
                    
            for product in promotions.product_rel_ids:
                
                if product.product_id.product_mark.id in discount_dict:
                    discount = discount_dict[product.product_id.product_mark.id]
                    amount += product.nsh_price*product.amount_product * (discount[1]/100)
                else:    
                    amount += product.nsh_price*product.amount_product*(promotions.client_id.discount_back/100)
            val[promotions.id] = amount
        return val
    
    def _get_value_nsh(self, cr, uid, ids, name, arg, context=None):
        val={}
        for promotions in self.browse(cr, uid, ids):
            amount = 0.00
            for product in promotions.product_rel_ids:
                amount += product.nsh_price*product.amount_product
                
            for gratis in promotions.gratis_ids:
                if gratis.distribution == '02':
                    amount += gratis.front_price*gratis.count
            val[promotions.id] = amount
        return val
    
    def _get_value_prom(self, cr, uid, ids, name, arg, context=None):
        val={}
        for promotions in self.browse(cr, uid, ids):
            amount = 0.00
            for product in promotions.product_rel_ids:
                amount += product.prom_price*product.amount_product
                
            for gratis in promotions.gratis_ids:
                if gratis.distribution == '02':
                    amount += gratis.nsh_price*gratis.count
            val[promotions.id] = amount
        return val
    
    def _get_fixed_cost(self, cr, uid, ids, name, arg, context=None):
        val={}
        for promotions in self.browse(cr, uid, ids):
            amount = 0.00
            for cost in promotions.cost_promotions_ids:
                amount += cost.amount
                
            for gratis in promotions.gratis_ids:
                if gratis.distribution == '01':
                    amount += gratis.value_cogs
            val[promotions.id] = amount
        return val
    
    def _get_revenue(self, cr, uid, ids, name, arg, context=None):
        val={}
        for promotions in self.browse(cr, uid, ids):
            amount = 0.00
            amount = promotions.value_prom - (promotions.cogs + promotions.fixed_cost + promotions.contract_cost)
            val[promotions.id] = amount
        return val
    
    def _get_promo_format_count(self, cr, uid, ids, name, arg, context=None):
        val={}
        for promotion in self.browse(cr, uid, ids):
            count = 0
            for format in promotion.promo_format_ids:
                count += format.shops
            val[promotion.id] = count
        return val
    
    def _get_product_list(self, cr, uid, ids, name, arg, context=None):
        val={}
        for promotions in self.browse(cr, uid, ids):
            listing_obj = self.pool.get("cd.listing")
            listing_ids = listing_obj.search(cr, uid, [('client_id','=',promotions.client_id.id),('status_l','=','0')])
            listings = listing_obj.read(cr, uid, listing_ids,['product_id'])
            
            product_list = []
            for listing in listings:
                product_list.append(listing['product_id'][0])
            val[promotions.id] = [[6, False, product_list]]
        return val
    
    def _get_margin_warning(self, cr, uid, ids, name, arg, context=None):
        val={}
        for promotions in self.browse(cr, uid, ids):
            cd_config_obj = self.pool.get('cd.config.settings')
            cd_config_id = cd_config_obj.search(cr, uid, [])
            min_margin_prom = cd_config_obj.browse(cr, uid, cd_config_id[-1]).min_margin_prom

            if min_margin_prom < promotions.gpp:
                val[promotions.id] = True
            else:
                val[promotions.id] = False
        return val
    
    def _get_edit_date(self, cr, uid, ids, name, arg, context=None):
        val={}
        for promotions in self.browse(cr, uid, ids):
            cd_config_obj = self.pool.get('cd.config.settings')
            cd_config_id = cd_config_obj.search(cr, uid, [])
            plan_prom = cd_config_obj.browse(cr, uid, cd_config_id[-1]).plan_prom
            start_date = datetime.datetime.strptime(promotions.start_date,"%Y-%m-%d").date()
            val[promotions.id] = (start_date - timedelta(days=plan_prom)).strftime("%Y-%m-%d")
        return val
    
    def _get_gratis(self, cr, uid, ids, name, arg, context=None):
        val={}
        for promotions in self.browse(cr, uid, ids):
            amount = 0.0
            for gratis in promotions.gratis_ids:
                if gratis.distribution == '01':
                    amount += gratis.value_cogs
            
            val[promotions.id] = amount
        return val
    
    def _get_procent_nsh_promo(self, cr, uid, ids, name, arg, context=None):
        #pdb.set_trace()
        val = {}
        plan_client_obj = self.pool.get('cd.plan.client')
        
        for promotion in self.browse(cr, uid, ids):
            procent_nsh_promo = 0.0
            client_id = promotion.client_id.id
            discount_from = datetime.datetime.strptime(promotion.discount_from,"%Y-%m-%d").date()
            month = str(discount_from.month).zfill(2)
            year = discount_from.year
            plan_client_id = plan_client_obj.search(cr, uid, [('year','=', year),('month','=', month),('client_id','=',client_id)])
            if plan_client_id:
                plan_client = plan_client_obj.browse(cr, uid, plan_client_id)[0]
                plan_total = plan_client.plan_plan
                if plan_total > 0:
                    procent_nsh_promo = promotion.value_prom /plan_total
            val[promotion.id] = procent_nsh_promo * 100
        return val
    
    def _get_value(self, cr, uid, ids, name, arg, context=None):
        val = {}
        discount_client_obj  = self.pool.get('cd.discount.partner')
        rcost_obj = self.pool.get('cd.report.cost')
        for promotion in self.browse(cr, uid, ids):
            gross_sales = 0.0
            discount_front = 0.0
            discount_promo_contract = 0.0
            discount_promo_budget = 0.0
            nsh = 0.0
            trade_promo = 0.0
            nsv = 0.0
            cogs = 0.0 
            other_cogs = 0.0
            gp = 0.0
            gpp = 0.0
            coop = 0.0
            other_marketing = 0.0
            contrib = 0.0
            contribp = 0.0
            
            discount_ids = discount_client_obj.search(cr, uid, [('client_id','=', promotion.client_id.id)])
            discount_dict = {}
            if discount_ids:
                for discount in discount_client_obj.browse(cr, uid, discount_ids):
                    discount_dict[discount.product_category.id] = [discount.discount_front, discount.discount_promo]
                    
            for product in promotion.product_rel_ids:
                if product.product_id.product_mark.id in discount_dict:
                    discount = discount_dict[product.product_id.product_mark.id]
                    disc_front = discount[0]
                    disc_promo = discount[1]
                else:
                    disc_front = promotion.client_id.discount_front
                    disc_promo = promotion.client_id.discount_promo
                    
                list_price = product.list_price
                product_count = product.amount_product
                disc_product = product.discount_prom
                gross_sales += list_price*product_count
                front_price = (list_price - list_price*(disc_front/100))
                discount_front += (list_price*(disc_front/100))*product_count

                if disc_product - disc_promo <= 0:
                    discount_promo_contract += front_price*(disc_product/100)*product_count
                else:
                    discount_promo_contract += front_price*(disc_promo/100)*product_count
                    discount_promo_budget += front_price*((disc_product-disc_promo)/100)*product_count
                
                cogs += product.product_id.price_cogs*product_count
            
            for gratis in promotion.gratis_ids:
                if gratis.distribution == '02':
                    cogs += gratis.value_cogs
                elif gratis.distribution == '01':
                    other_cogs += gratis.value_cogs
                        
            rcost_ids = rcost_obj.search(cr, uid, [('promotion_id','=',promotion.id)])
            
            for rcost in rcost_obj.browse(cr, uid, rcost_ids):
                if rcost.type == 'other marketing':
                    other_marketing += rcost.value
                if rcost.type == 'other cogs':
                    other_cogs += rcost.value
                if rcost.type == 'coop':
                    coop += rcost.value
                if rcost.type == 'trade promo':
                    trade_promo += rcost.value
            
            nsh = gross_sales - discount_front-discount_promo_contract-discount_promo_budget
            
            nsv = nsh - trade_promo
            
            gp = nsv - cogs - other_cogs
            
            if gp != 0.0 and nsv != 0.0:
                gpp = gp/nsv*100
            
            contrib = nsv - cogs - other_cogs - coop - other_marketing
            
            if contrib != 0.0 and nsv != 0.0:
                contribp = contrib/nsv*100
                    
            val[promotion.id] = {
                                 'gross_sales': gross_sales,
                                 'discount_front': discount_front,
                                 #'discount_promo': discount_promo,
                                 'discount_promo_contract': discount_promo_contract,
                                 'discount_promo_budget': discount_promo_budget,
                                 'nsh': nsh,
                                 'trade_promo': trade_promo,
                                 'nsv': nsv,
                                 'cogs': cogs,
                                 'other_cogs': other_cogs,
                                 'gp': gp,
                                 'gpp': gpp,
                                 'coop': coop,
                                 'other_marketing': other_marketing,
                                 'contrib': contrib,
                                 'contribp': contribp,
                                 }
        return val
        
    
    def _get_email_link(self, cr, uid, ids, name, arg, context=None):
        
        vals = {}
        for promotion in self.browse(cr, uid, ids):
            cd_config_obj = self.pool.get('cd.config.settings')
            cd_config_id = cd_config_obj.search(cr, uid, [])
            cd_crm = cd_config_obj.browse(cr, uid, cd_config_id[-1]).cd_crm
            action_id = self.pool.get('ir.actions.actions').search(cr, uid, [('name','=','Rabaty z promocji')])
            vals[promotion.id] = ("http://%s/?db=%s#page=0&limit=&view_type=list&model=cd.product.rel&action=%s")%(cd_crm, cr.dbname, str(action_id[0]))
                
        return vals
    
    def _get_bok_email(self, cr, uid, ids, name, arg, context=None):
        
        vals = {}
        
        for promotion in self.browse(cr, uid, ids):
            vals[promotion.id] = promotion.client_id.bok_user_id.email
        
        return vals

    def _get_value_report(self, cr, uid, ids, name, arg, context=None):
        vals = {}
        
        for promo in self.browse(cr, uid, ids):
            communication_form = ''
            for item in promo.communication_ids:
                if communication_form != '':
                    communication_form += ', '
                communication_form += item.name
        vals[promo.id] = {
                          'communication_form': communication_form,
                         }
        return vals

    def _get_str_sales_director_ids(self, cr, uid, ids, name, arg, context=None):
        val={}
        user_obj = self.pool.get('res.users')
        user_ids = user_obj.search(cr,uid,[('groups_id.name','=','Sales Director'),('id','!=',1)])
        for lead in self.browse(cr, uid, ids):
            val[lead.id] = (''.join(str(user.partner_id.id)+',' for user in user_obj.browse(cr, uid ,user_ids)))[:-1]
        return val
    
    _columns = {
        'promotions_name': fields.char("Nazwa promocji", size=255, required=True),
        'name': fields.char('Name'),
        'create_uid': fields.many2one('res.users', "Twórca"),
        'start_date': fields.date("Data początkowa", required=True),
        'stop_date': fields.date("Data końcowa", required=True),
        'client_id': fields.many2one('res.partner', "Klient", required=True),
        'email_link' : fields.function(_get_email_link, type="char", store=False, string="Email from"),
        'bok_email' :fields.function(_get_bok_email, type="char", store=False, string="Email to"),
        'discount_front': fields.related('client_id', 'discount_front', type="float", string="Rabat frontowy (%)", readonly=True),
        'discount_back': fields.related('client_id', 'discount_back', type="float", string="Rabat backowy (%)", readonly=True),
        'discount_promo': fields.related('client_id', 'discount_promo', type="float", string="Rabat promocyjny (%)", readonly=True),
        'monitored': fields.boolean("Akcja monitorowana"),
        'stage_id': fields.many2one('cd.promotions.stage', 'Status', help='Aktualny status promocji', domain="[('sequence', 'in', [10,20,50])]", ondelete="set null", track_visibility='onchange'),
        'product_rel_ids': fields.one2many('cd.product.rel','promotions_id',"Produkty"),
        'discount_from': fields.date("Rabat od", required=True),
        'discount_to' :  fields.date("Rabat do"),
        'state': fields.related('stage_id', 'state', type="selection", store=True,
                selection=cd_promotions_stage.AVAILABLE_STATES, string="Status", readonly=True,),
        'sequence': fields.related('stage_id', 'sequence', type="integer", store=True, string="Status", readonly=True,),
        'create_uid':fields.many2one('res.users', 'Twórca', size=64),
        'start_month': fields.char('Miesiąc rozpoczącia'),
        'start_year': fields.char('Rok rozpoczęcia'),
        'cost_promotions_ids': fields.one2many('cd.cost.promotions', 'promotions_id', 'Dodatkowe koszty akcji'),
        'product_id': fields.many2one('product.product', "Wybierz produkt"),
        'product_list_ids' : fields.function(_get_product_list, relation='product.product', type='many2many', string='Produkty klienta', store=False),
        'attention': fields.text("Uwagi"),
        'promotion_rules': fields.text("Zasady akcji"),
        'edit_date': fields.function(_get_edit_date, type='date', string='Ostateczna data edycji', store=False),
        'gratis_ids' : fields.one2many('cd.gratis','promotions_id','Gratisy'),
        'type_promotions_id': fields.many2one('cd.type.promotions', 'Typ promocji', required=True),
        'product_category': fields.many2one('product.category', 'Marka', domain="[('parent_id','=',False)]", required=True),
        'accept_tmm': fields.boolean('Akceptacja Trade Marketing Manager', readonly=True),
        'accept_trade_director': fields.boolean('Akceptacja Dyrektor Handlowy', readonly=True),
        'accept_finances_director': fields.boolean('Akceptacja Dyrektor Finansowy', readonly=True),
        'accept_country_manager': fields.boolean('Akceptacja Country Manager', readonly=True),
        
        #bilans
        'margin_warning': fields.function(_get_margin_warning, type="boolean", string="Ostrzeżenie o niskiej marży", store=False),
        'gross_sales': fields.function(_get_value, type="float", string='Gross sales', readonly=True, store=True, multi="get_value"),
        'discount_front': fields.function(_get_value, type="float", string='Rabat front', readonly=True, store=True, multi="get_value"),
        'discount_promo_contract': fields.function(_get_value, type="float", string='Rabat promo kontraktowy', readonly=True, store=True, multi="get_value"),
        'discount_promo_budget': fields.function(_get_value, type="float", string='Rabat promo pozabudżetowy', readonly=True, store=True, multi="get_value"),
        'nsh': fields.function(_get_value, type="float", string='NSH', readonly=True, store=True, multi="get_value"),
        'trade_promo': fields.function(_get_value, type="float", string='Trade promo', readonly=True, store=True, multi="get_value"),
        'nsv': fields.function(_get_value, type="float", string='NSV', readonly=True, store=True, multi="get_value"),
        'cogs': fields.function(_get_value, type="float", string='COGS', readonly=True, store=True, multi="get_value"),
        'other_cogs': fields.function(_get_value, type="float", string='Other COGS', readonly=True, store=True, multi="get_value"),
        'gp': fields.function(_get_value, type="float", string='GP', readonly=True, store=True, multi="get_value"),
        'gpp': fields.function(_get_value, type="float", string='GP %', readonly=True, store=True, multi="get_value"),
        'coop': fields.function(_get_value, type="float", string='COOP', readonly=True, store=True, multi="get_value"),
        'other_marketing': fields.function(_get_value, type="float", string='Other Marketing', readonly=True, store=True, multi="get_value"),
        'contrib': fields.function(_get_value, type="float", string='Contrib.', readonly=True, store=True, multi="get_value"),
        'contribp': fields.function(_get_value, type="float", string='Contrib. %', readonly=True, store=True, multi="get_value"),
        
        'promo_format_ids' : fields.many2many('cd.client.format', string='Formaty objęte promocją'),
        'promo_format_count' : fields.function(_get_promo_format_count, type="integer", string="Ilość sklepów objętych promocją"),
        'distribution' : fields.selection([('lokalne', 'Lokalne'), ('centralne', 'Centralne')], 'Zatowarowanie'),
        'display_ids' : fields.many2many('cd.display', string='Ekspozycja'),
        'display_count' : fields.integer('Ilość sklepów objętych ekspozycją'),
        'task_sale_ids' : fields.many2many('cd.task.sale', string='Zadania PH'),
        'task_merchandising_ids' : fields.many2many('cd.task.merchandising', string='Zadania Merchandising'),
        'monitor_merchand' : fields.boolean('Monitoring merchandising'),
        'communication_ids' : fields.many2many('cd.communication', string="Forma komunikacji"), 

        #pola do raportu kalendarza akcji promo
        'communication_form' : fields.function(_get_value_report, type="float", string='GP', readonly=True, store=False, multi="get_value"),
        
        'str_sales_director_ids': fields.function(_get_str_sales_director_ids, type='char', string="Dyrektorzy handlowi", store=False, readonly=True),

    }
    
    _defaults = {
        'stage_id': lambda s, cr, uid, c: s.pool.get('cd.promotions.stage').search(cr, uid, [('sequence','=',10)])[0],
        'sequence': 10
    }
    
    def create(self, cr, uid, data, context=None):
        users_obj = self.pool.get('res.users')
        
        if '__copy_data_seen' in context:
            cd_config_obj = self.pool.get('cd.config.settings')
            cd_config_id = cd_config_obj.search(cr, uid, [])
            cd_plan_prom = cd_config_obj.browse(cr, uid, cd_config_id[-1]).plan_prom
            
            date_min = datetime.date.today()+timedelta(days=cd_plan_prom)
            data['discount_from'] = date_min.strftime('%Y-%m-%d')
            data['start_date'] = date_min.strftime('%Y-%m-%d')
            data['stop_date'] = (date_min+timedelta(days=1)).strftime('%Y-%m-%d')
            
        self.on_change_start_date(cr, uid, None, data['start_date'], context=context)
        self.validation_date(cr, uid, data['start_date'], data['stop_date'], context=context)

        months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        
        start_month = datetime.datetime.strptime(data['discount_from'],"%Y-%m-%d").month
        start_year = datetime.datetime.strptime(data['discount_from'],"%Y-%m-%d").year
        data['start_month'] = str(start_month).zfill(2)
        data['start_year'] = start_year
               
        stage_id = self.pool.get('cd.promotions.stage').search(cr, uid, [('sequence','=',10)])
        data['stage_id'] = stage_id[0]
                
        promotions_id = super(cd_promotions, self).create(cr, uid, data, context=context)
        
        #na prośbę Krzysiu wyłączyliśmy dodawanie produktów promowanych.
        #listing_obj = self.pool.get('cd.listing')
        #pmark_obj = self.pool.get('cd.plan.mark')
        #pmark_ids = pmark_obj.search(cr, uid, [('month','=',str(start_month).zfill(2)),('year','=',start_year)])
        #
        #for pmark in pmark_obj.browse(cr, uid, pmark_ids):
        #    data_prod = {}
        #    if listing_obj.search(cr, uid, [('product_id','=',pmark.product_id.id),('client_id','=',data['client_id'])]):
        #        data_prod['product_id'] = pmark.product_id.id
        #        data_prod['promotions_id'] = promotions_id
        #        self.pool.get('cd.product.rel').create(cr, uid, data_prod, context=None)   
            
        return promotions_id
    
    def write(self, cr, uid, ids, vals, context=None):
        users_obj = self.pool.get('res.users')
        promotion = self.browse(cr, uid, ids[0])
        
        if 'discount_from' in vals:
            start_month = datetime.datetime.strptime(vals['discount_from'],"%Y-%m-%d").month
            start_year = datetime.datetime.strptime(vals['discount_from'],"%Y-%m-%d").year
            vals['start_month'] = str(start_month).zfill(2)
            vals['start_year'] = start_year
        
        if 'stage_id' in vals:
            change_stage_id = self.pool.get('cd.promotions.stage').browse(cr, uid, vals['stage_id'])
            current_stage_id = self.browse(cr, uid, ids[0]).stage_id
            
            if change_stage_id.sequence == 50:
                template = self.pool.get('ir.model.data').get_object(cr, uid, 'cederroth_sale', 'email_template_cd_promotion_confirmed')
                self.pool.get('email.template').send_mail(cr, uid, template.id, ids[0], force_send=True, context=context)
       
            
            if change_stage_id.sequence < current_stage_id.sequence and not current_stage_id.sequence < 50:
                raise osv.except_osv(decode('Ostrzeżenie'), decode('Status akcji promocyjnej nie może zostać cofnięty'))
            elif current_stage_id.sequence == 10 and change_stage_id.sequence != 20 and change_stage_id.sequence != 90:
                raise osv.except_osv(decode('Ostrzeżenie'), decode('Status może zostać zmieniony tylko na "Do akceptacji"'))
            elif current_stage_id.sequence == 20 and change_stage_id.sequence >= 50:
                raise osv.except_osv(decode('Ostrzeżenie'), decode('Nie można zmienić na wybrany status'))
            elif current_stage_id.sequence == 20 and change_stage_id.sequence !=10:
                users_obj = self.pool.get('res.users')
                group_id = self.pool.get('res.groups').search(cr,uid,[('name','=','KAM')])
                user_ids = users_obj.search(cr,uid,[('groups_id','in',group_id),('id','!=',1)])
                if uid in user_ids:
                    raise osv.except_osv(decode('Ostrzeżenie'), decode('Nie można zmienić na wybrany status'))
            elif current_stage_id.sequence == 30 and change_stage_id.sequence not in [10,50,90]:
                raise osv.except_osv(decode('Ostrzeżenie'), decode('Status może zostać zmieniony tylko na "W przygotowaniu","Potwierdzona" lub "Anulowano"'))
            elif current_stage_id.sequence == 40 and change_stage_id.sequence not in [10,90]:
                raise osv.except_osv(decode('Ostrzeżenie'), decode('Status może zostać zmieniony tylko na "W przygotowaniu" lub "Anulowano"'))
            elif current_stage_id.sequence == 50 and change_stage_id.sequence not in [60,90]:
                raise osv.except_osv(decode('Ostrzeżenie'), decode('Status można zmienić tylko na następny'))
            elif current_stage_id.sequence >= 60 and current_stage_id.sequence <= 80 and change_stage_id.sequence - current_stage_id.sequence != 10:
                raise osv.except_osv(decode('Ostrzeżenie'), decode('Nie można zmienić na wybrany status'))
            elif current_stage_id.sequence == 80:
                raise osv.except_osv(decode('Ostrzeżenie'), decode('Nie można anulować rozliczonej akcji'))
            
            if current_stage_id.sequence == 10 and not promotion.product_rel_ids:
                raise osv.except_osv(decode('Ostrzeżenie'), decode('Do akcji promocyjnej nie zostały dodane produkty')) 
            elif current_stage_id.sequence == 10 and change_stage_id.sequence == 20:
                client = promotion.client_id
                users_obj = self.pool.get('res.users')
                group_obj = self.pool.get('res.groups')
                mail_to = ''
                
                if client.section_id and client.section_id.user_id and client.section_id.user_id.email:
                    mail_to += client.section_id.user_id.email
                
                    if mail_to != '':
                        cd_config_obj = self.pool.get('cd.config.settings')
                        cd_config_id = cd_config_obj.search(cr, uid, [])
                        cd_crm = cd_config_obj.browse(cr, uid, cd_config_id[-1]).cd_crm
                        url = ("http://%s/?db=%s#id=%s&view_type=form&model=cd.promotions")%(cd_crm, cr.dbname, promotion.id)
                        vals_email = (url)
                        subject = 'Akcja promocyjna'
                        body = decode("W platformie znajduje się akcja promocyjna do akceptacji <br/><a href='%s'>Link do akcji promocyjnej</a>") % vals_email
                        self.pool.get('product.product').send_mail(cr, uid, body, subject, mail_to)
                        
            elif current_stage_id.sequence == 20 and change_stage_id.sequence == 30:
                #Powiadomienie Country Managera, Dyrektora Finansowego i Dyrektora Handlowego jeżeli rabat pozabudżetowy > 0
                group_obj = self.pool.get('res.groups')
                if promotion.discount_promo_budget > 0:
                    group_id = group_obj.search(cr,uid,[('name','in',['Country Manager','Finances Director','Trade Director'])])
                    user_ids = users_obj.search(cr,uid,[('groups_id','in',group_id),('id','!=',1)])
                    mail_to = ''

                    for user in users_obj.browse(cr, uid, user_ids):
                        if user.email:
                            mail_to += user.email + ', '
                
                    if mail_to != '':
                        cd_config_obj = self.pool.get('cd.config.settings')
                        cd_config_id = cd_config_obj.search(cr, uid, [])
                        cd_crm = cd_config_obj.browse(cr, uid, cd_config_id[-1]).cd_crm
                        url = ("http://%s/?db=%s#id=%s&view_type=form&model=cd.promotions")%(cd_crm, cr.dbname, promotion.id)
                        vals_email = (url)
                        subject = 'Akcja promocyjna'
                        body = decode("W platformie znajduje się akcja promocyjna do akceptacji, w której rabat promocyjny został przekroczony.<br/><a href='%s'>Link do akcji promocyjnej</a>") % vals_email
                        self.pool.get('product.product').send_mail(cr, uid, body, subject, mail_to)
                        
                #Powiadomienie Dyrektora Handlowego o akceptacji akcji promocyjnej poniżej progu gp.
                self.send_mail_to_sales_director(cr, uid, promotion.id)
                        
        super(cd_promotions, self).write(cr, uid, ids, vals, context=context)
        return True
    
    def send_mail_to_sales_director(self, cr, uid, promotion_id, context=None):
        promo = self.browse(cr, uid, promotion_id)
        if promo.margin_warning == False:
            template = self.pool.get('ir.model.data').get_object(cr, uid, 'cederroth_sale', 'cd_email_template_accept_promo')
            self.pool.get('email.template').send_mail(cr, uid, template.id, promo.id, force_send=True, context=context)
        return True
    
    def on_change_start_date(self, cr, uid, vals, start_date, context=None):
        cd_config_obj = self.pool.get('cd.config.settings')
        cd_config_id = cd_config_obj.search(cr, uid, [])
        cd_plan_prom = cd_config_obj.browse(cr, uid, cd_config_id[-1]).plan_prom
        
        date_min = datetime.date.today()+timedelta(days=cd_plan_prom)
        start_date = datetime.datetime.strptime(start_date,"%Y-%m-%d").date()
        if date_min > start_date:
            raise osv.except_osv(decode('Błąd'), decode('Minimalna data rozpoczęcia to:\n %s')%date_min.strftime("%d.%m.%Y"))
        return True
    
    def on_change_stop_date(self, cr, uid, vals, stop_date, context=None):
        vals = {}
        vals = {
            'discount_to' : stop_date
        }
        return {'value' : vals}
    
    def validation_date(self, cr, uid, start_date, stop_date, context=None):
        start_date = datetime.datetime.strptime(start_date,"%Y-%m-%d").date()
        stop_date = datetime.datetime.strptime(stop_date,"%Y-%m-%d").date()
        if stop_date < start_date:
            raise osv.except_osv(decode('Błąd'), decode('Data końcowa nie może być przed datą początkową !'))
        return True
    
    def notification_discount(self, cr, uid, context=None):
        cd_config_obj = self.pool.get('cd.config.settings')
        discount_date = datetime.date.today()+timedelta(days=10)
        promotions_ids = self.search(cr, uid, [('discount_from','=',discount_date),('monitored','=',True),('sequence','=',50)])
        for promotion in self.browse(cr, uid, promotions_ids):
            users_obj = self.pool.get('res.users')
            group_id = self.pool.get('res.groups').search(cr,uid,[('name','=','Trade Marketing Manager')])
            user_ids = users_obj.search(cr,uid,[('groups_id','in',group_id),('id','!=',1)])
            users = users_obj.browse(cr, uid, user_ids)
            mail_to = ''
            for user in users:
                if user.email and user.email != '':
                    mail_to += user.email+', '
            tms_user = promotion.client_id.section_id.tms_user_id
            if tms_user.email:
                mail_to += tms_user.email
            if mail_to != '':
                create_uid = users_obj.browse(cr, uid, uid)
                cd_config_id = cd_config_obj.search(cr, uid, [])
                cd_crm = cd_config_obj.browse(cr, uid, cd_config_id[-1]).cd_crm
                url = ("http://%s/?db=%s#id=%s&view_type=form&model=cd.promotions")%(cd_crm, cr.dbname, promotion.id)
                vals = (discount_date, promotion.client_id.name, url)
                subject = 'Termin obowiązywania rabatu'
                body = decode("Dnia %s zaczyna się termin obowiązywania rabatu dla klienta %s <br/><a href='%s'>Link do akcji promocyjnej</a>") % vals
                self.pool.get('product.product').send_mail(cr, uid, body, subject, mail_to)
                
        discount_date_2 = datetime.date.today()+timedelta(days=2)
        promotions_ids_2 = self.search(cr, uid, [('discount_from','=',discount_date_2),('sequence','=',50)])
        
        for promotion in self.browse(cr, uid, promotions_ids_2):
            users_obj = self.pool.get('res.users')
            group_id = self.pool.get('res.groups').search(cr,uid,[('name','=','Logistics Manager')])
            user_ids = users_obj.search(cr,uid,[('groups_id','in',group_id),('id','!=',1)])
            users = users_obj.browse(cr, uid, user_ids)
            mail_to = ''
            for user in users:
                if user.email and user.email != '':
                    mail_to += user.email+', '
            if mail_to != '':
                create_uid = users_obj.browse(cr, uid, uid)
                cd_config_id = cd_config_obj.search(cr, uid, [])
                cd_crm = cd_config_obj.browse(cr, uid, cd_config_id[-1]).cd_crm
                url = ("http://%s/?db=%s#id=%s&view_type=form&model=cd.promotions")%(cd_crm, cr.dbname, promotion.id)
                subject = 'Termin obowiązywania rabatu'
                
                rows = '<tr><td colspan="2"><b>Produkty akcji promocyjnej:</b></td></tr>'
                l = 0
                for product in promotion.product_rel_ids:
                    l +=1
                    rows += '<tr><td style="width: 20px;">%s.</td><td>%s</td></tr>'%(l, product.product_name)
                
                vals = (discount_date_2, promotion.client_id.name, rows, url)                
                body = decode("Dnia %s zaczyna się termin obowiązywania rabatu dla klienta %s <br/><br/><table>%s</table><br/><a href='%s'>Link do akcji promocyjnej</a>") % vals
                self.pool.get('product.product').send_mail(cr, uid, body, subject, mail_to)
        
        cd_config_id = cd_config_obj.search(cr, uid, [])
        info_guardian = cd_config_obj.browse(cr, uid, cd_config_id[-1]).info_guardian
        discount_date_3 = datetime.date.today()+timedelta(days=info_guardian)
        promotions_ids_3 = self.search(cr, uid, [('discount_from','=',discount_date_3),('sequence','=',50)])
        
        for promotion in self.browse(cr, uid, promotions_ids_3):
            if promotion.client_id.user_id and promotion.client_id.user_id.partner_id.email:
                template = self.pool.get('ir.model.data').get_object(cr, uid, 'cederroth_sale', 'cd_email_template_accept_promo_discount2')
                self.pool.get('email.template').send_mail(cr, uid, template.id, promotion.id, force_send=True, context=context)
        return True
    
    def notification_start_date(self, cr, uid, context=None):
        start_date = datetime.date.today()+timedelta(days=10)
        promotions_ids = self.search(cr, uid, [('start_date','=',start_date),('sequence','=',50)])
        #powiadomienie na 10 dni przed rozpoczęciem do PH
        for promotion in self.browse(cr, uid, promotions_ids):
            mail_to = ''
            for affiliate in promotion.client_id.affiliate_ids:
                if affiliate.ph_user_id and affiliate.ph_user_id.email:
                    mail_to += affiliate.ph_user_id.email+', '
            if mail_to != '':
                cd_config_obj = self.pool.get('cd.config.settings')
                cd_config_id = cd_config_obj.search(cr, uid, [])
                cd_crm = cd_config_obj.browse(cr, uid, cd_config_id[-1]).cd_crm
                url = ("http://%s/?db=%s#id=%s&view_type=form&model=cd.promotions")%(cd_crm, cr.dbname, promotion.id)
                vals = (promotion.client_id.name, url)
                subject = 'Rozpoczęcie akcji promocyjnej'
                body = decode("Za 10 dni rozpocznie się akcja promocyjna dla Twojego klienta %s <br/><a href='%s'>Link do akcji promocyjnej</a>") % vals
                self.pool.get('product.product').send_mail(cr, uid, body, subject, mail_to)
                    
        promotions_mon_ids = self.search(cr, uid, [('start_date','=',start_date),('sequence','=',50),('monitored','=',True)])
        #powiadomienie jeżeli monitorowana na 10 dni przed rozpoczęciem do TMS i TMM
        for promotion in self.browse(cr, uid, promotions_mon_ids):
            users_obj = self.pool.get('res.users')
            group_id = self.pool.get('res.groups').search(cr,uid,[('name','=','Trade Marketing Manager')])
            user_ids = users_obj.search(cr,uid,[('groups_id','in',group_id),('id','!=',1)])
            users = users_obj.browse(cr, uid, user_ids)
            mail_to = ''
            for user in users:
                if user.email and user.email != '':
                    mail_to += user.email+', '
            tms_user = promotion.client_id.section_id.tms_user_id
            if tms_user.email:
                mail_to += tms_user.email
            if mail_to != '':
                cd_config_obj = self.pool.get('cd.config.settings')
                cd_config_id = cd_config_obj.search(cr, uid, [])
                cd_crm = cd_config_obj.browse(cr, uid, cd_config_id[-1]).cd_crm
                url = ("http://%s/?db=%s#id=%s&view_type=form&model=cd.promotions")%(cd_crm, cr.dbname, promotion.id)
                vals = (promotion.client_id.name, url)
                subject = 'Rozpoczęcie akcji promocyjnej'
                body = decode("Za 10 dni rozpocznie się akcja promocyjna dla klienta %s <br/><a href='%s'>Link do akcji promocyjnej</a>") % vals
                self.pool.get('product.product').send_mail(cr, uid, body, subject, mail_to)
        return True
    
    def change_stage(self, cr, uid, context=None):
        cd_config_obj = self.pool.get('cd.config.settings')
        cd_config_id = cd_config_obj.search(cr, uid, [])
        plan_prom = cd_config_obj.browse(cr, uid, cd_config_id[-1]).plan_prom
        date = datetime.date.today()+timedelta(days=plan_prom)
        today = datetime.date.today()
        
        #Zaakceptowana -> Anulowana
        promotions_ids = self.search(cr, uid, [('sequence','in',[30]), ('start_date','<=', date)])
        if promotions_ids:
            stage_id = self.pool.get('cd.promotions.stage').search(cr, uid, [('sequence','=',90)])[0]
            for promotion in self.browse(cr, uid, promotions_ids):
                vals = {}
                vals['stage_id'] = stage_id
                self.write(cr, uid, [promotion.id], vals)
        #Do akceptacji -> Odrzucona
        promotions_ids_2 = self.search(cr, uid, [('sequence','in',[20]), ('start_date','<=', date)])
        if promotions_ids_2:
            stage_id = self.pool.get('cd.promotions.stage').search(cr, uid, [('sequence','=',40)])[0]
            for promotion in self.browse(cr, uid, promotions_ids_2):
                vals = {}
                vals['stage_id'] = stage_id
                self.write(cr, uid, [promotion.id], vals)
        #Potwierdzona -> W trakcie
        promotions_ids_3 = self.search(cr, uid, [('sequence','in',[50]), ('start_date','=', today)])
        if promotions_ids_3:
            stage_id = self.pool.get('cd.promotions.stage').search(cr, uid, [('sequence','=',60)])[0]
            for promotion in self.browse(cr, uid, promotions_ids_3):
                vals = {}
                vals['stage_id'] = stage_id
                self.write(cr, uid, [promotion.id], vals)
        #W trakcie -> Zakończona
        promotions_ids_4 = self.search(cr, uid, [('sequence','in',[60]), ('stop_date','=', today)])
        if promotions_ids_4:
            stage_id = self.pool.get('cd.promotions.stage').search(cr, uid, [('sequence','=',70)])[0]
            for promotion in self.browse(cr, uid, promotions_ids_4):
                vals = {}
                vals['stage_id'] = stage_id
                self.write(cr, uid, [promotion.id], vals)
                mail_to = ''
                if promotion.create_uid and promotion.create_uid != '':
                    mail_to += promotion.create_uid.email+', '
                if mail_to != '':
                    cd_config_obj = self.pool.get('cd.config.settings')
                    cd_config_id = cd_config_obj.search(cr, uid, [])
                    cd_crm = cd_config_obj.browse(cr, uid, cd_config_id[-1]).cd_crm
                    url = ("http://%s/?db=%s#id=%s&view_type=form&model=cd.promotions")%(cd_crm, cr.dbname, promotion.id)
                    subject = 'Akcja promocyjna została zakończona.'
                    vals = (promotion.client_id.name, url)                
                    body = decode("Akcja promocyjna klienta %s została zakończona i oczekuje na rozliczenie.<br/><a href='%s'>Link do akcji promocyjnej</a>") % vals
                    self.pool.get('product.product').send_mail(cr, uid, body, subject, mail_to)
                
        return True

    def add_product(self, cr, uid, ids, context=None):
        w = self.browse(cr, uid, ids[0])
        data = {}
        data['product_id'] = w.product_id.id
        
        for product in w.product_rel_ids:
            if product.product_id.id == w.product_id.id:
                raise osv.except_osv(decode('Ostrzeżenie'), decode('Ten produkt został już dodany.'))
        data['promotions_id'] = ids[0]
        self.pool.get('cd.product.rel').create(cr, uid, data, context=None)
        vals = {}
        vals['product_id'] = False
        self.write(cr, uid, ids, vals, context=None)
        return {'value': vals}
    #funkcja do automatycznego przeliczania bilansu akcji
    def auto_calculate_balance(self,cr, uid, context=None):
        promotion_ids = self.search(cr, uid, [])
        for id in promotion_ids:
            self.calculate_balance(cr, uid, [id], context)
            
    def calculate_balance(self, cr, uid, ids, context=None):
        w = self.browse(cr, uid, ids[0])
        vals = {}
        prod_rel_obj = self.pool.get('cd.product.rel')
        for prod in w.product_rel_ids:
            prod_rel_obj.write(cr, uid, [prod.id], vals, context=None)
        
        self.write(cr, uid, ids, vals, context=None)
        self.write(cr, uid, ids, vals, context=None)
        
        return True
    
    def onchange_product_list(self, cr, uid, ids, client_id, context=None):
        listing_obj = self.pool.get("cd.listing")
        listing_ids = listing_obj.search(cr, uid, [('client_id','=',client_id)])
        listings = listing_obj.read(cr, uid, listing_ids,['product_id'])
        
        product_list = []
        for listing in listings:
            product_list.append(listing['product_id'][0])
            
        vals = {}
        vals['product_list_ids'] = [[6,False,product_list]]
        if product_list:
            return {'value': vals}
        else:
            return {'value':vals, 'warning':{'title':'Ostrzeżenie','message':'Wybrany klient nie posiada Listingów.'}}
        
    def accept_tmm(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'accept_tmm': True})
        return True
        
    def accept_trade_d(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'accept_trade_director': True})
        return True
        
    def accept_finances_d(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'accept_finances_director': True})
        return True
        
    def accept_country_m(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'accept_country_manager': True})
        return True
    
    def accept_promotions(self, cr, uid, ids, context=None):
        stage_id = self.pool.get('cd.promotions.stage').search(cr, uid, [('sequence','=', 30)])[0]
        vals = {}
        vals['stage_id'] = stage_id
        self.write(cr, uid, ids, vals)
        
        mail_to = ''
        promotion = self.browse(cr, uid, ids[0])
        if promotion.create_uid.email and promotion.create_uid.email != '':
            mail_to += promotion.create_uid.email+', '
            
        """
        if promotion.margin_warning == False:
            users_obj = self.pool.get('res.users')
            group_id = self.pool.get('res.groups').search(cr,uid,[('name','=','Sales Director')])
            user_ids = users_obj.search(cr,uid,[('groups_id','in',group_id),('id','!=',1)])
            for user in users_obj.browse(cr, uid, user_ids):
                if user.email and user.email != '':
                    mail_to += user.email+', '
        """    
        if mail_to != '':
            cd_config_obj = self.pool.get('cd.config.settings')
            cd_config_id = cd_config_obj.search(cr, uid, [])
            cd_crm = cd_config_obj.browse(cr, uid, cd_config_id[-1]).cd_crm
            url = ("http://%s/?db=%s#id=%s&view_type=form&model=cd.promotions")%(cd_crm, cr.dbname, promotion.id)
            subject = 'Akcja promocyjna została zaakceptowana.'
            vals = (promotion.client_id.name, url)                
            body = decode("Akcja promocyjna klienta %s została zaakceptowana.<br/><a href='%s'>Link do akcji promocyjnej</a>") % vals
            self.pool.get('product.product').send_mail(cr, uid, body, subject, mail_to)
        return True
        
    def cancelled_promotions(self, cr, uid, ids, context=None):
        stage_id = self.pool.get('cd.promotions.stage').search(cr, uid, [('sequence','=', 40)])[0]
        vals = {}
        vals['stage_id'] = stage_id
        self.write(cr, uid, ids, vals)
        
        mail_to = ''
        promotion = self.browse(cr, uid, ids[0])
        if promotion.create_uid.email and promotion.create_uid.email != '':
            mail_to += promotion.create_uid.email+', '
        if mail_to != '':
            cd_config_obj = self.pool.get('cd.config.settings')
            cd_config_id = cd_config_obj.search(cr, uid, [])
            cd_crm = cd_config_obj.browse(cr, uid, cd_config_id[-1]).cd_crm
            url = ("http://%s/?db=%s#id=%s&view_type=form&model=cd.promotions")%(cd_crm, cr.dbname, promotion.id)
            subject = 'Akcja promocyjna została odrzucona.'
            vals = (promotion.client_id.name, url)                
            body = decode("Akcja promocyjna klienta %s została anulowana.<br/><a href='%s'>Link do akcji promocyjnej</a>") % vals
            self.pool.get('product.product').send_mail(cr, uid, body, subject, mail_to)
            
    def calculate_promotions(self, cr, uid, ids, context=None):
        stage_id = self.pool.get('cd.promotions.stage').search(cr, uid, [('sequence','=', 80)])[0]
        vals = {}
        vals['stage_id'] = stage_id
        self.write(cr, uid, ids, vals)
        
        
    def rejected_promotions(self, cr, uid, ids, context=None):
        stage_id = self.pool.get('cd.promotions.stage').search(cr, uid, [('sequence','=', 90)])[0]
        vals = {}
        vals['stage_id'] = stage_id
        self.write(cr, uid, ids, vals)
        mail_to = ''
        promotion = self.browse(cr, uid, ids[0])
        if promotion.create_uid.email and promotion.create_uid.email != '':
            mail_to += promotion.create_uid.email+', '
        if mail_to != '':
            cd_config_obj = self.pool.get('cd.config.settings')
            cd_config_id = cd_config_obj.search(cr, uid, [])
            cd_crm = cd_config_obj.browse(cr, uid, cd_config_id[-1]).cd_crm
            url = ("http://%s/?db=%s#id=%s&view_type=form&model=cd.promotions")%(cd_crm, cr.dbname, promotion.id)
            subject = 'Akcja promocyjna została odrzucona.'
            vals = (promotion.client_id.name, url)                
            body = decode("Akcja promocyjna klienta %s została odrzucona.<br/><a href='%s'>Link do akcji promocyjnej</a>") % vals
            self.pool.get('product.product').send_mail(cr, uid, body, subject, mail_to)
        
    def user_in_group(self, cr, uid, group_name, context=None):
        users_obj = self.pool.get('res.users')
        group_id = self.pool.get('res.groups').search(cr,uid,[('name','=',group_name)])
        user_ids = users_obj.search(cr,uid,[('groups_id','in',group_id)])
        if uid not in user_ids:
            raise osv.except_osv(decode('Ostrzeżenie'), decode('Operację może wykonać tylko %s')%group_name)
        
    def open_add_products(self, cr, uid, ids, context=None):
        promotion = self.browse(cr, uid, ids)[0]
        listing_obj = self.pool.get("cd.listing")
        listing_ids = listing_obj.search(cr, uid, [('client_id','=',promotion.client_id.id),('status_l','=','0')])
        listings = listing_obj.read(cr, uid, listing_ids,['product_id'])
        
        product_list = []
        for listing in listings:
            product_list.append(listing['product_id'][0])
            
        context['product_list'] = product_list
        return {
            'type': 'ir.actions.act_window',
            'name': 'Dodaj wiele produktów', 
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self.pool.get('cd.product.rel.add.wizard')._name,
            'target': 'new',
            'context': context,
        }
        
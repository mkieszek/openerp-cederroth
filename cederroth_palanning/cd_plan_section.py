# -*- coding: utf-8 -*-
"""
@author: mbereda
"""

from openerp.osv import fields, osv
from openerp.osv.orm import Model
from openerp.addons.mail.mail_message import decode
from datetime import timedelta
import calendar
import datetime
import pdb

AVAILABLE_MONTHS = [('01',"Styczeń"), ('02',"Luty"), ('03',"Marzec"), ('04',"Kwiecień"), ('05',"Maj"), ('06',"Czerwiec"), 
          ('07',"Lipiec"), ('08',"Sierpień"), ('09',"Wrzesień"), ('10',"Październik"), ('11',"Listopad"), ('12',"Grudzień")]

AVAILABLE_STATE = [('01',"W trakcie"), ('02',"Wykonany"), ('03',"Zaakceptowany")]

class cd_plan_section(osv.Model):
    _name = "cd.plan.section"
    _inherit = 'mail.thread'
    _rec_name = "plan_name"
    _description = "Plan departament"
    
    def _get_value_clients(self, cr, uid, ids, name, arg, context=None):
        val={}
        for plans in self.browse(cr, uid, ids):
            amount = 0.00
            for plan_client in plans.plan_client_ids:
                amount += plan_client.get_value
            val[plans.id] = amount
        return val
    
    def _get_client_list(self, cr, uid, ids, name, arg, context=None):
        val={}
        res_partner_obj = self.pool.get('res.partner')
        for plan in self.browse(cr, uid, ids):
            plan_client_list = []
            for plan_client in plan.plan_client_ids:
                plan_client_list.append(plan_client.client_id.id)
            partner_ids = res_partner_obj.search(cr, uid, [('section_id','=',plan.section_id.id),('is_company','=',True),('parent_id','=',False),('id','not in', plan_client_list)])
            val[plan.id] = [[6, False, partner_ids]]
        return val
    
    def _get_blocked(self, cr, uid, ids, name, arg, context=None):
        val={}
        today = datetime.date.today()
        for plan in self.browse(cr, uid, ids):
            #sale_start = datetime.datetime.strptime(plan.start_plan,"%Y-%m-%d").date()
            sale_stop = datetime.datetime.strptime(plan.stop_plan,"%Y-%m-%d").date()
            if sale_stop >= today:
                val[plan.id] = False
            else:
                val[plan.id] = True
        return val
    
    def _get_blocked_uid(self, cr, uid, ids, name, arg, context=None):
        val={}
        groups_obj = self.pool.get('res.groups')
        for plan in self.browse(cr, uid, ids):
            if not groups_obj.search(cr, uid, [('users','=',uid),('name','=','Sales Director')]):
                val[plan.id] = True
            else:
                val[plan.id] = False
        return val
    
    def _get_date_plan(self, cr, uid, ids, name, arg, context=None):
        val={}
        term_obj = self.pool.get('cd.plan.term')
        for plan in self.browse(cr, uid, ids):
            term_ids = term_obj.search(cr, uid, [('month','=',plan.month),('year','=',plan.year)])
            term = term_obj.browse(cr, uid, term_ids[0])
            val[plan.id] = {'start_plan': term.sale_start, 'stop_plan': term.sale_stop}
        return val
    
    def _get_plan_mark(self, cr, uid, ids, name, arg, context=None):
        val={}
        mark_obj = self.pool.get('cd.plan.mark')
        for plan in self.browse(cr, uid, ids):
            mark_ids = mark_obj.search(cr, uid, [('year','=',plan.year),('month','=',plan.month)])
            val[plan.id] = mark_ids
        return val
    
    def _get_gp(self, cr, uid, ids, name, arg, context=None):
        val={}
        plan_client_obj = self.pool.get('cd.plan.client')
        for splan in self.browse(cr, uid, ids):                            
            nsh_total = 0.0
            gpp_total = 0.0
            nsv_total = 0.0
            nsh_promo = 0.0
            gross_sale = 0.0
            disc_front_total = 0.0
            other_cogs = 0.0
            product_cogs = 0.0
            discount_pormo = 0.0
            cm_total = 0.0
            cmp_total = 0.0
            coop_value = 0.0
            nsh_p_nsh_t = 0.0
            trade_promo_listing = 0.0
            other_marketing = 0.0
            
            for planc in splan.plan_client_ids:
                data = plan_client_obj._get_gp(cr, uid, [planc.id], ['nsh_total', 'nsh_promo','gross_sale','disc_front_total','other_cogs','product_cogs','discount_pormo','cm_total','coop', 'trade_promo_listing', 'other_marketing'], '')
                
                nsv_total += data[planc.id]['nsv_total']
                gross_sale += data[planc.id]['gross_sale']
                disc_front_total += data[planc.id]['disc_front_total']
                other_cogs += data[planc.id]['other_cogs']
                product_cogs += data[planc.id]['product_cogs']
                discount_pormo += data[planc.id]['discount_pormo']
                cm_total += data[planc.id]['cm_total']
                coop_value += data[planc.id]['coop']
                trade_promo_listing += data[planc.id]['trade_promo_listing']
                other_marketing += data[planc.id]['other_marketing']
                nsh_promo += data[planc.id]['nsh_promo']
                
            nsh_total = gross_sale - disc_front_total - discount_pormo
            
            if nsv_total != 0 and nsv_total-cm_total != 0:    
                cmp_total = (nsv_total - cm_total)/nsv_total*100
                
            if nsv_total != 0 and nsv_total-product_cogs-other_cogs != 0:
                gpp_total = (nsv_total - product_cogs - other_cogs)/nsv_total*100
            
            if nsh_total > 0:
                nsh_p_nsh_t = (nsh_promo/nsh_total)*100  
            
            val[splan.id] = {
                            'gpp_total': gpp_total,
                            'gp_total': nsv_total-product_cogs-other_cogs,
                            'nsh_total': nsh_total,
                            'nsh_promo': nsh_promo,
                            'nsv_total': nsv_total,
                            
                            'gross_sale': gross_sale,
                            'disc_front_total': disc_front_total,
                            'other_cogs': other_cogs,
                            'product_cogs': product_cogs,
                            'discount_pormo': discount_pormo,
                            'cm_total': cm_total,
                            'cmp_total': cmp_total,
                            'coop': coop_value,
                            'nsh_p_nsh_t': nsh_p_nsh_t,
                            'trade_promo_listing': trade_promo_listing,
                            'other_marketing': other_marketing,
                            }
        return val
    
    def _get_budget_mark(self, cr, uid, ids, name, arg, context=None):
        val={}
        for plan in self.browse(cr, uid, ids):
            bud_cm = 0.0
            bud_nsh = 0.0
            for brand in plan.plan_section_brand_ids:
                bud_cm += brand.contrib
                bud_nsh += brand.forecast
                
            val[plan.id] = {
                            'budget_contrib': bud_cm,
                            'budget_nsh': bud_nsh,
                            }
        return val
    
    _columns = {
        'plan_name': fields.char("Nazwa estymacji", size=255, required=False),
        'state_id': fields.selection(AVAILABLE_STATE, 'Status'),
        'year': fields.integer("Rok", required=True, group_operator='min'),
        'month': fields.selection(AVAILABLE_MONTHS, 'Miesiąc', required=True),
        'start_date': fields.date('Data rozpoczęcia'),
        'stop_date': fields.date('Data zakończenia'),
        'section_id': fields.many2one('crm.case.section', 'Zespół sprzedaży', required=True),
        #'budget_contrib': fields.float('Budżet Contrib.'),
        #'budget_nsh': fields.float('Budżet NSH'),
        'budget_contrib': fields.function(_get_budget_mark, type='float', string='Budżet Contrib.', store=False, readonly=True, multi="budget_mark"),
        'budget_nsh': fields.function(_get_budget_mark, type='float', string='Budżet NSH', store=False, readonly=True, multi="budget_mark"),
        'plan_value': fields.float('Forecast', required=False, track_visibility='onchange'),
        'get_value': fields.function(_get_value_clients, type="float", string='Zrealizowana wartość', readonly=True, store=False),
        'plan_client_ids': fields.one2many('cd.plan.client', 'plan_section_id', 'Plan Klient'),
        'client_id': fields.many2one('res.partner', "Wybierz klienta"),
        'client_list_ids' : fields.function(_get_client_list, relation='res.partner', type='many2many', string='Klienci', store=False),
        'blocked' : fields.function(_get_blocked, type='boolean', string='Zablokowane', store=False),
        'blocked_uid' : fields.function(_get_blocked_uid, type='boolean', string='Zablokowane', store=False),
        'plan_section_brand_ids': fields.one2many('cd.plan.section.brand', 'plan_section_id', 'Plan Marka', readonly=True),
        'plan_mark_ids': fields.function(_get_plan_mark, type='one2many', relation='cd.plan.mark', store=False, readonly=True),
        
        'start_plan': fields.function(_get_date_plan, type='date', string='Rozpoczęcie planowania', store=False, multi='plan_date'),
        'stop_plan': fields.function(_get_date_plan, type='date', string='Zakończenie planowania', store=False, multi='plan_date'),
        
        'gpp_total': fields.function(_get_gp, type='float', string='Estym GP %', store=False, readonly=True, multi='summation'),
        'gpp_promo': fields.function(_get_gp, type='float', string='Estym GP % promo', store=False, readonly=True, multi='summation'),
        'gp_total': fields.function(_get_gp, type='float', string='Estym GP', store=False, readonly=True, multi='summation'),
        'gp_promo': fields.function(_get_gp, type='float', string='Estym GP promo', store=False, readonly=True, multi='summation'),
        'nsh_total': fields.function(_get_gp, type='float', string='Estym NSH total', store=False, readonly=True, multi='summation'),
        'nsh_promo': fields.function(_get_gp, type='float', string='Estym NSH promo', store=False, readonly=True, multi='summation'),
        'cost_total': fields.function(_get_gp, type='float', string='Koszt total', store=False, readonly=True, multi='summation'),
        'cost_promo': fields.function(_get_gp, type='float', string='Koszt promo', store=False, readonly=True, multi='summation'),
        'percentage': fields.function(_get_gp, type='float', string='Estym pormo / Estym total (%)', store=False, readonly=True, multi='summation'),
        'nsv_total': fields.function(_get_gp, type='float', string='Estym NSV total', store=False, readonly=True, multi='summation'),
        #'nsv_promo': fields.function(_get_gp, type='float', string='NSV promo', store=False, readonly=True, multi='summation'),
        
        #nowe
        'gross_sale': fields.function(_get_gp, type='float', string='Estym Gross Sale', store=False, readonly=True, multi='summation'),
        'disc_front_total': fields.function(_get_gp, type='float', string='Estym Rabat Front', store=False, readonly=True, multi='summation'),
        'trade_promo': fields.function(_get_gp, type='float', string='Estym Trade promo', store=False, readonly=True, multi='summation'),
        'other_cogs': fields.function(_get_gp, type='float', string='Estym Other COGS', store=False, readonly=True, multi='summation'),
        'other_listings': fields.function(_get_gp, type='float', string='Estym Other (listing)', store=False, readonly=True, multi='summation'),
        'other_marketing': fields.function(_get_gp, type='float', string='Estym Other Marketing', store=False, readonly=True, multi='summation'),
        'product_cogs': fields.function(_get_gp, type='float', string='Estym COGS', store=False, readonly=True, multi='summation'),
        'discount_pormo': fields.function(_get_gp, type='float', string='Estym Rabaty Promo', store=False, readonly=True, multi='summation'),
        'cm_total': fields.function(_get_gp, type='float', string='Estym Contrib.', store=False, readonly=True, multi='summation'),
        'cmp_total': fields.function(_get_gp, type='float', string='Estym Contrib. %', store=False, readonly=True, multi='summation'),
        'coop': fields.function(_get_gp, type='float', string='Estym COOP', store=False, readonly=True, multi='summation'),
        'nsh_p_nsh_t': fields.function(_get_gp, type='float', string='Estym NSH Promo / NSH Total', store=False, readonly=True, multi='summation'),
        'trade_promo_listing': fields.function(_get_gp, type='float', string='Estym Trade promo + Listingi', store=False, readonly=True, multi='summation'),
        'other_marketing': fields.function(_get_gp, type='float', string='Estym Other Marketing', store=False, readonly=True, multi='summation'),
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
        reads = self.read(cr, uid, ids, ['section_id', 'month', 'year'], context)
        for record in reads:
            client = record['section_id'][1]
            month = record['month']
            year = record['year']
            res.append((record['id'], client + ' ' + str(year) + '-' + str(month)))
        return res
    
    def create(self, cr, uid, data, context=None):
        if self.search(cr, uid, [('year','=',data['year']),('month','=',data['month']),('section_id','=',data['section_id'])]):
            raise osv.except_osv(decode('Ostrzeżenie'), decode('Plan Departament na wybrany miesiąc już jest w systemie'))
        
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
            raise osv.except_osv(decode('Ostrzeżenie'), decode('Plan Departamentu nie może zostać utworzony w tym terminie'))
        """
        if not 'message_follower_ids' in data:
            data['message_follower_ids'] = False
        
        plan_id = super(cd_plan_section, self).create(cr, uid, data, context=context)
        plan_section = self.browse(cr, uid, plan_id)
        partner_obj = self.pool.get('res.partner')
        partner_ids = partner_obj.search(cr, uid, [('section_id','=',plan_section.section_id.id),('parent_id','=',False),('is_company','=',True)])
        
        for partner in partner_obj.browse(cr, uid, partner_ids):
            vals_client = {}
            vals_client = {
                           'client_id': partner.id,
                           'month': plan_section.month,
                           'year': plan_section.year,
                           'plan_value': 0.0,
                           'plan_section_id': plan_section.id,
                           }
            self.pool.get('cd.plan.client').create(cr, uid, vals_client, context=None)
        if plan_section.section_id.user_id.partner_id:
            self.message_subscribe(cr, uid, [plan_id], [plan_section.section_id.user_id.partner_id.id], context=context)
            
        #Usunięcie dodawania Administratora do obserwarotów
        self.message_unsubscribe(cr, uid, [plan_id], [3], context=None)
            
        #print data['month'] + " " +str(data['year'])
        return plan_id
    
    def write(self, cr, uid, ids, data, context=None):
        for id in ids:
            plan_sec = self.browse(cr, uid, id)
            
            if 'month' in data or 'year' in data:
                month = ''
                year = 0
                if 'month' in data:
                    month = data['month']
                else:
                    month = plan_sec.month
                if 'year' in data:
                    year = data['year']
                else:
                    year = plan_sec.year
                if self.search(cr, uid, [('year','=',year),('month','=',month),('section_id','=',plan_sec.section_id.id)]):
                    raise osv.except_osv(decode('Ostrzeżenie'), decode('Plan Departament na wybrany miesiąc już jest w systemie'))

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
                    raise osv.except_osv(decode('Ostrzeżenie'), decode('Plan Departamentu nie może zostać utworzony w tym terminie'))
                """
        plan_id = super(cd_plan_section, self).write(cr, uid, ids, data, context=context)
        
        return plan_id
    
    def add_months(self, sourcedate,months):
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month / 12 
        month = month % 12 + 1
        day = min(sourcedate.day,calendar.monthrange(year,month)[1])
        return datetime.date(year,month,day)
    
    def add_client(self, cr, uid, ids, context=None):
        w = self.browse(cr, uid, ids[0])
        data = {}
        data['client_id'] = w.client_id.id
        for plan_client in w.plan_client_ids:
            if plan_client.client_id.id == w.client_id.id:
                raise osv.except_osv(decode('Ostrzeżenie'), decode('Ten klient został już dodany.'))
        data['plan_value'] = 0.0
        data['year'] = w.year
        data['month'] = w.month
        data['plan_section_id'] = w.id
        self.pool.get('cd.plan.client').create(cr, uid, data, context=None)
        vals = {}
        vals['client_id'] = False
        self.write(cr, uid, ids, vals, context=None)
        return {'value': vals}
    
    def onchange_client_list(self, cr, uid, ids, section_id, context=None):
        val = {}
        partner_ids = self.pool.get('res.partner').search(cr, uid, [('section_id','=',section_id),('is_company','=',True),('parent_id','=',False)])
        val['client_list_ids'] = [[6, False, partner_ids]]
        if partner_ids:
            return {'value': val}
        else:
            return {'value':val, 'warning':{'title':'Ostrzeżenie','message':'Wybrany zespół nie posiada klientów.'}}
        
    def create_department(self, cr, uid, context=None):
        mark_month_obj = self.pool.get('cd.plan.mark.month')
        t_sec_obj = self.pool.get('crm.case.section')
        t_sec_ids = t_sec_obj.search(cr, uid, [])
        for t_sec_id in t_sec_ids:
            section_date = self.add_months(datetime.date.today(),1)
            next_year = self.add_months(section_date,12)
            while (section_date != next_year):
                month = ''
                month = str(section_date.month).zfill(2)
                if not self.search(cr, uid, [('month','=',month),('section_id','=',t_sec_id)]):
                    vals = {}
                    vals = {
                            'year': section_date.year,
                            'month': month,
                            'section_id': t_sec_id,
                            'plan_value': 0.0,
                            }
                    self.create(cr, uid, vals, context=None)

                if not mark_month_obj.search(cr, uid, [('month','=',month),('year','=',section_date.year)]):
                    vals = {}
                    vals = {
                            'month': month,
                            'year': section_date.year
                            }
                    mark_month_obj.create(cr, uid, vals, context=None)
        
                section_date = self.add_months(section_date, 1)        
        
        
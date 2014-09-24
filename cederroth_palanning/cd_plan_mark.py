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

AVAILABLE_PRIORITY = [('01',"1"), ('02',"2"), ('03',"3"), ('04',"4"), ('05',"5"), ('06',"Nowość")]

class cd_plan_mark(osv.Model):
    _name = "cd.plan.mark"
    _inherit = 'mail.thread'
    _rec_name = "plan_name"
    _description = "Plan Marketingowy"
    
    def _get_blocked(self, cr, uid, ids, name, arg, context=None):
        val={}
        today = datetime.date.today()
        for plan in self.browse(cr, uid, ids):
            #start_plan = datetime.datetime.strptime(plan.start_plan,"%Y-%m-%d").date()
            stop_plan = datetime.datetime.strptime(plan.stop_plan,"%Y-%m-%d").date()
            if stop_plan >= today:
                val[plan.id] = False
            else:
                val[plan.id] = True
        return val
    
    def _get_blocked_prod(self, cr, uid, ids, name, arg, context=None):
        val={}
        for plan in self.browse(cr, uid, ids):
            val[plan.id] = True
        return val
    
    _columns = {
        'plan_name': fields.char("Nazwa Planu", size=255, required=False),
        'year': fields.integer("Rok", required=True, group_operator='min', readonly=True),
        'month': fields.selection(AVAILABLE_MONTHS, 'Miesiąc', required=True, readonly=True),
        'priority': fields.selection(AVAILABLE_PRIORITY, 'Priorytet', required=True),
        'product_id': fields.many2one('product.product', "Produkt", required=False),
        'start_date': fields.date('Data rozpoczęcia'),
        'stop_date': fields.date('Data zakończenia'),
        'create_uid': fields.many2one('res.users', 'Twórca'),
        'blocked' : fields.function(_get_blocked, type='boolean', string='Zablokowane', store=False),
        'blocked_prod' : fields.function(_get_blocked_prod, type='boolean', string='Blokowany produkt', store=False),
        'plan_mark_month_id': fields.many2one('cd.plan.mark.month', 'Plan Makretingowy Miesiąc', required=True, ondelete='cascade'),
        #'start_plan': fields.related('plan_mark_month_id', 'start_plan', type='date', string='Rozpoczęcie planowania', readonly=True),
        'stop_plan': fields.related('plan_mark_month_id', 'stop_plan', type='date', string='Zakończenie planowania', readonly=True),
        'categ_id' : fields.many2one('product.category', "Linia produktowa")
    }
    
    def name_get(self, cr, uid, ids, context=None):
        """Overrides orm name_get method"""
        if not isinstance(ids, list) :
            ids = [ids]
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['categ_id', 'priority'], context)
        for record in reads:
            if record['categ_id'] != False:
                product = record['categ_id'][1]
            else:
                product='' 
            priority = record['priority']
            res.append((record['id'], product + ' - ' + priority))
        return res
    
    def create(self, cr, uid, data, context=None):
        if 'month' not in data and 'year' not in data:
            plan_month = self.pool.get('cd.plan.mark.month').browse(cr, uid, data['plan_mark_month_id'])
            data['month'] = plan_month.month
            data['year'] = plan_month.year
        #if self.search(cr, uid, [('year','=',data['year']),('month','=',data['month']),('product_id','=',data['product_id'])]):
        #    raise osv.except_osv(decode('Ostrzeżenie'), decode('Plan Marketing z tym produktem na wybrany miesiąc już jest w systemie'))
        start_date = datetime.date(data['year'], int(data['month']), 1)
        stop_date = (self.add_months(start_date,1)) - timedelta(days=1)
        data['start_date'] = start_date
        data['stop_date'] = stop_date
                    
        plan_id = super(cd_plan_mark, self).create(cr, uid, data, context=context)
        
        #Usunięcie dodawania Administratora do obserwarotów
        self.message_unsubscribe(cr, uid, [plan_id], [3], context=None)
        
        return plan_id
    
    def write(self, cr, uid, ids, data, context=None):
        if 'plan_mark_month_id' in data:
            plan_month = self.pool.get('cd.plan.mark.month').browse(cr, uid, data['plan_mark_month_id'])
            data['month'] = plan_month.month
            data['year'] = plan_month.year
        for id in ids:
            plan_mark = self.browse(cr, uid, id)
            
            if 'month' in data or 'year' in data:
                month = ''
                year = 0
                if 'month' in data:
                    month = data['month']
                else:
                    month = plan_mark.month
                if 'year' in data:
                    year = data['year']
                else:
                    year = plan_mark.year
                    
                start_date = datetime.date(year, int(month), 1)
                stop_date = (self.add_months(start_date,1)) - timedelta(days=1)
                data['start_date'] = start_date
                data['stop_date'] = stop_date
                
                cd_config_obj = self.pool.get('cd.config.settings')
                cd_config_id = cd_config_obj.search(cr, uid, [])
                cd_plan_prom = cd_config_obj.browse(cr, uid, cd_config_id[-1]).plan_plan_prom
                
                next_date = self.add_months(datetime.date.today(),cd_plan_prom)
                if next_date >= start_date:
                    raise osv.except_osv(decode('Ostrzeżenie'), decode('Plan Marketing nie może zostać utworzony w tym terminie'))
            
        plan_id = super(cd_plan_mark, self).write(cr, uid, ids, data, context=context)
        plan = self.browse(cr, uid, ids[0])
        if len(self.search(cr, uid, [('year','=',plan.year),('month','=',plan.month),('product_id','=',plan.product_id.id)])) > 1:
            raise osv.except_osv(decode('Ostrzeżenie'), decode('Plan Marketing na wybrany miesiąc już jest w systemie'))
    
        return plan_id
    
    def add_months(self, sourcedate,months):
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month / 12 
        month = month % 12 + 1
        day = min(sourcedate.day,calendar.monthrange(year,month)[1])
        return datetime.date(year,month,day)
     
    def notifications_deadline_plan(self, cr, uid, context=None):
        today = datetime.date.today()
        next_date = today+timedelta(days=5)
        
        mark_ids = self.search(cr, uid, [('stop_plan','>=',today),('stop_plan','<=',next_date)])
        
        for plan_mark in self.browse(cr, uid, mark_ids):
            days = ''
            if plan_mark.stop_plan == (today+timedelta(days=5)).strftime('%Y-%m-%d'):
                days = '5 dni'
            elif plan_mark.stop_plan == (today+timedelta(days=3)).strftime('%Y-%m-%d'):
                days = '3 dni'
            elif plan_mark.stop_plan == (today+timedelta(days=1)).strftime('%Y-%m-%d'):
                days = '1 dzień'
                
            if days != '':
                mail_to = plan_mark.create_uid.email
                if mail_to != False or mail_to != '':
                    cd_config_obj = self.pool.get('cd.config.settings')
                    cd_config_id = cd_config_obj.search(cr, uid, [])
                    cd_crm = cd_config_obj.browse(cr, uid, cd_config_id[-1]).cd_crm
                    url = ("http://%s/?db=%s#id=%s&view_type=form&model=cd.plan.mark")%(cd_crm, cr.dbname, plan_mark.id)
                    vals_email = (str(today.month), decode(days), str(url))
                    subject = 'Koniec planowania na miesiąc: %s' % str(today.month)
                    body = decode("Planowanie na miesiąc: %s kończy się za %s.<br/><a href='%s'>Link do plan marketing</a>") % vals_email
                    self.pool.get('product.product').send_mail(cr, uid, body, subject, mail_to)
                    
    def notifications_plan_marketing(self, cr, uid, context=None):
        mark_month_obj = self.pool.get('cd.plan.mark.month')
        yesterday = datetime.date.today()-timedelta(days=1)
        
        plan_month_ids = mark_month_obj.search(cr, uid, [('stop_plan','=',yesterday)])
        
        if plan_month_ids:
            users_obj = self.pool.get('res.users')
            group_id = self.pool.get('res.groups').search(cr,uid,['|',('name','=','KAM'),'|',('name','=','Department Director'),('name','=','Sales Director')])
            user_ids = users_obj.search(cr,uid,[('groups_id','in',group_id),('id','!=',1)])
            users = users_obj.browse(cr, uid, user_ids)
            mail_to = ''
            for user in users:
                if user.email and user.email != '':
                    mail_to += user.email+', '
            if mail_to != '':
                cd_config_obj = self.pool.get('cd.config.settings')
                cd_config_id = cd_config_obj.search(cr, uid, [])
                cd_crm = cd_config_obj.browse(cr, uid, cd_config_id[-1]).cd_crm

                url = ("http://%s/?db=%s#id=%s&view_type=form&model=cd.plan.mark.month")%(cd_crm, cr.dbname, str(plan_month_ids[0]))
                vals = (str(yesterday.month), str(yesterday.year), url)
                subject = 'Zakończenie planowania Marketingu'
                body = decode("Dział Marketingu zakończył planowanie na %s-%s<br/><a href='%s'>Link do planu Marketingowego</a>") % vals
                self.pool.get('product.product').send_mail(cr, uid, body, subject, mail_to)
        
    def onchange_mark_month(self, cr, uid, ids, mark_month_id, context=None):
        val = {}
        plan = self.pool.get('cd.plan.mark.month').browse(cr, uid, mark_month_id)
        val['year'] = plan.year
        val['month'] = plan.month
        
        return {'value': val}        

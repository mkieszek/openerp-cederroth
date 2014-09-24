# -*- coding: utf-8 -*-
'''
@author: mbereda
'''

from openerp.osv import fields, osv
from openerp.osv.orm import Model
from openerp import tools

import pdb

class cd_report_plan_client(osv.Model):
    _name = "cd.report.plan.client"    
    
    def _get_other_marketing(self, cr, uid, ids, name, arg, context=None):
        val={}
        
        cd_report_other_mark_month_obj = self.pool.get('cd.report.other.mark.month')
        cd_report_coop_obj = self.pool.get('cd.report.coop')
        cd_report_trade_promo_obj = self.pool.get('cd.report.trade.promo')
        cd_report_other_cogs_obj = self.pool.get('cd.report.other.cogs')
        for plan in self.browse(cr, uid, ids):
            other_marketing = 0.0
            coop = 0.0
            trade_promo = 0.0
            other_cogs = 0.0
            
            search_vals = [('year','=',plan.plan_client_id.year),
                           ('month','=', plan.plan_client_id.month),
                           ('client_id','=', plan.client_id.id)]
            
            other_marketing_ids = cd_report_other_mark_month_obj.search(cr, uid, search_vals)
            coop_ids = cd_report_coop_obj.search(cr, uid, search_vals)
            trade_promo_ids = cd_report_trade_promo_obj.search(cr, uid, search_vals)
            other_cogs_ids = cd_report_other_cogs_obj.search(cr, uid, search_vals)
            
            for item in cd_report_other_mark_month_obj.browse(cr, uid, other_marketing_ids):
                other_marketing += item.value
                
            for item in cd_report_coop_obj.browse(cr, uid, coop_ids):
                coop += item.value
                
            for item in cd_report_trade_promo_obj.browse(cr, uid, trade_promo_ids):
                trade_promo += item.value
            
            for item in cd_report_other_cogs_obj.browse(cr, uid, other_cogs_ids):
                other_cogs += item.value
                
            val[plan.id] = {
                            'other_marketing': other_marketing,
                            'coop': coop,
                            'trade_promo': trade_promo,
                            'other_cogs': other_cogs
                            }
        return val
    
    _columns = {
        'plan_client_id': fields.many2one('cd.plan.client', 'Plan Klient'),
        'year': fields.integer('Year', group_operator="max"),
        'month' : fields.char('Month'),
        'section_id' : fields.many2one('crm.case.section', 'Kanał'),
        'client_id' : fields.many2one('res.partner','Klient'),
        'create_date': fields.date('Data akceptacji'),
        
        #'plan_value': fields.float('Forecast'),
        #'get_value': fields.float('Zrealizowana wartość'),
        'nsv_total': fields.float('NSV Total'),
        #'nsv_promo': fields.float('NSV promo'),
        'nsh_total': fields.float('NSH Total'),
        #'nsh_promo': fields.float('NSH promo'),
        #'cost_total': fields.float('Koszt total'),
        #'cost_promo': fields.float('Koszt promo'),
        'gpp_total': fields.float('GP % Total', group_operator="avg"),
        #'gpp_promo': fields.float('GP % promo', group_operator="avg"),
        #'percentage': fields.float('Estym promo / Estym total (%)', group_operator="avg"),
        #'stop_plan': fields.date('Zakończenie planowania'),
        #'other_marketing': fields.function(_get_other_marketing, type='float', string='Other Marketing', store=False, readonly=True, multi='summation', group_operator="sum"),
        #'coop': fields.function(_get_other_marketing, type='float', string='COOP', store=False, readonly=True, multi='summation'),
        #'trade_promo': fields.function(_get_other_marketing, type='float', string='Trade Promo', store=False, readonly=True, multi='summation'),
        #'other_cogs': fields.function(_get_other_marketing, type='float', string='Other COGS', store=False, readonly=True, multi='summation'),
        
        'gp_total': fields.float('Estym GP'),
        'gpp_total': fields.float('Estym_GP (%)'),
        'gross_sale': fields.float('Estym Gross Sale'),
        'disc_front_total': fields.float('Estym Rabaty Front'),
        'other_cogs': fields.float('Estym Other COGS'),
        'product_cogs': fields.float('Estym COGS'),
        'discount_pormo': fields.float('Estym Rabaty Promo'),
        'cm_total': fields.float('Estym Contrib.'),
        'cmp_total': fields.float('Estym Contrib. %'),
        'coop': fields.float('Estym COOP'),
        'nsh_p_nsh_t': fields.float('Estym NSH Promo / NSH Total'),
        'trade_promo_listing': fields.float('Estym Trade Promo + Listingi'),      
        'other_marketing' : fields.float('Other marketing')  
    }
    
    def open_plan_client(self, cr, uid, ids, context=None):
        plan_client_id = self.browse(cr, uid, ids[0]).plan_client_id.id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Plan Klient', 
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'cd.plan.client',
            'res_id': plan_client_id,
            'target': 'self',
        }

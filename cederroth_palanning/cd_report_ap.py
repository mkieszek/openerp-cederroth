# -*- coding: utf-8 -*-
"""
@author: mbereda
"""

from openerp.osv import fields, osv
from openerp.osv.orm import Model
from openerp import tools

import datetime
import pdb

class cd_report_ap(osv.Model):
    _name = "cd.report.ap"
    _auto = False
    """
    def _get_fc_mark(self, cr, uid, ids, name, arg, context=None):
        val={}
        cbrand_obj = self.pool.get('cd.plan.client.brand')
        for rap in self.browse(cr, uid, ids):
            ap_client_id = rap.promotions_id.client_id
            ap_brand = rap.promotions_id.product_category
            ap_date = datetime.datetime.strptime(rap.promotions_id.discount_from,"%Y-%m-%d").date()
            cbrand_ids = cbrand_obj.search(cr, uid, [('plan_client_id.client_id.id','=',ap_client_id.id),('product_category_id','=',ap_brand.id),('plan_client_id.month','=',str(ap_date.month).zfill(2)),('plan_client_id.year','=',ap_date.year)])
            if cbrand_ids:
                val[rap.id] = cbrand_obj.browse(cr, uid, cbrand_ids[0]).forecast
            else:
                val[rap.id] = 0.0
        return val

    def _get_gratis(self, cr, uid, ids, name, arg, context=None):
        val={}
        promotions_obj = self.pool.get('cd.promotions')
        for promo in promotions_obj.browse(cr, uid, ids):
            amount = 0.0
            for grat in promo.gratis_ids:
                amount += grat.value_cogs
            
            val[promo.id] = amount
        return val
    
    def _get_other_mark(self, cr, uid, ids, name, arg, context=None):
        val={}
        promotions_obj = self.pool.get('cd.promotions')
        for promo in promotions_obj.browse(cr, uid, ids):
            amount = 0.0
            for cost in promo.cost_promotions_ids:
                if cost.cost_type == '01':
                    amount += cost.amount
            val[promo.id] = amount
        return val
    
    def _get_coop_tp(self, cr, uid, ids, name, arg, context=None):
        val={}
        promotions_obj = self.pool.get('cd.promotions')
        for promo in promotions_obj.browse(cr, uid, ids):
            amount = 0.0
            for cost in promo.cost_promotions_ids:
                if cost.cost_type == '02' or cost.cost_type == '03':
                    amount += cost.amount
            val[promo.id] = amount
        return val
    
    def _get_total_cost(self, cr, uid, ids, name, arg, context=None):
        val={}
        for rap in self.browse(cr, uid, ids):            
            val[rap.id] = rap.gratis+rap.other_mark+rap.coop_tp+rap.product_cogs#+rap.contract_cost
        return val

    def _get_nsh_promo_plan(self, cr, uid, ids, name, arg, context=None):
        val={}
        promotions_obj = self.pool.get('cd.promotions')
        plan_client_obj = self.pool.get('cd.plan.client')
        for promo in promotions_obj.browse(cr, uid, ids):
            month = datetime.datetime.strptime(promo.discount_from,"%Y-%m-%d").month
            year = datetime.datetime.strptime(promo.discount_from,"%Y-%m-%d").year
            plan_client_ids = plan_client_obj.search(cr, uid, [('month','=',str(month).zfill(2)),('year','=',year),('client_id','=',promo.client_id.id)])
            if plan_client_ids:
                plan_client = plan_client_obj.browse(cr, uid, plan_client_ids[0])
                if promo.value_prom != 0 and plan_client.nsh_total:
                    val[promo.id] = (promo.nsh/plan_client.nsh_total)*100
                else:
                    val[promo.id] = 0.0
            else:
                val[promo.id] = 0.0
        return val
    
    def _get_value(self, cr, uid, ids, name, arg, context=None):
        val={}
        promotions_obj = self.pool.get('cd.promotions')
        for promo in promotions_obj.browse(cr, uid, ids):
            coop_tp = 0.0
            other_mark = 0.0
            gratis = 0.0
            for cost in promo.cost_promotions_ids:
                if cost.cost_type == '01':
                    other_mark += cost.amount
                if cost.cost_type == '02' or cost.cost_type == '03':
                    coop_tp += cost.amount
            
            for grat in promo.gratis_ids:
                gratis += grat.value_cogs
                    
            val[promo.id] = {
                             'coop_tp': coop_tp,
                             'gratis': gratis,
                             'other_mark': other_mark,
                             }

        return val
    """
    _columns = {
        'promotions_id': fields.many2one('cd.promotions', 'Akcja Promocyjna'),
        'client_id': fields.many2one('res.partner', 'Klient'),
        'product_category': fields.many2one('product.category', 'Marka'),
        'month': fields.char('Miesiąc'),
        'year': fields.char('Rok'),
        'start_date': fields.date('Data startu'),
        'stop_date': fields.date('Data końca'),
        'discount_from': fields.date('Rabat od'),
        'stage_id': fields.many2one('cd.promotions.stage', 'Status'),
        
        #'promo_discount_value': fields.float('Wartość rabatów promo'), wyłączone z powodu zmian bilansu akcji, pole było używane w plan client linia 140
        #'sale_nsh_value': fields.float('Wartość sprzedaży NSH'),
        #'product_cogs': fields.float('COGS produktów'),
        #'contract_cost': fields.float('Koszty kontraktowe'), wyłączone z powodu zmian bilansu akcji
        #'gpp': fields.float('GP %', group_operator="avg"),
        #'gp': fields.float('GP'),
        
        
        #'fc_mark': fields.function(_get_fc_mark, type="float", string='FC Marka', readonly=True, store=False),
        #'gratis': fields.function(_get_gratis, type="float", string='Gratis', readonly=True, store=False),
        #'other_mark': fields.function(_get_other_mark, type="float", string='Other marketing', readonly=True, store=False),
        #'coop_tp': fields.function(_get_coop_tp, type="float", string='COOP + Trade promo', readonly=True, store=False),
        #'total_cost': fields.function(_get_total_cost, type="float", string='Koszty total', readonly=True, store=False),
        
        #'fc_mark': fields.function(_get_fc_mark, type="float", string='FC Marka', readonly=True, store=False),
        #'gratis': fields.function(_get_value, type="float", string='Gratis', readonly=True, store=False, multi='get_value'),
        #'other_mark': fields.function(_get_value, type="float", string='Other marketing', readonly=True, store=False, multi='get_value'),
        #'coop_tp': fields.function(_get_value, type="float", string='COOP + Trade promo', readonly=True, store=False, multi='get_value'),
        #'total_cost': fields.function(_get_total_cost, type="float", string='Koszty total', readonly=True, store=False),
        
        #'nsh_promo_plan': fields.function(_get_nsh_promo_plan, type="float", string='NSH Akcji / NSH promo total', readonly=True, store=False),
        
        #nowe
        'gross_sales': fields.float('Gross sales'),
        'discount_front': fields.float('Rabat Front'),
        'discount_promo_contract': fields.float('Rabat promo kontraktowy'),
        'discount_promo_budget': fields.float('Rabat promo pozabudżetowy'),
        'nsh': fields.float('NSH'),
        'trade_promo': fields.float('Trade promo'),
        'nsv': fields.float('NSV'),
        'cogs': fields.float('COGS'),
        'other_cogs': fields.float('Other COGS'),
        'gp': fields.float('GP'),
        'gpp': fields.float('GP %'),
        'coop': fields.float('COOP'),
        'other_marketing': fields.float('Other Marketing'),
        'contrib': fields.float('Contrib.'),
        'contribp': fields.float('Contrib. %'),
    }
    
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'cd_report_ap')
        cr.execute("""
            CREATE OR REPLACE VIEW cd_report_ap AS (
                
                SELECT id, id as promotions_id, client_id, start_date, stop_date, start_month as month, start_year as year, discount_from, product_category, stage_id,
                gross_sales, discount_front, discount_promo_contract, discount_promo_budget, nsh, trade_promo, nsv, cogs, other_cogs, gp, gpp, coop, other_marketing, contrib, contribp
                FROM cd_promotions
                WHERE  sequence not in (40,90)

            )""")
        
    def open_promotions(self, cr, uid, ids, context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Akcje promocyjne', 
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'cd.promotions',
            'res_id': ids[0],
            'target': 'self',
        }

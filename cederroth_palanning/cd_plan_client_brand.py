# -*- coding: utf-8 -*-
"""
@author: mbereda
"""

from openerp.osv import fields, osv
from openerp.osv.orm import Model

import pdb

class cd_plan_client_brand(osv.Model):
    _name = "cd.plan.client.brand"
    
    def _get_plan(self, cr, uid, ids, name, arg, context=None):
        val={}
        plan_product_obj = self.pool.get('cd.plan.product')
        for plan in self.browse(cr, uid, ids):
            plan_value = 0.0
            plan_luz = 0.0
            plan_promo = 0.0
            exec_value = 0.0
            estimation = 0.0
            estim_sr = 0.0

            for product in plan.plan_client_id.plan_product_ids:
                if product.product_id.product_mark.id == plan.product_category_id.id:
                    data = plan_product_obj._get_plan_product_vals(cr, uid, [product.id], ['sum_plan_value','nsh_price','plan_value','promo_plan_value','sum_plan_value'], '')
                    plan_value += data[product.id]['sum_plan_value']
                    plan_luz += data[product.id]['plan_value']
                    plan_promo += data[product.id]['promo_plan_value']
                    exec_value += product.sum_exec_value
                    if product.new_product != '':
                        estimation += data[product.id]['sum_plan_value']
                    estim_sr += data[product.id]['nsh_price']*product.propo_count
                    
            val[plan.id] = {
                            'plan_value': plan_value, 
                            'exec_value': exec_value,
                            'plan_luz': plan_luz, 
                            'plan_promo': plan_promo,
                            'estimation_news': estimation,
                            'estim_sr': estim_sr,
                            }            
        return val
    
    _columns = {        
        'plan_client_id': fields.many2one('cd.plan.client', 'Plan Klient'),
        'product_category_id': fields.many2one('product.category', 'Marka', domain="[('parent_id','=',False)]", readonly=True),
        'forecast': fields.float('Budżet NSH'),
        'plan_value': fields.function(_get_plan, type='float', string='Estymacja NSH', store=False, readonly=True, multi='brand_value'),
        'exec_value': fields.function(_get_plan, type='float', string='Zrealizowana wartość', store=False, readonly=True, multi='brand_value'),
        'plan_luz': fields.function(_get_plan, type='float', string='Estymacja NSH standard', store=False, multi='brand_value'),
        'plan_promo': fields.function(_get_plan, type='float', string='Estymacja NSH promo', store=False, multi='brand_value'),
        'estimation_news': fields.function(_get_plan, type='float', string='Estymacja NSH nowości', store=False, readonly=True, multi='brand_value'),
        'estim_sr': fields.function(_get_plan, type='float', string='Estymacja NSH średnia miesiąc', store=False, readonly=True, multi='brand_value'),
    }

    def create(self, cr, uid, data, context=None):
        plan_id = super(cd_plan_client_brand, self).create(cr, uid, data, context=context)
        
        return plan_id
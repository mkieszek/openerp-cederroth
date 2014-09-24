# -*- coding: utf-8 -*-
"""
@author: mbereda
"""

from openerp.osv import fields, osv
from openerp.osv.orm import Model

import pdb

class cd_plan_section_brand(osv.Model):
    _name = "cd.plan.section.brand"
    
    def _get_plan_value(self, cr, uid, ids, name, arg, context=None):
        val={}
        client_brand_obj = self.pool.get('cd.plan.client.brand')
        for plan in self.browse(cr, uid, ids):
            plan_value = 0.0
            plan_luz = 0.0
            plan_promo = 0.0
            estimation_news = 0.0
            estim_sr = 0.0

            for plan_client in plan.plan_section_id.plan_client_ids:
                for client_brand in plan_client.plan_client_brand_ids:
                    if plan.product_category_id.id == client_brand.product_category_id.id:
                        data = client_brand_obj._get_plan(cr, uid, [client_brand.id], ['plan_value','plan_luz','plan_promo','estimation_news','estim_sr'], '')
                        plan_value += data[client_brand.id]['plan_value']
                        plan_luz += data[client_brand.id]['plan_luz']
                        plan_promo += data[client_brand.id]['plan_promo']
                        estimation_news += data[client_brand.id]['estimation_news']
                        estim_sr += data[client_brand.id]['estim_sr']
            
            val[plan.id] = {
                            'plan_value': plan_value,
                            'plan_luz': plan_luz,
                            'plan_promo': plan_promo,
                            'estimation_news': estimation_news,
                            'estim_sr': estim_sr,
                            }
        return val

    _columns = {        
        'plan_section_id': fields.many2one('cd.plan.section', 'Estymacja Departamentu'),
        'product_category_id': fields.many2one('product.category', 'Marka', domain="[('parent_id','=',False)]", required=True),
        'forecast': fields.float('Budżet NSH'),
        'plan_value': fields.function(_get_plan_value, type='float', string='Estymacja NSH', store=False, readonly=True, multi='plan_value'),
        'exec_value': fields.float('Zrealizowana wartość', readonly=True),
        'plan_luz': fields.function(_get_plan_value, type='float', string='Estymacja NSH standard', store=False, multi='plan_value'),
        'plan_promo': fields.function(_get_plan_value, type='float', string='Estymacja NSH promo', store=False, multi='plan_value'),
        'estimation_news': fields.function(_get_plan_value, type='float', string='Estymacja NSH nowości', store=False, readonly=True, multi='plan_value'),
        'estim_sr': fields.function(_get_plan_value, type='float', string='Estymacja NSH średnia miesiąc', store=False, readonly=True, multi='plan_value'),
    }

    def create(self, cr, uid, data, context=None):
        plan_id = super(cd_plan_section_brand, self).create(cr, uid, data, context=context)
        plan = self.browse(cr, uid, plan_id)
        for plan_client in plan.plan_section_id.plan_client_ids:
            vals = {}
            vals = {
                    'product_category_id': plan.product_category_id.id,
                    'forecast': 0.0,
                    'plan_client_id': plan_client.id,
                    }
            self.pool.get('cd.plan.client.brand').create(cr, uid, vals, context=None)
        
        return plan_id
    
    def unlink(self, cr, uid, ids, context=None):
        plans = self.browse(cr, uid, ids)
        client_brand_obj = self.pool.get('cd.plan.client.brand')
        for plan in plans:
            for plan_client in plan.plan_section_id.plan_client_ids:
                client_brand_ids = client_brand_obj.search(cr, uid, [('plan_client_id','=',plan_client.id),('product_category_id','=',plan.product_category_id.id)])
                client_brand_obj.unlink(cr, uid, client_brand_ids)
        plan_id = super(cd_plan_section_brand, self).unlink(cr, uid, ids, context=context)
        
        return plan_id
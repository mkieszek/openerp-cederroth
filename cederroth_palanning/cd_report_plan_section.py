# -*- coding: utf-8 -*-
'''
@author: mbereda
'''

from openerp.osv import fields, osv
from openerp.osv.orm import Model
from openerp import tools

import pdb

AVAILABLE_STATE = [('01',"W trakcie"), ('02',"Wykonany"), ('03',"Zaakceptowany")]

class cd_report_plan_section(osv.Model):
    _name = "cd.report.plan.section"
    _auto = False
    
    _columns = {
        'year': fields.integer('Rok', group_operator="max"),
        'month' : fields.char('Miesiąc'),
        'section_id' : fields.many2one('crm.case.section', 'Kanał'),
        'plan_section_id': fields.many2one('cd.plan.section', 'Plan Departament'),
        #'state_id': fields.selection(AVAILABLE_STATE, 'Status'),
        'state_id': fields.related('plan_section_id', 'state_id', type='selection', string='Status'),
        
        'nsv_total': fields.float('NSV Total'),
        'nsh_total': fields.float('NSH Total'),
        
        'gp_total': fields.float('Estym GP'),
        'gpp_total': fields.float('Estym_GP (%)', group_operator="avg"),
        'gross_sale': fields.float('Estym Gross Sale'),
        'disc_front_total': fields.float('Estym Rabaty Front'),
        'other_cogs': fields.float('Estym Other COGS'),
        'product_cogs': fields.float('Estym COGS'),
        'discount_pormo': fields.float('Estym Rabaty Promo'),
        'cm_total': fields.float('Estym Contrib.'),
        'cmp_total': fields.float('Estym Contrib. %', group_operator="avg"),
        'coop': fields.float('Estym COOP'),
        'nsh_p_nsh_t': fields.float('Estym NSH Promo / NSH Total', group_operator="avg"),
        'trade_promo_listing': fields.float('Estym Trade Promo + Listingi'),      
        'other_marketing' : fields.float('Other marketing')  
    }

    def init(self, cr, context=None):
        tools.drop_view_if_exists(cr, 'cd_report_plan_section')
        cr.execute("""
            CREATE OR REPLACE VIEW cd_report_plan_section AS (

           SELECT ps.id as id, ps.id as plan_section_id, ps.state_id,  rpc.month, rpc.year, ps.section_id, avg(rpc.gpp_promo) as gpp_promo, sum(rpc.nsh_promo) as nsh_promo, sum(rpc.nsv_promo) as nsv_promo, sum(rpc.plan_value) as plan_value, sum(rpc.cost_total) as cost_total, 
                sum(rpc.get_value) as get_value, sum(rpc.nsh_total) as nsh_total, avg(rpc.gpp_total) as gpp_total, avg(rpc.percentage) as percentage, sum(rpc.nsv_total) as nsv_total, sum(rpc.cost_promo) as cost_promo, 
                avg(rpc.cmp_total) as cmp_total, sum(rpc.coop) as coop, sum(rpc.gp_total) as gp_total, sum(rpc.cm_total) as cm_total, sum(rpc.trade_promo_listing) as trade_promo_listing, sum(rpc.product_cogs) as product_cogs, 
                sum(rpc.other_cogs) as other_cogs, avg(rpc.nsh_p_nsh_t) as nsh_p_nsh_t, sum(rpc.disc_front_total) as disc_front_total, sum(rpc.gross_sale) as gross_sale, sum(rpc.other_marketing) as other_marketing, 
                sum(rpc.discount_pormo) as discount_pormo
            FROM cd_report_plan_client as rpc
            LEFT JOIN cd_plan_client as cpc ON cpc.id = rpc.plan_client_id
            LEFT JOIN cd_plan_section as ps ON ps.id = cpc.plan_section_id
            GROUP BY ps.id, rpc.month, rpc.year

            )""")
        
    def open_plan_section(self, cr, uid, ids, context=None):
        plan_section_id = self.browse(cr, uid, ids[0]).plan_section_id.id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Plan Departament', 
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'cd.plan.section',
            'res_id': plan_section_id,
            'target': 'self',
        }
# -*- coding: utf-8 -*-
'''
@author: pczorniej
'''

from openerp.osv import fields, osv
from openerp.osv.orm import Model
from openerp import tools

import pdb

class cd_report_other_cogs(osv.Model):
    _name = "cd.report.other.cogs"
    _auto = False
    
    
    _columns = {
        'year': fields.integer("Year", required=True, group_operator="min"),
        'month' : fields.char('Month'),
        'section_id' : fields.many2one('crm.case.section', 'Kanał'),
        'client_id' : fields.many2one('res.partner','Klient'),
        'product_mark' : fields.many2one('product.category','Marka'),
        'categ_id' :  fields.many2one('product.category', 'Kategoria'),
        'count' : fields.integer('Ilość'),
        'cost' : fields.float('Koszt CU', group_operator="avg"),
        'value' : fields.float('Wartość COGS'),
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'cd_report_other_cogs')
        cr.execute("""
            CREATE OR REPLACE VIEW cd_report_other_cogs AS (
            
                select id, r.year, r.month, r.section_id, r.client_id, r.product_mark, r.categ_id, r.cost, r.count, r.value
from 
(select
    coc.id,
    CASE 
    WHEN coc.plan_client_id is not NULL THEN (cpc.year)
    WHEN coc.plan_mark_month_id is not NULL THEN (cpmm.year)
    ELSE NULL
    END as year,
    CASE 
    WHEN coc.plan_client_id is not NULL THEN (cpc.month)
    WHEN coc.plan_mark_month_id is not NULL THEN (cpmm.month)
    ELSE NULL
    END as month,
    CASE 
    WHEN coc.plan_client_id is not NULL THEN (rp.section_id)
    WHEN coc.plan_mark_month_id is not NULL THEN (NULL)
    ELSE NULL
    END as section_id,
    CASE 
    WHEN coc.plan_client_id is not NULL THEN (rp.id)
    WHEN coc.plan_mark_month_id is not NULL THEN (1)
    ELSE NULL
    END as client_id,
    pp.product_mark, 
    pt.categ_id,
    coc.price_cogs as cost,
    coc.count,
    coc.price_cogs * coc.count as value
from cd_other_cogs coc
left join cd_plan_client cpc on coc.plan_client_id = cpc.id
left join cd_plan_mark_month cpmm on coc.plan_mark_month_id = cpmm.id
LEFT JOIN product_product as pp ON pp.id=coc.product_id
left join product_template pt on pp.product_tmpl_id = pt.id
left join res_partner rp on rp.id = cpc.client_id

UNION

select
    co.id+20000,
    CASE 
    WHEN co.plan_client_id is not NULL THEN (cpc.year)
    WHEN co.plan_mark_month_id is not NULL THEN (cpmm.year)
    ELSE NULL
    END as year,
    CASE 
    WHEN co.plan_client_id is not NULL THEN (cpc.month)
    WHEN co.plan_mark_month_id is not NULL THEN (cpmm.month)
    ELSE NULL
    END as month,
    CASE 
    WHEN co.plan_client_id is not NULL THEN (rp.section_id)
    WHEN co.plan_mark_month_id is not NULL THEN (NULL)
    ELSE NULL
    END as section_id,
    CASE 
    WHEN co.plan_client_id is not NULL THEN (rp.id)
    WHEN co.plan_mark_month_id is not NULL THEN (1)
    ELSE NULL
    END as client_id,
    co.product_category, 
    NULL as categ_id,
    co.amount as cost,
    co.count,
    co.amount * co.count as value
from cd_other co
left join cd_plan_client cpc on co.plan_client_id = cpc.id
left join cd_plan_mark_month cpmm on co.plan_mark_month_id = cpmm.id
left join res_partner rp on rp.id = cpc.client_id
where co.target in ('c01', 'c02', 'c03', 'c04', 'c05', 'c06')

UNION

select cg.id+40000, cast(cp.start_year as integer) as year, cp.start_month as month, rp.section_id, rp.id as client_id, pp.product_mark as product_category, pt.categ_id, cg.price_cogs as cost, cg.count, cg.value_cogs as value
from cd_gratis cg
LEFT JOIN product_product as pp ON pp.id=cg.product_id
    LEFT JOIN cd_promotions as cp ON cg.promotions_id=cp.id
    left join res_partner rp on rp.id = cp.client_id
    left join product_template pt on pp.product_tmpl_id = pt.id
where cg.distribution = '01' and cp.sequence not in (40,90)

UNION

select cpl.id+60000, cpc.year, cpc.month, rp.section_id, cpc.client_id, pp.product_mark, pt.categ_id, pp.price_cogs as cost, cpl.count, pp.price_cogs * cpl.count as value
from cd_product_limited cpl
left join cd_plan_client cpc on cpl.plan_client_id = cpc.id
LEFT JOIN product_product as pp ON pp.id=cpl.product_id
left join product_template pt on pp.product_tmpl_id = pt.id
left join res_partner rp on rp.id = cpc.client_id

UNION

select ccp.id+80000, cast(cp.start_year as integer) as year, cp.start_month as month, rp.section_id, rp.id as client_id, cp.product_category as product_mark, NULL as categ_id, ccp.cu_cost as cost, ccp.count, ccp.cu_cost * ccp.count as value
from cd_cost_promotions ccp
LEFT JOIN cd_promotions as cp ON ccp.promotions_id=cp.id
left join res_partner rp on rp.id = cp.client_id
where cost_type = '04'  and cp.sequence not in (40,90)
) as r




            )""")
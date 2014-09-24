# -*- coding: utf-8 -*-
'''
@author: pczorniej
'''

from openerp.osv import fields, osv
from openerp.osv.orm import Model
from openerp import tools

import pdb

class cd_report_other_mark_month(osv.Model):
    _name = "cd.report.other.mark.month"
    _auto = False
    
    
    _columns = {
        'year': fields.integer("Year", required=True),
        'month' : fields.char('Month'),
        'section_id' : fields.many2one('crm.case.section', 'Kanał'),
        'client_id' : fields.many2one('res.partner','Klient'),
        'product_mark' : fields.many2one('product.category','Marka'),
        'pos_name' : fields.char('Nazwa POS'),
        'count' : fields.integer('Ilość'),
        'cost' : fields.float('Koszt CU'),
        'value' :fields.float('Wartość'),
    }

    def init(self, cr):
        #pdb.set_trace()
        tools.drop_view_if_exists(cr, 'cd_report_other_mark_month')
        sql_query = """
            CREATE OR REPLACE VIEW cd_report_other_mark_month AS (
            
                select id, r.year, r.month, r.section_id, r.client_id, r.product_mark, r.pos_name, r.cost, r.count, r.value
from 
(select
    com.id,
    CASE 
    WHEN com.plan_client_id is not NULL THEN (cpc.year)
    WHEN com.plan_mark_month_id is not NULL THEN (cpmm.year)
    ELSE NULL
    END as year,
    CASE 
    WHEN com.plan_client_id is not NULL THEN (cpc.month)
    WHEN com.plan_mark_month_id is not NULL THEN (cpmm.month)
    ELSE NULL
    END as month,
    CASE 
    WHEN com.plan_client_id is not NULL THEN (rp.section_id)
    WHEN com.plan_mark_month_id is not NULL THEN (NULL)
    ELSE NULL
    END as section_id,
    CASE 
    WHEN com.plan_client_id is not NULL THEN (rp.id)
    WHEN com.plan_mark_month_id is not NULL THEN (1)
    ELSE NULL
    END as client_id,
    com.product_category_id as product_mark,
    com.pos_name,
    com.cu_cost as cost,
    com.count,
    com.cu_cost * com.count as value
from cd_other_marketing com
left join cd_plan_client cpc on com.plan_client_id = cpc.id
left join cd_plan_mark_month cpmm on com.plan_mark_month_id = cpmm.id
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
    'Szkolenia' as pos_name,
    co.amount as cost,
    co.count,
    co.amount * co.count as value
from cd_other co
left join cd_plan_client cpc on co.plan_client_id = cpc.id
left join cd_plan_mark_month cpmm on co.plan_mark_month_id = cpmm.id
left join res_partner rp on rp.id = cpc.client_id
where co.target in ('05','08')

UNION

select ccp.id+40000, cast(cp.start_year as integer) as year, cp.start_month as month, rp.section_id, rp.id as client_id, cp.product_category as product_mark, ccd.name as pos_name, ccp.cu_cost as cost, ccp.count, ccp.cu_cost * ccp.count as value
from cd_cost_promotions ccp
LEFT JOIN cd_promotions as cp ON ccp.promotions_id=cp.id
left join res_partner rp on rp.id = cp.client_id
left join cd_cost_data ccd on ccd.id = ccp.cost_data_id
where ccp.cost_type = '01' and cp.sequence not in (40,90)
) as r


            )"""
        cr.execute(sql_query)
        
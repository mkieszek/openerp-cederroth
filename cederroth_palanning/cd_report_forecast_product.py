# -*- coding: utf-8 -*-
'''
@author: mbereda
'''

from openerp.osv import fields, osv
from openerp.osv.orm import Model
from openerp import tools

import pdb

class cd_report_forecast_product(osv.Model):
    _name = "cd.report.forecast.product"
    _auto = False
    
    
    _columns = {
        'year': fields.integer("Year", group_operator="min"),
        'month' : fields.char('Month', group_operator="min"),
        'product_id': fields.many2one('product.product', 'Produkt'),
        'count' : fields.integer('Ilość'),
        'product_movex': fields.char('MOVEX'),
        'section_id': fields.many2one('crm.case.section', 'Departament'),
        'client_id': fields.many2one('res.partner', 'Klient'),
        'categ_id': fields.many2one('product.category', 'Kategoria'),
        'product_mark': fields.many2one('product.category', 'Marka'),
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'cd_report_forecast_product')
        cr.execute("""
            CREATE OR REPLACE VIEW cd_report_forecast_product AS (
            SELECT 
cast(cast((year-2010) as varchar)||cast(cast(month as integer) as varchar)||client_id||product_id as bigint) as id
,r.product_id
, r.product_movex
, sum(r.count) as count
, r.month
, r.year
, r.section_id
, r.client_id
, r.product_mark
, r.categ_id
FROM (
    SELECT pp.id as product_id, pp.default_code as product_movex, cpp.month as month, cpp.year as year, cpp.plan_count as count, rp.section_id, rp.id as client_id, pp.product_mark, pt.categ_id
    FROM cd_plan_product as cpp
    left JOIN product_product as pp ON pp.id=cpp.product_id
    left join cd_plan_client cpc on cpc.id = cpp.plan_client_id
    left join res_partner rp on rp.id = cpc.client_id
    left join product_template pt on pp.product_tmpl_id = pt.id
    UNION

    SELECT pp.id as product_id, pp.default_code as product_movex,
    CASE 
    WHEN oc.plan_client_id is not NULL THEN (cpc.month)
    WHEN oc.plan_mark_month_id is not NULL THEN (cpmm.month)
    ELSE NULL
    END as month,
    CASE 
    WHEN oc.plan_client_id is not NULL THEN (cpc.year)
    WHEN oc.plan_mark_month_id is not NULL THEN (cpmm.year)
    ELSE NULL
    END as year,
    oc.count as count,
    CASE 
    WHEN oc.plan_client_id is not NULL THEN (rp.section_id)
    WHEN oc.plan_mark_month_id is not NULL THEN (NULL)
    ELSE NULL
    END as section_id,
    CASE 
    WHEN oc.plan_client_id is not NULL THEN (rp.id)
    WHEN oc.plan_mark_month_id is not NULL THEN (1)
    ELSE NULL
    END as client_id, 
    pp.product_mark, 
    pt.categ_id
    FROM cd_other_cogs as oc
    LEFT JOIN product_product as pp ON pp.id=oc.product_id
    left join cd_plan_client cpc on cpc.id = oc.plan_client_id
    left join res_partner rp on rp.id = cpc.client_id
    left join cd_plan_mark_month cpmm on cpmm.id = oc.plan_mark_month_id
    left join product_template pt on pp.product_tmpl_id = pt.id
    --WHERE oc.plan_client_id is not NULL or oc.plan_mark_month_id is not NULL

    UNION
    
    SELECT pp.id as product_id, pp.default_code as product_movex, cpc.month as month, cpc.year as year, cpl.count as count, rp.section_id, rp.id as client_id, pp.product_mark, pt.categ_id
    FROM cd_product_limited as cpl
    LEFT JOIN product_product as pp ON pp.id=cpl.product_id
    LEFT JOIN cd_plan_client as cpc ON cpc.id=cpl.plan_client_id
    left join res_partner rp on rp.id = cpc.client_id
    left join product_template pt on pp.product_tmpl_id = pt.id
    
    UNION

    SELECT pp.id as product_id, pp.default_code as product_movex, cpc.month as month, cpc.year as year, cs.count as count, rp.section_id, rp.id as client_id, pp.product_mark, pt.categ_id
    FROM cd_sale as cs
    LEFT JOIN product_product as pp ON pp.id=cs.product_id
    LEFT JOIN cd_plan_client as cpc ON cpc.id=cs.plan_client_id
    left join res_partner rp on rp.id = cpc.client_id
    left join product_template pt on pp.product_tmpl_id = pt.id
    
    UNION

    SELECT pp.id as product_id, pp.default_code as product_movex, to_char(cp.discount_FROM, 'MM') as month, to_char(cp.discount_FROM, 'YYYY')::int as year, cpr.amount_product as count, rp.section_id, rp.id as client_id, pp.product_mark, pt.categ_id
    FROM cd_product_rel as cpr
    LEFT JOIN product_product as pp ON pp.id=cpr.product_id
    LEFT JOIN cd_promotions as cp ON cpr.promotions_id=cp.id
    left join res_partner rp on rp.id = cp.client_id
    left join product_template pt on pp.product_tmpl_id = pt.id
    where cp.sequence not in (40,90)

    UNION

    SELECT pp.id as product_id, pp.default_code as product_movex, to_char(cp.discount_FROM, 'MM') as month, to_char(cp.discount_FROM, 'YYYY')::int as year, cg.count as count, rp.section_id, rp.id as client_id, pp.product_mark, pt.categ_id
    FROM cd_gratis as cg
    LEFT JOIN product_product as pp ON pp.id=cg.product_id
    LEFT JOIN cd_promotions as cp ON cg.promotions_id=cp.id
    left join res_partner rp on rp.id = cp.client_id
    left join product_template pt on pp.product_tmpl_id = pt.id
    where cp.sequence not in (40,90)

) as r
left join res_partner rp on client_id = rp.id
where rp.active = true and count > 0
group by r.year, r.month, r.section_id, r.client_id, r.product_mark, r.categ_id, r.product_id, r.product_movex

            )""")
# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.osv.orm import Model
from openerp import tools

import pdb


class cd_report_trade_promo(osv.Model):
    _name = "cd.report.trade.promo"
    _auto = False
    
    
    _columns = {
        'year': fields.integer("Year", required=True),
        'month' : fields.char('Month'),
        'section_id' : fields.many2one('crm.case.section', 'Kanał'),
        'client_id' : fields.many2one('res.partner','Klient'),
        'product_mark' : fields.many2one('product.category','Marka'),
        'name' : fields.char('Nazwa POS'),
        'count' : fields.integer('Ilość'),
        'cost' : fields.float('Koszt CU'),
        'value' :fields.float('Wartość'),
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'cd_report_trade_promo')
        cr.execute("""
            CREATE OR REPLACE VIEW cd_report_trade_promo AS (
select max(id) as id, r.year, r.month, r.section_id, r.client_id, r.product_mark, r.name, avg(r.cost) as cost, sum(r.count) as count, sum(r.value) as value
from 
(

select
    co.id,
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
    co.product_category as product_mark,
    'Akcje pozabudżetowe - Trade Promo' as name,
    co.amount as cost,
    co.count,
    co.amount * co.count as value
from cd_other co
left join cd_plan_client cpc on co.plan_client_id = cpc.id
left join cd_plan_mark_month cpmm on co.plan_mark_month_id = cpmm.id
left join res_partner rp on rp.id = cpc.client_id
where co.target in ('03','06')

UNION

select ccp.id+40000, cast(cp.start_year as integer) as year, cp.start_month as month, rp.section_id, rp.id as client_id, cp.product_category as product_mark, ccd.name as name, ccp.cu_cost as cost, ccp.count, ccp.cu_cost * ccp.count as value
from cd_cost_promotions ccp
LEFT JOIN cd_promotions as cp ON ccp.promotions_id=cp.id
left join res_partner rp on rp.id = cp.client_id
left join cd_cost_data ccd on ccd.id = ccp.cost_data_id
where ccp.cost_type = '03' and cp.sequence not in (40,90)

UNION

select max(cpr.id)+60000, cast(cp.start_year as integer) as year, cp.start_month as month, rp.section_id, cp.client_id, pp.product_mark, 
    'Back promo' as name, 
avg(CASE
    WHEN cdp.discount_back_trade_promo IS NOT NULL THEN cpr.prom_price/100*cdp.discount_back_trade_promo
    WHEN rp.discount_back_trade_promo IS NOT NULL THEN cpr.prom_price/100*rp.discount_back_trade_promo
    ELSE 0
END) AS cost,

    sum(cpr.amount_product) as count,
    sum(CASE
    WHEN cdp.discount_back_trade_promo IS NOT NULL THEN cpr.prom_price/100*cdp.discount_back_trade_promo*cpr.amount_product
    WHEN rp.discount_back_trade_promo IS NOT NULL THEN cpr.prom_price/100*rp.discount_back_trade_promo*cpr.amount_product
    ELSE 0
END) AS value
from cd_product_rel cpr
left join cd_promotions cp on cp.id = cpr.promotions_id
left join res_partner rp on rp.id = cp.client_id
left join product_product pp on pp.id = cpr.product_id
left join cd_discount_partner cdp on cdp.client_id = cp.client_id and cdp.product_category = pp.product_mark
left join crm_case_section ccs on ccs.id = rp.section_id
where cp.sequence not in (40,90) and (CASE
    WHEN cdp.discount_back_trade_promo IS NOT NULL THEN cpr.prom_price/100*cdp.discount_back_trade_promo
    WHEN rp.discount_back_trade_promo IS NOT NULL THEN cpr.prom_price/100*rp.discount_back_trade_promo
    ELSE 0
END) > 0
group by cp.start_year, cp.start_month, rp.section_id, cp.client_id, pp.product_mark

UNION

select max(cpp.id)+80000, cpc.year as year, cpc.month as month, rp.section_id, cpc.client_id, pp.product_mark, 
    'Back' as name, 
avg(CASE
WHEN cl.price_sale is not null then
    CASE
        WHEN cdp.discount_back_trade_promo IS NOT NULL THEN (cl.price_sale - (cl.price_sale/100*cdp.discount_front))/100*cdp.discount_back_trade_promo
        WHEN rp.discount_back_trade_promo IS NOT NULL THEN (cl.price_sale - (cl.price_sale/100*rp.discount_front))/100*rp.discount_back_trade_promo
        ELSE 0
    END
ELSE 0
END) as cost,

    sum(cpp.plan_count) as count,
    sum(CASE WHEN cl.price_sale is not null then
    CASE
        WHEN cdp.discount_back_trade_promo IS NOT NULL THEN (cl.price_sale - (cl.price_sale/100*cdp.discount_front))/100*cdp.discount_back_trade_promo*cpp.plan_count
        WHEN rp.discount_back_trade_promo IS NOT NULL THEN (cl.price_sale - (cl.price_sale/100*rp.discount_front))/100*rp.discount_back_trade_promo*cpp.plan_count
        ELSE 0
    END
        ELSE 0
        END) as value
from cd_plan_product cpp
left join cd_plan_client cpc on cpc.id = cpp.plan_client_id
left join res_partner rp on rp.id = cpc.client_id
left join product_product pp on pp.id = cpp.product_id
left join cd_discount_partner cdp on cdp.client_id = cpc.client_id and cdp.product_category = pp.product_mark
left join (select client_id, product_id, max(price_sale)as price_sale from cd_listing where status_l = '0' group by client_id, product_id) as cl on cl.client_id = cpc.client_id and cl.product_id = cpp.product_id
left join crm_case_section ccs on ccs.id = rp.section_id
where (CASE
WHEN cl.price_sale is not null then
    CASE
        WHEN cdp.discount_back_trade_promo IS NOT NULL THEN (cl.price_sale - (cl.price_sale/100*cdp.discount_front))/100*cdp.discount_back_trade_promo
        WHEN rp.discount_back_trade_promo IS NOT NULL THEN (cl.price_sale - (cl.price_sale/100*rp.discount_front))/100*rp.discount_back_trade_promo
        ELSE 0
    END
ELSE 0
END) > 0
group by cpc.year, cpc.month, rp.section_id, cpc.client_id, pp.product_mark

) as r
group by year, month, section_id, client_id, product_mark, name
            
            
            )""")
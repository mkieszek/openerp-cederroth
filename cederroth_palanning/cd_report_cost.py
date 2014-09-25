# -*- coding: utf-8 -*-
'''
@author: mbereda
'''

from openerp.osv import fields, osv
from openerp.osv.orm import Model
from openerp import tools

import pdb

class cd_report_cost(osv.Model):
    _name = "cd.report.cost"
    _auto = False
    
    
    _columns = {
        'year': fields.integer("Year", required=True, group_operator="min"),
        'month' : fields.char('Month'),
        'section_id' : fields.many2one('crm.case.section', 'Kanał'),
        'client_id' : fields.many2one('res.partner','Klient'),
        'product_mark' : fields.many2one('product.category','Marka'),
        'count' : fields.integer('Ilość'),
        'cost' : fields.float('Koszt CU', group_operator="avg"),
        'value' : fields.float('Wartość COGS'),
        'type': fields.char('Typ kosztu'),
        'promotion_id': fields.many2one('cd.promotions', 'Akcje promocyjne'),
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'cd_report_cost')
        cr.execute("""
            CREATE OR REPLACE VIEW cd_report_cost AS (
SELECT *
            FROM (
            select ccp.id+10000 as id, cp.id as promotion_id, cast(cp.start_year as integer) as year, cp.start_month as month, rp.section_id, rp.id as client_id, cp.product_category as product_mark, ccd.name as name, ccp.cu_cost as cost, ccp.count, ccp.cu_cost * ccp.count as value, 'trade promo' as type
            from cd_cost_promotions ccp
            LEFT JOIN cd_promotions as cp ON ccp.promotions_id=cp.id
            left join res_partner rp on rp.id = cp.client_id
            left join cd_cost_data ccd on ccd.id = ccp.cost_data_id
            where ccd.cost_type = '03'
            
            UNION
            
            select max(cpr.id)+20000 as id, cp.id as promotion_id, cast(cp.start_year as integer) as year, cp.start_month as month, rp.section_id, cp.client_id, pp.product_mark, 'Back promo' as name,
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
            END) AS value, 'trade promo' as type
            from cd_product_rel cpr
            left join cd_promotions cp on cp.id = cpr.promotions_id
            left join res_partner rp on rp.id = cp.client_id
            left join product_product pp on pp.id = cpr.product_id
            left join cd_discount_partner cdp on cdp.client_id = cp.client_id and cdp.product_category = pp.product_mark
            left join crm_case_section ccs on ccs.id = rp.section_id
            where (CASE
                WHEN cdp.discount_back_trade_promo IS NOT NULL THEN cpr.prom_price/100*cdp.discount_back_trade_promo
                WHEN rp.discount_back_trade_promo IS NOT NULL THEN cpr.prom_price/100*rp.discount_back_trade_promo
                ELSE 0
            END) > 0
            group by cp.start_year, cp.start_month, rp.section_id, cp.client_id, pp.product_mark, cp.id
            
            UNION
            
            select ccp.id+30000 as id, cp.id as promotion_id, cast(cp.start_year as integer) as year, cp.start_month as month, rp.section_id, rp.id as client_id, cp.product_category as product_mark, ccd.name as name, ccp.cu_cost as cost, ccp.count, ccp.cu_cost * ccp.count as value, 'coop' as type
            from cd_cost_promotions ccp
            LEFT JOIN cd_promotions as cp ON ccp.promotions_id=cp.id
            left join res_partner rp on rp.id = cp.client_id
            left join cd_cost_data ccd on ccd.id = ccp.cost_data_id
            where ccd.cost_type = '02'
            UNION
            
            select max(cpr.id)+40000 as id, cp.id as promotion_id, cast(cp.start_year as integer) as year, cp.start_month as month, rp.section_id, cp.client_id, pp.product_mark, 
                'Back promo' as name, 
            avg(CASE
                WHEN cdp.discount_back_coop IS NOT NULL THEN cpr.prom_price/100*cdp.discount_back_coop
                WHEN rp.discount_back_coop IS NOT NULL THEN cpr.prom_price/100*rp.discount_back_coop
                ELSE 0
            END) AS cost,
            
                sum(cpr.amount_product) as count,
                sum(CASE
                WHEN cdp.discount_back_coop IS NOT NULL THEN cpr.prom_price/100*cdp.discount_back_coop*cpr.amount_product
                WHEN rp.discount_back_coop IS NOT NULL THEN cpr.prom_price/100*rp.discount_back_coop*cpr.amount_product
                ELSE 0
            END) AS value, 'coop' as type
            from cd_product_rel cpr
            left join cd_promotions cp on cp.id = cpr.promotions_id
            left join res_partner rp on rp.id = cp.client_id
            left join product_product pp on pp.id = cpr.product_id
            left join cd_discount_partner cdp on cdp.client_id = cp.client_id and cdp.product_category = pp.product_mark
            left join crm_case_section ccs on ccs.id = rp.section_id
            where (CASE
                WHEN cdp.discount_back_coop IS NOT NULL THEN cpr.prom_price/100*cdp.discount_back_coop
                WHEN rp.discount_back_coop IS NOT NULL THEN cpr.prom_price/100*rp.discount_back_coop
                ELSE 0
            END) > 0
            group by cp.start_year, cp.start_month, rp.section_id, cp.client_id, pp.product_mark, cp.id
            
            UNION
            
            select cg.id+50000 as id, cp.id as promotion_id, cast(cp.start_year as integer) as year, cp.start_month as month, rp.section_id, rp.id as client_id, pp.product_mark as product_category, 'other cogs' as name, cg.price_cogs as cost, cg.count, cg.value_cogs as value, 'other cogs' as type
            from cd_gratis cg
            LEFT JOIN product_product as pp ON pp.id=cg.product_id
                LEFT JOIN cd_promotions as cp ON cg.promotions_id=cp.id
                left join res_partner rp on rp.id = cp.client_id
                left join product_template pt on pp.product_tmpl_id = pt.id
            where cg.distribution = '01'
            
            UNION
            
            select ccp.id+60000 as id, cp.id as promotion_id, cast(cp.start_year as integer) as year, cp.start_month as month, rp.section_id, rp.id as client_id, cp.product_category as product_mark, 'other cogs' as name, ccp.cu_cost as cost, ccp.count, ccp.cu_cost * ccp.count as value, 'other cogs' as type
            from cd_cost_promotions ccp
            LEFT JOIN cd_promotions as cp ON ccp.promotions_id=cp.id
            left join res_partner rp on rp.id = cp.client_id
            left join cd_cost_data as ccd on ccp.cost_data_id = ccd.id
            where ccd.cost_type = '04'
            
            UNION 
            
            select ccp.id+70000 as id, cp.id as promotion_id, cast(cp.start_year as integer) as year, cp.start_month as month, rp.section_id, rp.id as client_id, cp.product_category as product_mark, ccd.name as pos_name, ccp.cu_cost as cost, ccp.count, ccp.cu_cost * ccp.count as value, 'other marketing' as type
            from cd_cost_promotions ccp
            LEFT JOIN cd_promotions as cp ON ccp.promotions_id=cp.id
            left join res_partner rp on rp.id = cp.client_id
            left join cd_cost_data ccd on ccd.id = ccp.cost_data_id
            where ccd.cost_type = '01'
            ) as w

            )""")
# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp.osv import fields

class crm_case_section(osv.osv):
    _inherit = "crm.case.section"
    _columns = {
        'tms_user_id': fields.many2one('res.users', 'Trade Marketing Specialist', domain="[('groups_id.name', '=', 'Trade Marketing Specialist')]"),
    }
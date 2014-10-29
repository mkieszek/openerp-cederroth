# -*- coding: utf-8 -*-
'''
Created on 14 paź 2014

@author: sony
'''
from openerp.osv import osv, fields
import pdb

class cd_report_promo_wizard(osv.osv_memory):
    _name = 'cd.report.promo.wizard'
    _description = "Promo report wizard"
    
    def print_report(self, cr, uid, ids, context=None):
        w = self.browse(cr, uid, ids, context=context)[0]
        data = {}
        return { 'type': 'ir.actions.report.xml', 'report_name': 'cd.report_promo_board', 'datas': data}
    
    def send_report(self, cr, uid, ids, context=None):
        template = self.pool.get('ir.model.data').get_object(cr, uid, 'cederroth_palanning', 'email_template_cd_report_promo_board')
        self.pool.get('email.template').send_mail(cr, uid, template.id, ids[0], force_send=True, context=context)
        return True
        
    def print_report_salesman(self, cr, uid, ids, context=None):
        w = self.browse(cr, uid, ids, context=context)[0]
        data = {}
        return { 'type': 'ir.actions.report.xml', 'report_name': 'cd.report_promo_salesman', 'datas': data}
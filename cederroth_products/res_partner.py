# -*- coding: utf-8 -*-
import os
import shutil
import logging
import pdb


from openerp.osv.orm import Model
from openerp.osv import fields

class res_partner(Model):
    _inherit = "res.partner"
    _columns = {
        'listing' : fields.one2many('cd.listing','client_id', 'Listing'),
        'cformat' : fields.one2many('cd.client.format','client_id','Client Format'),
    }
    _defaults = {
        'user_id': lambda obj, cr, uid, ctx=None: uid,
    }
    
    def create(self, cr, uid, data, context=None):
        #pdb.set_trace()
        part_id = super(res_partner, self).create(cr, uid, data, context=context)
        
        if data.has_key('user_id'):
            if data['user_id']:  
                partner_obj = self.pool.get('res.users')
                partner = partner_obj.search(cr, uid, [('id','=',data['user_id'])], context=context)
                partner_id = partner_obj.browse(cr, uid, partner)[0].partner_id.id
                self.message_subscribe(cr, uid, [part_id], [partner_id], context=context)
               
        return part_id

        
        
    def write(self, cr, uid, ids, data, context=None):
        #pdb.set_trace()
        part_id = super(res_partner, self).write(cr, uid, ids, data, context=context)
        
        for client in self.browse(cr, uid, ids):
            if 'section_id' in data and data['section_id']:
                plan_client_obj = self.pool.get('cd.plan.client')
                plan_section_obj = self.pool.get('cd.plan.section')
                plan_client_ids = plan_client_obj.search(cr, uid, ['|',('state_id','=','01'),('state_id','=',False),('client_id','=',client.id)])
                for plan_client in plan_client_obj.browse(cr, uid, plan_client_ids):
                    if plan_client.blocked == False:
                        new_section_id = plan_section_obj.search(cr, uid, [('section_id','=',data['section_id']),('month','=',plan_client.month),('year','=',plan_client.year)])
                        if new_section_id:
                            plan_client_obj.write(cr, uid, [plan_client.id], {'plan_section_id':new_section_id[0]})
                        
                    
                            
        
        
        if data.has_key('user_id'):
            if data['user_id']:  
                partner_obj = self.pool.get('res.users')
                partner = partner_obj.search(cr, uid, [('id','=',data['user_id'])], context=context)
                partner_id = partner_obj.browse(cr, uid, partner)[0].partner_id.id
                self.message_subscribe(cr, uid, ids, [partner_id], context=context)
        
        return part_id
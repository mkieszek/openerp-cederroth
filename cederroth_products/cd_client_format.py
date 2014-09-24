# -*- coding: utf-8 -*-
import pdb

from openerp.osv import fields, osv

class cd_client_format(osv.Model):
    _name = "cd.client.format"
    _columns = {
        'client_id' : fields.many2one('res.partner', 'Client', required=True),
        'name': fields.char('Name', size=64, required=True),
        'shops' : fields.integer('shops'),
        'status' : fields.boolean('Active'),
        'fclient_id' : fields.one2many('cd.listing','fclient_id','Client Format'),
    }
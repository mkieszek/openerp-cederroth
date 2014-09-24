# -*- coding: utf-8 -*-
"""
Created on Tue Sep 17 14:18:21 2013

@author: pczorniej
"""
from openerp.osv import fields, osv
from tools.translate import _

class cd_pack_type(osv.Model):
    _name = "cd.pack.type"
    _columns = {
        'name': fields.char('Name', size=64),
    }
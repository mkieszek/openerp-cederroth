# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from tools.translate import _

class cd_listing_status(osv.Model):
    _name = "cd.listing.status"
    _columns = {
        'name': fields.char('Name', size=64),
    }
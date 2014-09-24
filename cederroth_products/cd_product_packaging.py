# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv.orm import Model
from openerp.osv import fields
from openerp.tools.translate import _

class cd_product_packaging(Model):
    _name = 'product.packaging'
    _inherit = 'product.packaging'
    _columns = {
        'weight_tolerance': fields.integer('Tolerancja wagi'),
        'box_qty' : fields.integer('Ilość kartonów'),
        'layer_qty' : fields.integer('Ilość sztuk na warstwie'),
        'ean_code' : fields.char('EAN code', size=13),
        }
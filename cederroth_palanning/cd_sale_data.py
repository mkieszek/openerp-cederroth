'''
Created on 16 maj 2014

@author: sony
'''

from openerp.osv import fields, osv
from openerp.osv.orm import Model
from datetime import timedelta
import calendar
import datetime
import pdb
import xlrd

"""
import xlrd
workbook = xlrd.open_workbook('my_workbook.xls')
worksheet = workbook.sheet_by_name('Sheet1')
num_rows = worksheet.nrows - 1
num_cells = worksheet.ncols - 1
curr_row = -1
while curr_row < num_rows:
    curr_row += 1
    row = worksheet.row(curr_row)
    print 'Row:', curr_row
    curr_cell = -1
    while curr_cell < num_cells:
        curr_cell += 1
        # Cell Types: 0=Empty, 1=Text, 2=Number, 3=Date, 4=Boolean, 5=Error, 6=Blank
        cell_type = worksheet.cell_type(curr_row, curr_cell)
        cell_value = worksheet.cell_value(curr_row, curr_cell)
        print '    ', cell_type, ':', cell_value
"""

class cd_sale_data(osv.Model):
    _name = "cd.sale.data"
    _description = "Sale data"
    
    _columns = {
                'year' : fields.integer('Year',),
                'month' : fields.integer('Month',),
                'retailer' : fields.char('Retailer', size=255),
                'item' : fields.char('Item', size=255),
                'net_value' : fields.float('Net value'),
                'qty': fields.integer('Qty (CU)'),
                'sale_import_id': fields.many2one('cd.sale.data.import', 'Import'),
    }
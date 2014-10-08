# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp.osv.orm import Model

import datetime
import xlrd
import pdb

AVAILABLE_MONTHS = [('01',"Styczeń"), ('02',"Luty"), ('03',"Marzec"), ('04',"Kwiecień"), ('05',"Maj"), ('06',"Czerwiec"), 
          ('07',"Lipiec"), ('08',"Sierpień"), ('09',"Wrzesień"), ('10',"Październik"), ('11',"Listopad"), ('12',"Grudzień")]


class cd_dch_import(osv.Model):
    _name = "cd.dch.import"
    
    _columns = {
        'filename' : fields.char('Filename', size=255),
        'import_file' : fields.binary('Plik do importu', required=True),
        'year': fields.integer('Rok', required=True),
        'month': fields.selection(AVAILABLE_MONTHS, 'Miesiąc', required=True),
        'create_date': fields.date('Data utworzenia', readonly=True),
        'log' : fields.html('Logi', readonly=True),
   }
    
    
    def create(self, cr, uid, data, context=None):
        
        import_id = super(cd_dch_import, self).create(cr, uid, data, context=context)
        log = self.import_dch(cr, uid, [import_id], context)
        
        self.write(cr, uid, import_id, {'log':log})

        return import_id
    
    
    def import_dch(self, cr, uid, ids, context=None):
        
        result = ''
        w = self.browse(cr, uid, ids, context=context)[0]

        fh = open(w.filename, "wb")
        #pdb.set_trace()
        fh.write(w.import_file.decode('base64'))
        fh.close()
                    
        workbook = xlrd.open_workbook(w.filename)
        worksheet = workbook.sheet_by_name('Sheet1')
        num_rows = worksheet.nrows - 1
        num_cells = worksheet.ncols - 1
        curr_row = 1
        
        plan_product_obj = self.pool.get('cd.plan.product')
        
        client_vals = {}
        date_vals = {}
        
        #pdb.set_trace()
        result = "<table>"
        while curr_row < num_rows:
            
            client_id = None
            product_id = None
            plan_client_id = None
            plan_product_id = None
            vals = None
            
            str_type = "INFO"
            curr_row += 1
                
            str_msg = "Zaimportowany"
            row = worksheet.row(curr_row)
            
            year = int(row[0].value)
            month = str(int(row[1].value)).zfill(2)
            
            retailer_tab = row[2].value.split(' ')
            client_ident = retailer_tab[0]
            movex_code = row[3].value
            value = str(int(row[6].value))
            
            if w.year == year and w.month == int(month):
                client_id = self.pool.get('res.partner').search(cr, uid, [('ref','=',client_ident)])
                if client_id:
                    product_id = self.pool.get('product.product').search(cr, uid, [('default_code','=',movex_code)])
                    if product_id:
                        plan_client_id = self.pool.get('cd.plan.client').search(cr, uid, [('client_id','=',client_id),('year','=',year),('month','=',month)])
                        if plan_client_id:
                            plan_product_id = self.pool.get('cd.plan.product').search(cr, uid, [('plan_client_id','=',plan_client_id),('product_id','=',product_id)])
                            if plan_product_id:
                                vals = {'plan_count': value, 'propo_count': value}
                                self.pool.get('cd.plan.product').write(cr, uid, plan_product_id, vals)
                                str_msg = "Zaimportowano"
                            else:
                                str_type = "ERROR "
                                str_msg = "Brak planu produkt"
                        else:
                            str_type = "ERROR "
                            str_msg = "Brak planu klient"
                    else:
                        str_type = "ERROR "
                        str_msg = "Nierozpoznany produkt"
                else:
                    str_type = "ERROR "
                    str_msg = "Nierozpoznany klient"
            else:
                str_msg = "Zignorowany"
            
            result += '<tr><td>{0} </td><td>Wiersz nr: {1} </td><td>{2} </td></tr>'.format(str_type, curr_row + 1, str_msg)
        result += "</table>"
        return result
        #pdb.set_trace()
            
            

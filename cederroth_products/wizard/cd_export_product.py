# -*- coding: utf-8 -*-

from openerp.osv import osv,fields
from tools.translate import _
import pdb
import datetime
import base64

AVAILABLE_EXPORTS = [
    ('selgros', 'Selgros'),
    ('auchan', 'Auchan'),
    ('makro_real', 'Makro / Real'),
    ('carrefour', 'Carrefour'),
    ('kaufland','Kaufland'),
    ('leclerc','Leclerc'),
    ('tesco','Tesco'),
    ('hebe','Hebe'),
    ('cederroth','Cederroth'),
    ('super_pharm','Super-Pharm'),
]

class cd_export_products(osv.osv_memory):
    _name = 'cd.export.products'
    
    _columns = {
        'name': fields.char('Export'),
        'product_ids': fields.many2many('product.product', string='Produkty'),
        'file_export': fields.binary('Export file', readolny=True),
        'client' : fields.selection(AVAILABLE_EXPORTS, 'Kleint'),
        'state': fields.selection([('choose', 'choose'),
                                       ('get', 'get')])
    }
    _defaults = { 
        'state': 'choose',
        'name': 'lang.tar.gz',
    }
    def _convert_str(self, text):
        return text.encode('cp1250')
    
    def create(self, cr, uid, vals, context=None):
        #pdb.set_trace()
        
        export = super(cd_export_products, self).create(cr, uid, vals, context=context)
        return export
    
    def export_products(self, cr, uid, ids, context=None):
        #pdb.set_trace()
        w = self.browse(cr, uid, ids, context=context)[0]
        export = ''
        if w.client == "selgros":
            export = self.selgros(cr, uid, ids, context=None)
        elif w.client == "auchan":
            export = self.auchan(cr, uid, ids, context=None)
        elif w.client == "makro_real":
            export = self.makro_real(cr, uid, ids, context=None)
        elif w.client == "carrefour":
            export = self.carrefour(cr, uid, ids, context=None)
        elif w.client == "kaufland":
            export = self.kaufland(cr, uid, ids, context=None)
        elif w.client == "leclerc":
            export = self.leclerc(cr, uid, ids, context=None)
        elif w.client == "tesco":
            export = self.tesco(cr, uid, ids, context=None)
        elif w.client == "hebe":
            export = self.hebe(cr, uid, ids, context=None)
        elif w.client == "cederroth":
            export = self.cederroth_pl(cr, uid, ids, context=None)
        elif w.client == "super_pharm":
            export = self.cederroth_pl(cr, uid, ids, context=None)
            
        out = base64.encodestring(export)
        today_string = datetime.datetime.today().strftime('%Y%m%d')
        file_name = '%s%s.csv' % (w.client, today_string)
        self.write(cr, uid, ids, {'file_export': out,
                                  'state': 'get',
                                  'name': file_name}, context=context)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cd.export.products',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': w.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
            
    def selgros(self, cr, uid, ids, context=None):
        #pdb.set_trace()
        w = self.browse(cr, uid, ids, context=context)[0]
        export = ''

        #row_format = "%s,%.0f,%.0f,%s,%s,%s,%s,%s,%s,%s,%s,%s\n"
        #header_row = ("Kod dostawcy,Kod EAN,Kod EAN kartonu,Nazwa artykułu,Pojemność (ml),Sztuka/karton,Cena Netto(szt),VAT,Kod CN,PKWIU,Gramatura Netto,Gramatura Brutto\n")

        row_format = "\"%s\";\"%.0f\";\"%.0f\";\"%s\";\"%s\";\"%s\";\"%s\";\"%s\";\"%s\";\"%s\";\"%s\";\"%s\"\n"
        header_row = ("Kod dostawcy;Kod EAN;Kod EAN kartonu;Nazwa artykułu;Pojemność (ml);Sztuka/karton;Cena Netto(szt);VAT;Kod CN;PKWIU;Gramatura Netto;Gramatura Brutto\n")
        
        export = header_row.decode('utf-8').encode('cp1250')
        
        box_ean = 0
        
        for product in w.product_ids:
            for packaging in product.packaging:
                if packaging.ul_qty != 0:
                    if packaging.ul.name == 'Karton':
                        if packaging.ean_code != '':
                            box_ean = int(packaging.ean_code)
                        else:
                            box_ean = 0
            row = row_format % (product.nr_dostawcy_selgros,product.ean,box_ean,product.name,product.kod_eu_factor,product.order_ul.name,"CENA NETTO",product.vat_2010,product.kod_cn,product.pkwiu2008,product.weight_net,product.weight)
            export += row.encode('cp1250')
        
        return export
            
    def auchan(self, cr, uid, ids, context=None):
        #pdb.set_trace()
        w = self.browse(cr, uid, ids, context=context)[0]
        export = ''
        
        row_format = "\"%s\";\"%s\";\"%.0f\";\"%s\";\"%s\";\"%s\";\"%s\";\"%s\";\"%s\";\"%s\"\n"
        header_row = ("Kod dostawcy;Nazwa artykułu;Kod EAN;Jednostka miary;Jednostkowa pojemność produktu;Szt w kartonie (PCB);Szt na palecie (JK/JE);Termin przydatności (dni);VAT;PKWIU\n")
        
        export = header_row.decode('utf-8').encode('cp1250')
        
        box_qty = 0
        pal_qty = 0
        
        for product in w.product_ids:
            for packaging in product.packaging:
                if packaging.ul_qty != 0:
                    if packaging.ul.name == 'Karton':
                        box_qty = packaging.qty
                    elif packaging.ul.name == "Paleta":
                        pal_qty = packaging.qty
            row = row_format % (product.nr_dostawcy_auchan,product.name_30_auchan,product.ean,product.kod_eu_unit,product.kod_eu_factor,box_qty,pal_qty,product.shelf_life,product.vat_2010,product.pkwiu2008)
            export += row.encode('cp1250')
            
        return export
        
    def makro_real(self, cr, uid, ids, context=None):
        #pdb.set_trace()
        w = self.browse(cr, uid, ids, context=context)[0]
        export = ''
        
        row_format = "%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s\n"
        header_row = ("EAN Bazowy szt (zakupowy);EAN Jednostki (MU)(zakupowy);EAN Bazowy szt (sprzedażowy);EAN Jednostki sprzedaży (MU)(sprzedażowy);Numer dostawcy;Nazwa artukułu;Rodzaj(kolor/smak/kształt);Typ artykułu;Ilość szt w jednostce sprzedaży;Rodzaj opakowania;Stawka VAT zakupowa;Stawka VAT sprzedażowa;PKWiU;Kraj pochodzenia;Okres przydatności (cały);Okres przydatkości (gwarantowany);Kod CN;EU Factor;EU Unit;Wysokość szt;Szerokość szt;Głębokość szt;Wysokość palety;Ilość na warstwie;Ilość na palecie;Waga szt Netto;Waga szt Brutto;Temperatura min;Temperatura max;Zawartość alkoholu;Minimum zamówieniowe,Nazwa Marki Dostawcy\n")
        
        export = header_row.decode('utf-8').encode('cp1250')
        
        box_qty = 0
        pal_qty = 0
        pal_ul_qty = 0
        pal_height = 0
        
        for product in w.product_ids:
            for packaging in product.packaging:
                if packaging.ul_qty != 0:
                    if packaging.ul.name == 'Karton':
                        box_qty = packaging.qty
                    elif packaging.ul.name == "Paleta":
                        pal_qty = packaging.qty
                        pal_ul_qty = packaging.ul_qty
                        pal_height = packaging.height
            row = row_format % ("brak","brak","brak","brak",product.nr_dostawcy_makro_real,product.name,product.nr_dostawcy_makro_real,product.typ_artykulu,product.rodzaj_makro,product.pack_type.name,"brak","brak",product.pkwiu2008,product.origin_country.name,product.shelf_life,"brak",product.kod_cn,product.kod_eu_factor,product.kod_eu_unit,product.height/10,product.width/10,product.length/10,pal_height/10,pal_ul_qty*box_qty,pal_qty,product.weight_net*1000,product.weight,product.temp_min,product.temp_max,product.alcohol,"brak","brak")
            export += row.encode('cp1250')
            
        return export
            
    def carrefour(self, cr, uid, ids, context=None):
        #pdb.set_trace()
        w = self.browse(cr, uid, ids, context=context)[0]
        export = ''
        
        row_format = "%s%s%.0f;%s%s%s%s%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s\n"
        
        box_ean = 0
        box_qty = 0
        box_weight = 0
        box_width = 0
        box_height = 0
        box_length = 0
        pal_qty = 0
        pal_rows = 0
        pal_weight = 0
        pal_width = 0
        pal_height = 0
        pal_length = 0
        
        max_movex = 0
        movex_list = []
        movex_list_str = []
        
        for product in w.product_ids:
            movex = product.default_code
            if not movex:
                movex = ''
            if len(movex) > max_movex:
                max_movex = len(movex)
        
            movex_list.append(list(movex))
        
        for element in movex_list:
            z=0
            movex_str = ''
            while z<len(element):
                movex_str += (element[z] or '')+';'
                z+=1
            x=0
            if x<(max_movex-z+1):
                while x<(max_movex-z):
                    movex_str += ';'
                    x+=1
            else:
                movex_str += ';'
            if max_movex != 0:
                movex_list_str.append(movex_str)
            else:
                movex_list_str.append(';')
        i=1
        header_movex = ''
        while i<max_movex:
            i+=1
            header_movex += 'Kod MOVEX '+str(i)+';'
            
        max_pkwiu2008 = 0
        pkwiu2008_list = []
        pkwiu2008_list_str = []
        for product in w.product_ids:
            pkwiu2008 = product.pkwiu2008
            if not pkwiu2008:
                pkwiu2008 = ''
            #pdb.set_trace()
            if pkwiu2008:
                if len(pkwiu2008) > max_pkwiu2008:
                    max_pkwiu2008 = len(pkwiu2008)
            else:
                pkwiu2008 = ''
                
            pkwiu2008_list.append(list(pkwiu2008))
        
        for element in pkwiu2008_list:
            z=0
            pkwiu2008_str = ''
            while z<len(element):
                pkwiu2008_str += (element[z] or '')+';'
                z+=1
            x=0
            if x<(max_pkwiu2008-z+1):
                while x<(max_pkwiu2008-z):
                    pkwiu2008_str += ';'
                    x+=1
            else:
                pkwiu2008_str += ';'
            if max_pkwiu2008 != 0:
                pkwiu2008_list_str.append(pkwiu2008_str)
            else:
                pkwiu2008_list_str.append(';')
        i=1
        header_pkwiu2008 = ''
        while i<max_pkwiu2008:
            i+=1
            header_pkwiu2008 += 'Kod PKWiU 2008 ('+str(i)+');'
            
        max_pkwiu1997 = 0
        pkwiu1997_list = []
        pkwiu1997_list_str = []
        for product in w.product_ids:
            pkwiu1997 = product.pkwiu1997
            if not pkwiu1997:
                pkwiu1997 = ''
            #pdb.set_trace()
            if pkwiu1997:
                if len(pkwiu1997) > max_pkwiu1997:
                    max_pkwiu1997 = len(pkwiu1997)
            else:
                pkwiu1997 = ' '
                
            pkwiu1997_list.append(list(pkwiu1997))
        
        for element in pkwiu1997_list:
            z=0
            pkwiu1997_str = ''
            while z<len(element):
                pkwiu1997_str += (element[z] or '')+';'
                z+=1
            x=0
            if x<(max_pkwiu1997-z+1):
                while x<(max_pkwiu1997-z):
                    pkwiu1997_str += ';'
                    x+=1
            else:
                pkwiu1997_str += ';'
            if max_pkwiu1997 != 0:
                pkwiu1997_list_str.append(pkwiu1997_str)
            else:
                pkwiu1997_list_str.append(';')
        i=1
        header_pkwiu1997 = ''
        while i<max_pkwiu1997:
            i+=1
            header_pkwiu1997 += 'Kod PKWiU 1997 ('+str(i)+');'
            
        max_manufacturer = 0
        manufacturer_list = []
        manufacturer_list_str = []
        for product in w.product_ids:
            manufacturer = product.manufacturer_id.name
            #pdb.set_trace()
            if not manufacturer:
                manufacturer = ''
            if len(manufacturer) > max_manufacturer:
                max_manufacturer = len(manufacturer)
                
            manufacturer_list.append(list(manufacturer))
        
        for element in manufacturer_list:
            z=0
            manufacturer_str = ''
            while z<len(element):
                manufacturer_str += (element[z] or '')+';'
                z+=1
            x=0
            if x<(max_manufacturer-z+1):
                while x<(max_manufacturer-z):
                    manufacturer_str += ';'
                    x+=1
            else:
                manufacturer_str += ';'
            if max_manufacturer !=0:
                manufacturer_list_str.append(manufacturer_str)
            else:
                manufacturer_list_str.append(';')
        i=1
        header_manufacturer = ''
        while i<max_manufacturer:
            i+=1
            header_manufacturer += 'Nazwa dostawcy ('+str(i)+');'
            
        max_name = 0
        name_list = []
        name_list_str = []
        for product in w.product_ids:
            name = product.name_35_carrefour
            if not name:
                name = ''
            #pdb.set_trace()
            if name:
                if len(name) > max_name:
                    max_name = len(name)
            else:
                name = ''
                
            name_list.append(list(name))
        
        for element in name_list:
            z=0
            name_str = ''
            while z<len(element):
                name_str += (element[z] or '')+';'
                z+=1
            x=0
            if x<(max_name-z+1):
                while x<(max_name-z):
                    name_str += ';'
                    x+=1
            else:
                name_str += ';'
            if max_name != 0:
                name_list_str.append(name_str)
            else:
                name_list_str.append(';')
        i=1
        header_name = ''
        while i<max_name:
            i+=1
            header_name += 'Nazwa produktu ('+str(i)+');'
            
        max_box_ean = 0
        box_ean_list = []
        box_ean_list_str = []
        for product in w.product_ids:
            for packaging in product.packaging:
                if packaging.ul_qty != 0:
                    if packaging.ul.name == 'Karton':
                        if packaging.ean_code != '':
                            box_ean = packaging.ean_code
                        else:
                            box_ean = ''
            #pdb.set_trace()
            if box_ean:
                if len(box_ean) > max_box_ean:
                    max_box_ean = len(box_ean)
            else:
                box_ean = ''
                
            box_ean_list.append(list(box_ean))
        
        for element in box_ean_list:
            z=0
            box_ean_str = ''
            while z<len(element):
                box_ean_str += (element[z] or '')+';'
                z+=1
            x=0
            if x<(max_box_ean-z+1):
                while x<(max_box_ean-z):
                    box_ean_str += ';'
                    x+=1
            else:
                box_ean_str += ';'
            if max_box_ean != 0:
                box_ean_list_str.append(box_ean_str)
            else:
                box_ean_list_str.append(';')
        i=1
        header_box_ean = ''
        while i<max_box_ean:
            i+=1
            header_box_ean += 'EAN kartonu ('+str(i)+');'
            
        header_row = ("Nazwa dostawcy (1);%sNazwa produktu (1);%sEAN produktu;EAN kartonu (1);%sKod PKWiU 1997 (1);%sKod PKWiU 2008 (1);%sKod MOVEX (1);%sIlość szt w kartonie;Ilość szt na palecie;Ilość warstw na palecie;Waga szt brutto(kg);Waga szt netto(kg);Waga kartonu brutto(kg);Objętość kartonu(l);Waga palety brutto(kg);Objętość palety(l);Wysokość szt(cm);Szerokość szt (cm);Głębokość szt(cm);Wysokość kartonu(cm);Szerokość kartonu(cm);Głębokość kartonu(cm);Wysokość palety(cm);Szerokość palety(cm);Głębokość palety(cm);Termin przydatności(dni);Minimum zamówienia(szt);Stawka VAT do 2010;Stawka VAT od 2011;Cena cennikowa(bez VAT)\n") % (header_manufacturer,header_name,header_box_ean,header_pkwiu1997,header_pkwiu2008,header_movex)
        
        export = header_row.decode('utf-8').encode('cp1250')
        
        c=0
        for product in w.product_ids:
            for packaging in product.packaging:
                if packaging.ul_qty != 0:
                    if packaging.ul.name == 'Karton':
                        box_qty = packaging.qty
                        box_weight = packaging.weight
                        box_width = packaging.width
                        box_height = packaging.height
                        box_length = packaging.length
                    elif packaging.ul.name == "Paleta":
                        pal_qty = packaging.qty
                        pal_rows = packaging.rows
                        pal_weight = packaging.weight
                        pal_width = packaging.width
                        pal_height = packaging.height
                        pal_length = packaging.length
            row = row_format % (manufacturer_list_str[c],name_list_str[c],product.ean,box_ean_list_str[c],pkwiu1997_list_str[c],pkwiu2008_list_str[c],movex_list_str[c],box_qty,pal_qty,pal_rows,product.weight,product.weight_net,box_weight,(box_height*box_width*box_length)/1000,pal_weight,(pal_width*pal_height*pal_length)/1000,product.height,product.width,product.length,box_height,box_width,box_length,pal_height,pal_width,pal_length,product.shelf_life,"Brak",product.vat_2010,"Brak","Brak")
            #pdb.set_trace()
            export += row.encode('cp1250')
            c+=1
        return export
            
    def kaufland(self, cr, uid, ids, context=None):
        w = self.browse(cr, uid, ids, context=context)[0]
        export = ''
        
        row_format = "%s;%s;%s;%.0f;%.0f;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s\n"
        header_row = ("Dokładna nazwa artykułu;Kod dostawcy;Grupa EKG;EAN produktu;EAN kartonu;Ilość szt w kartonie;Ilość szt na warstwie;Ilość szt na palecie;Waga szt netto(kg)/objętość szt(l);Waga szt brutto(kg);Waga kartonu brutto(kg);Waga palety brutto (kg);Wysokość szt(cm);Szerokość szt (cm);Głębokość szt(cm);Wysokość kartonu(cm);Szerokość kartonu(cm);Głębokość kartonu(cm);Wysokość palety(cm);Szerokość palety(cm);Głębokość palety(cm);Pojemność artykułu;W przeliczeniu na ml;Rodzaj opakowania;Termin przydatności całkowity(dni);Termin przydatności od dnia dostawy(dni);Kod MOVEX;Kraj pochodzenia;Stawka VAT;Nr PKWiU;Typ etykiety;Źródło dostaw;Magazyn;Grupa warunków;Cena cennikowa (bez VAT);Etykieta regałowa 20;Etykieta regałowa 12;Etykieta regałowa 15;Sztuka\n")
        
        export = header_row.decode('utf-8').encode('cp1250')
        
        box_ean = 0
        box_qty = 0
        box_weight = 0
        box_width = 0
        box_height = 0
        box_length = 0
        pal_qty = 0
        pal_ul_qty = 0
        pal_weight = 0
        pal_width = 0
        pal_height = 0
        pal_length = 0
        
        for product in w.product_ids:
            for packaging in product.packaging:
                if packaging.ul_qty != 0:
                    if packaging.ul.name == 'Karton':
                        if packaging.ean_code != '':
                            box_ean = int(packaging.ean_code)
                        else:
                            box_ean = 0
                        box_qty = packaging.qty
                        box_weight = packaging.weight
                        box_width = packaging.width
                        box_height = packaging.height
                        box_length = packaging.length
                    elif packaging.ul.name == "Paleta":
                        pal_qty = packaging.qty
                        pal_ul_qty = packaging.ul_qty
                        pal_weight = packaging.weight
                        pal_width = packaging.width
                        pal_height = packaging.height
                        pal_length = packaging.length
            row = row_format % (product.name,product.nr_dostawcy_kaufland,product.grupa_ekg,product.ean,box_ean,box_qty,pal_ul_qty*box_qty,pal_qty,product.weight_net,product.weight,box_weight,pal_weight,product.height,product.width,product.length,box_height,box_width,box_length,pal_height,pal_width,pal_length,product.kod_eu_factor,product.kod_eu_factor,product.pack_type.name,product.shelf_life,product.shelf_life*0.75,product.default_code,product.origin_country.name,product.vat_2010,product.pkwiu2008,product.typ_etykiety,product.zrodlo_dostawy,product.magazyn,product.grupa_warunkow_kaufland,"BRAK",product.etykieta_regalowa_15,"BRAK","BRAK","BRAK")
            export += row.encode('cp1250')
            
        return export
              
    def leclerc(self, cr, uid, ids, context=None):
        #pdb.set_trace()
        w = self.browse(cr, uid, ids, context=context)[0]
        export = ''
        
        row_format = "%s;%.0f;%s;%s;%s;%s\n"
        
        box_qty = 0
        max_movex = 0
        movex_list = []
        movex_list_str = []
        
        for product in w.product_ids:
            movex = product.default_code
            if len(movex) > max_movex:
                max_movex = len(movex)
        
            movex_list.append(list(movex))
        
        for element in movex_list:
            z=0
            movex_str = ''
            while z<len(element):
                if len(element)-1 != z:
                    movex_str += (element[z] or '')+';'
                else:
                    movex_str += (element[z] or '')
                z+=1
            x=0
            while x<(max_movex-z):
                movex_str += ';'
                x+=1
            movex_list_str.append(movex_str)
        i=0
        header_movex = ''
        while i<max_movex:
            i+=1
            header_movex += 'Kod MOVEX '+str(i)+';'
            
        header_row = ("Nazwa artykułu;Kod EAN;%sIlość szt w kartonie;VAT;Cena cennikowa (bez VAT)\n") % (header_movex)
        
        #pdb.set_trace()
        
        export = header_row.decode('utf-8').encode('cp1250')
        c=0
        for product in w.product_ids:
            for packaging in product.packaging:
                if packaging.ul_qty != 0:
                    if packaging.ul.name == 'Karton':
                        box_qty = packaging.qty
            row = row_format % (product.name,product.ean,movex_list_str[c],box_qty,product.vat_2010,"BRAK")
            export += row.encode('cp1250')
            c+=1
        return export
            
    def tesco(self, cr, uid, ids, context=None):
        #pdb.set_trace()
        w = self.browse(cr, uid, ids, context=context)[0]
        export = ''
        
        row_format = "%s;%s;%s;%.0f;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s\n"
        header_row = ("Opis produktu;Kod PKWiU;Angielska nazwa produktu;Kod kreskowy;Kod wewnętrzny dostawcy (VPN);Stawka VAT;Cena zakupu szt;Cena zakupu kartonu;Sztuk w kartonie;Ilość kartonów na warstwie;Warstw na palecie;Kod kreskowy kartonu;Głębokość szt;Szerokość szt;Wysokość szt;Waga szt Netto;Waga szt Brutto;Głębokość Tray-packa;Szerokość Tray-packa;Wysokość Tray-packa;Głębokość Tray-packa;Szerokość Tray-packa;Wysokość Tray-packa;Głębokość kartonu;Szerokość kartonu;Wysokość kartonu;Waga kartonu Brutto;Waga kartonu Netto;Tolerancja wagi (%);Okres przydatności;Kod HTS\n")
        
        export = header_row.decode('utf-8').encode('cp1250')
        
        box_ean = 0
        box_qty = 0
        box_weight = 0
        box_width = 0
        box_height = 0
        box_length = 0
        pal_qty = 0
        pal_rows = 0
        
        for product in w.product_ids:
            for packaging in product.packaging:
                if packaging.ul_qty != 0:
                    if packaging.ul.name == 'Karton':
                        if packaging.ean_code != '':
                            box_ean = int(packaging.ean_code)
                        else:
                            box_ean = 0
                        box_qty = packaging.qty
                        box_weight = packaging.weight
                        box_width = packaging.width
                        box_height = packaging.height
                        box_length = packaging.length
                    elif packaging.ul.name == "Paleta":
                        pal_qty = packaging.ul_qty
                        pal_rows = packaging.rows
            row = row_format % (product.name,product.pkwiu2008,product.name_en,product.ean,"BRAK",product.vat_2010,"Brak","Brak",box_qty,pal_qty,pal_rows,box_ean,product.length,product.width,product.height,product.weight_net,product.weight,box_length,box_width,box_height,box_length,box_width,box_height,box_length,box_width,box_height,box_weight,"BRAK","BRAK",product.shelf_life,product.hts_code)
            export += row.encode('cp1250')
            
        return export
            
    def hebe(self, cr, uid, ids, context=None):
        #pdb.set_trace()
        w = self.browse(cr, uid, ids, context=context)[0]
        export = ''
        
        row_format = "%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%.0f;%.0f;%.0f;%s;%s;%s;%s;%s;%s;%s;%s\n"
        header_row = ("Nazwa handlowa(długa);Nazwa handlowa(krótka);Nazwa etykieta(1);Nazwa etykieta(2);Opis paragon;Podstawowa jed. miary;Waga/objętość(szt);Jednoska miary wagi/objętości;Jednostka;Cena cennikowa(szt);Ilość w kartonie;Wysokość kartonu;Szerokość kartonu;Długość kartonu;Ilość w Dispayu;Ilość na palecie;Kod EAN(szt);Kod EAN(Display);Kod EAN(kartonu);Index producenta;Producent;Marka;Submarka;VAT;Symbol PKWiU;Termin dostępności;Max. termin przydatności,Uwagi\n")
        
        export = header_row.decode('utf-8').encode('cp1250')
        
        box_ean = 0
        box_qty = 0
        box_width = 0
        box_height = 0
        box_length = 0
        pal_qty = 0
        bli_ean = 0
        bli_qty = 0
        
        for product in w.product_ids:
            #pdb.set_trace()
            for packaging in product.packaging:
                if packaging.ul_qty != 0:
                    if packaging.ul.name == 'Karton':
                        if packaging.ean_code != '':
                            box_ean = int(packaging.ean_code)
                        else:
                            box_ean = 0
                        box_qty = packaging.ul_qty
                        box_width = packaging.width
                        box_height = packaging.height
                        box_length = packaging.length
                    elif packaging.ul.name == "Paleta":
                        pal_qty = packaging.qty
                    elif packaging.ul.name == "Blister":
                        if packaging.ean_code != '':
                            bli_ean = int(packaging.ean_code)
                        else:
                            bli_ean = 0
                        bli_qty = packaging.ul_qty
                marka = ''
                submarka = ''
                submarka = product.product_tmpl_id.categ_id.name
                if product.product_tmpl_id.categ_id.parent_id:
                    marka = product.product_tmpl_id.categ_id.parent_id.name
                else:
                    marka = product.product_tmpl_id.categ_id.name
            row = row_format % (product.name,product.name_40,product.name_20_1,product.name_20_2,product.paragon_18,"sztuka",product.weight,"brak","kg","brak",box_qty,box_height,box_width,box_length,bli_qty,pal_qty,product.ean,bli_ean,box_ean,product.index_producenta_hebe,product.manufacturer_id.name,marka,submarka,product.vat_2010,product.pkwiu2008,product.availability_date,product.shelf_life)
            export += row.encode('cp1250')
            
        return export
            
    def cederroth_pl(self, cr, uid, ids, context=None):
        w = self.browse(cr, uid, ids, context=context)[0]
        export = ''
        
        row_format = "%s;%s;%s;%.0f;%.0f;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s\n"
        header_row = ("PKWiU;Kod produktu dostawcy;Dokładna nazwa produktu;Kod EAN produktu;Kod EAN opakowania zbiorczego;Cena zakupu producenta bez rabatu;VAT;Sugerowana cena sprzedaży brutto;Nazwa linii produktowej;Marka;Producent;Pojemność/waga Netto;Podstawowa jednostka miary;Wyskoność szt;Szerokość szt; Głębokość szt;Waga jednostkowa produktu Brotto;Wysokość kartonu;Szerokość kartonu;Głębokość kartonu;Waga opakowania zbiorczego Brutto;Ilość produktów w opakowaniu zbiorczym;Ilość opakowań zbiorczych na warstwie;Ilość warstw na palecie;Ilość opakowań zbiorczych na palecie;Ilość jednostek na palecie;Minimum logistyczne zamawianych produktów\n")
        
        export = header_row.decode('utf-8').encode('cp1250')
        
        box_ean = 0
        box_qty = 0
        box_width = 0
        box_height = 0
        box_length = 0
        pal_qty = 0
        pal_ul_qty = 0
        pal_rows = 0
        box_weight = 0
        
        for product in w.product_ids:
            for packaging in product.packaging:
                if packaging.ul_qty != 0:
                    if packaging.ul.name == 'Karton':
                        if packaging.ean_code != '':
                            box_ean = int(packaging.ean_code)
                        else:
                            box_ean = 0
                        box_qty = packaging.qty
                        box_weight = packaging.weight
                        box_width = packaging.width
                        box_height = packaging.height
                        box_length = packaging.length
                    elif packaging.ul.name == "Paleta":
                        pal_qty = packaging.qty
                        pal_ul_qty = packaging.ul_qty
                        pal_rows = packaging.rows
            marka = ''
            if product.product_tmpl_id.categ_id.parent_id:
                marka = product.product_tmpl_id.categ_id.parent_id.name
            else:
                marka = product.product_tmpl_id.categ_id.name
            manufacturer_name = product.manufacturer_id.name
            row = row_format % (product.pkwiu2008,
                                "BRAK",
                                product.name,
                                product.ean,
                                box_ean,
                                "BRAK",
                                product.vat_2010,
                                "BRAK",
                                product.name_20_1+product.name_20_2,
                                marka,
                                manufacturer_name,
                                product.weight_net,
                                product.kod_eu_unit,
                                product.height,
                                product.width,
                                product.length,
                                product.weight,
                                box_height,
                                box_width,
                                box_length,
                                box_weight,
                                box_qty,
                                pal_ul_qty,
                                pal_rows,
                                pal_ul_qty*pal_rows,
                                pal_qty,
                                "BRAK")
            export += row.encode('cp1250')
            
        return export

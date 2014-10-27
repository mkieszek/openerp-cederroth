from openerp.osv import fields, osv
from openerp.tools.translate import _
import pdb

class cd_config_settings(osv.osv):
    _name = 'cd.config.settings'
    _inherit = 'res.config.settings'

    _columns = {
            'cd_www': fields.char('Cederroth www'),
            'cd_crm': fields.char('Cederroth CRM'),
            'min_margin_prom': fields.float("Akcji promocyjnej"),
            'plan_prom': fields.integer("Akcji promocyjnej"),
            'start_sale': fields.integer("Start Plan sprzed"),
            'stop_sale': fields.integer("Stop Plan sprzed"),
            'start_mark': fields.integer("Start Plan marketing"),
            'stop_mark': fields.integer("Stop Plan marketing"),
            'info_guardian': fields.integer("Informacja dla Opiekuna", help="Na ile dni przed rozpoczeciem rabatu Akcji Promocyjnej ma zostac poinformowany opiekun klienta"),
    }
    
    def default_get(self, cr, uid, fields, context=None):
        res = super(cd_config_settings, self).default_get(cr, uid, fields, context)
        config_id = self.search(cr, uid, [])
        if config_id:
            res['cd_www'] = self.browse(cr, uid, config_id[-1]).cd_www
            res['cd_crm']= self.browse(cr, uid, config_id[-1]).cd_crm
            res['min_margin_prom'] = self.browse(cr, uid, config_id[-1]).min_margin_prom
            res['start_sale']= self.browse(cr, uid, config_id[-1]).start_sale
            res['stop_sale']= self.browse(cr, uid, config_id[-1]).stop_sale
            res['start_mark']= self.browse(cr, uid, config_id[-1]).start_mark
            res['stop_mark']= self.browse(cr, uid, config_id[-1]).stop_mark
            res['plan_prom']= self.browse(cr, uid, config_id[-1]).plan_prom
            res['info_guardian']= self.browse(cr, uid, config_id[-1]).info_guardian
        return res
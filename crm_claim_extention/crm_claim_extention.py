# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
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

import openerp
from openerp.addons.crm import crm
from openerp.osv import fields, osv
from openerp import tools
from openerp.tools.translate import _
from openerp.tools import html2plaintext
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)

AVAILABLE_ACTIONS = [
        ('correction','Corrective Action'),
        ('prevention','Preventive Action'),
        ('replace','Replace Action'),    # New option
        ('discard','Discard Action'),    # New option
    ]

class crm_claim(osv.osv):
    _name = "crm.claim"
    _inherit = "crm.claim"
    _columns = {
        'origin': fields.char('Origin',size=30,readonly=True),
        'products_id': fields.many2many('product.product', 'crm_claim_products', 'crm_claim_id', 'product_id', 'Productos', track_visibility='onchange'),
        'invoice_id': fields.many2many('account.invoice', 'crm_claim_invoice', 'crm_claim_id', 'invoice_id', 'Facturas', track_visibility='onchange'),
        'invoice_line_id': fields.many2many('account.invoice.line', 'crm_claim_invoice_line', 'crm_claim_id', 'invoice_line_id', 'Productos', track_visibility='onchange',domain="[('invoice_id', '=', invoice_id)]"),
        'has_check_solution': fields.boolean('has check soluction',readonly=True),
        'number_id': fields.char('Number', size=64, select=True),
        'type_action': fields.selection(AVAILABLE_ACTIONS, 'Action Type',readonly=True),    # Override required and selections
        'type_id': fields.many2one('crm.claim.type', 'Type'),


        #'product_id' : fields.Many2one('product.product'),
        #'ref': fields.reference('Reference', selection=openerp.addons.base.res.res_request.referencable_models),

    }
    _defaults = {
        'origin': lambda self, cr, uid, context: 'self',
        'number_id': lambda self, cr, uid, context: '/',
    }
    _sql_constraints = [
            ('uniq_number', 'unique(number, company_id)', "The Number must be unique per Company"),
        ]    
    def create(self, cr, uid, vals, context=None):
        if not 'number_id' in vals or vals['number_id'] == '/':
            if not 'origin' in vals :
                vals['origin'] = 'self'
            vals['number_id'] = vals['origin'] +  str(self.pool.get('ir.sequence').get(cr, uid, 'crm.claim'))
            #vals['number_id'] = vals['origin'] +  str(self.pool.get('ir.sequence').get(cr, uid, 'crm.claim'))
        return super(crm_claim, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):

        if 'stage_id' in vals:
            clm_stg = self.pool.get('crm.claim.stage')
            stage=clm_stg.read(cr, uid, vals['stage_id'], ['user_id','day_to_action_next','action_next','days_to_date_deadline'])

            if 'action_next' in stage and stage['action_next']:
                vals['action_next']=stage['action_next']
                vals['date_action_next']=datetime.today()+timedelta(days=int(stage['day_to_action_next']))
                vals['user_id']=stage['user_id'][0]
            if 'days_to_date_deadline' in stage and stage['days_to_date_deadline']:
                vals['date_deadline']=datetime.today()+timedelta(days=int(stage['days_to_date_deadline']))







        return super(crm_claim, self).write(cr, uid, ids, vals, context=context)


    def onchange_invoice_id(self, cr, uid, ids, invoice_id,  context=None):
        _logger.info("filoquin ----- domain  : %r", invoice_id)
        all_ids=[]
        if invoice_id ==   [[6, False, []]]:
            return {'value': {'email_from': False, 'partner_phone': 'sin xx'} ,'domain' :{'invoice_line_id':[('invoice_id','=',[0])]}}
       
        values = self.resolve_2many_commands(cr, uid, 'invoice_id', invoice_id, ['crm_claim_id', 'invoice_id'], context)
        if len(values)<1 :
            return {'value': {'email_from': False, 'partner_phone': 'sin datos'}}


        #if len(values)>1 :
            #all_ids.append('|')

        for item in values:
            _logger.info("my variable : %r", item['id'])
            #all_ids.append(('invoice_id','=',item['id']))
            all_ids.append(item['id'])


        invoice = self.pool.get('account.invoice').browse(cr, uid, values[0]['id'], context=context)
        _logger.info("todas : %r", all_ids)

        return {'value': {'partner_id': invoice.partner_id.id, 'email_from': invoice.partner_id.email, 'partner_phone': invoice.partner_id.phone},'domain' :{'invoice_line_id':[('invoice_id','in',all_ids)]}}
        


    def copy(self, cr, uid, _id, default={}, context=None):
        default.update({
                'number_id': self.pool.get('ir.sequence').get(cr, uid, 'crm.claim'),
            })
        return super(crm_claim, self).copy(cr, uid, _id, default, context)

crm_claim()


class crm_claim_stage(osv.osv):
    _name = "crm.claim.stage"
    _inherit = "crm.claim.stage"
    _columns = {
        'user_id': fields.many2one('res.users', 'Responsible', track_visibility='always'),
        'day_to_action_next': fields.integer('Days to next action'),
        'action_next': fields.char('Next Action'),
        'days_to_date_deadline': fields.char('Date to deadline'),
    }
    _defaults = {
        'day_next_action': lambda self, cr, uid, context: '7',
    }
crm_claim_stage()


class crm_claim_type(osv.osv):
    """ Type of Claim """
    _name = "crm.claim.type"
    _description = "Type of Claim"
    _columns = {
        'name': fields.char('Name', required=True, translate=True),
        'parent_id': fields.many2one('crm.claim.type', 'Type of claim', required=False, ondelete='cascade',
            help="Claim type."),
    }

    """def _find_object_id(self, cr, uid, context=None):
        context = context or {}
        object_id = context.get('object_id', False)
        ids = self.pool.get('ir.model').search(cr, uid, ['|', ('id', '=', object_id), ('model', '=', context.get('object_name', False))])
        return ids and ids[0] or False
    _defaults = {
        'object_id': _find_object_id
    }"""



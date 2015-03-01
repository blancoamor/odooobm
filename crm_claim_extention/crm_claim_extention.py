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
        'products_id': fields.many2many('product.product', 'crm_claim_products', 'crm_claim_id', 'product_id', 'Productos'),
        'has_check_solution': fields.boolean('has check soluction',readonly=True),
        'number_id': fields.char('Number', size=64, select=True),
        'type_action': fields.selection(AVAILABLE_ACTIONS, 'Action Type',readonly=True),    # Override required and selections
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
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
from openerp.osv import fields, osv , models
from openerp import tools
from openerp.tools.translate import _


class Configuration(osv.TransientModel):
    _name = 'pw.connect.config.settings'
    _inherit = 'res.config.settings'

    pw_connect_url = fields.Char(
        string='Url for connection',
        required=True,
        help="Path",
        default_model='pw.connect.config.settings',
    )
    pw_connect_user = fields.Char(
        string='User for connection',
        required=True,
        help="User db",
        default_model='pw.connect.config.settings',
    )
    pw_connect_password = fields.Char(
        string='password for connection',
        required=True,
        help="pass",
        default_model='pw.connect.config.settings',
    )

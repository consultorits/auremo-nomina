# -*- coding: utf-8 -*-
# Part of SysNeo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError, ValidationError

class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"

    apply_commission = fields.Boolean('Aplica Comisión')

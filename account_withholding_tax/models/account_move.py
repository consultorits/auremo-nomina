# -*- coding: utf-8 -*-
# Part of SysNeo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError, ValidationError

class AccountInvoice(models.Model):
    _inherit = 'account.move'

    withholding_id = fields.Many2one('account.withholding', string="Retención", copy=False, readonly=True, states={'draft': [('readonly', False)]})
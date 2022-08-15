# -*- coding: utf-8 -*-
# Part of SysNeo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError, ValidationError

class AccountMove(models.Model):
    _inherit = "account.move"

    amount_change = fields.Monetary(currency_field='currency_id', string="Cambio")

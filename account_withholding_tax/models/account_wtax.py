# -*- coding: utf-8 -*-
# Part of SysNeo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, exceptions, fields, models

class AccountWtax(models.Model):
    _name = 'account.wtax'
    _description = "Withholding tax"
    _order = 'name desc, id desc'

    name = fields.Char(
        string='Nombre', 
        required=True, 
    )

    code = fields.Char(
        string='Código', 
        required=True, 
    )

    account_id = fields.Many2one(
        comodel_name='account.account', 
        string='Cuenta',
        ondelete="restrict", 
        domain=[('deprecated', '=', False)],
        required=True,
    )

    rate = fields.Float(
        string='Ratio (%)', 
        required=True, 
    )
    company_id = fields.Many2one(
        comodel_name='res.company', 
        string='Company', 
        required=True, 
        index=True, 
        default=lambda self: self.env.company
    )
# -*- coding: utf-8 -*-
# Part of SysNeo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _, fields
from odoo.exceptions import ValidationError


class Users(models.Model):
    _inherit = "res.users"

    location_ids = fields.Many2many('stock.location', string="Ubicaciones Permitidas")

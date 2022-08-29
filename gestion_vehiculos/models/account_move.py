# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    vehiculos = fields.Many2many('gestion_vehiculos.gestion_vehiculos', string="Vehículos")
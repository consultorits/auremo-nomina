# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SecuenciaFiscal(models.Model):
    _inherit = 'ir.sequence'

    l10n_hn_cai = fields.Char(string="CAI")
    l10n_hn_correlativo_fiscal_inicial = fields.Integer(string="Rango Inicial")
    l10n_hn_correlativo_fiscal_final = fields.Integer(string="Rango Final")
    l10n_hn_fecha_inicial_emision = fields.Date(string="Fecha recepción")
    l10n_hn_fecha_final_emision = fields.Date(string="Fecha final emisión")
    l10n_hn_activo = fields.Boolean(string="Secuencia SAR", default=False)
    l10n_hn_fiscal_compras = fields.Boolean(string="Fiscal compras", default=False)
    l10n_hn_correlativo_fiscal_inicial_str = fields.Char(string="Correlativo fiscal str inicial", compute='get_range')
    l10n_hn_correlativo_fiscal_final_str = fields.Char(string="Correlativo fiscal str final", compute='get_range')

    def get_range(self):
        if self.l10n_hn_correlativo_fiscal_inicial:
            self.l10n_hn_correlativo_fiscal_inicial_str = str(self.prefix) + str(self.l10n_hn_correlativo_fiscal_inicial).zfill(8)
        if self.l10n_hn_correlativo_fiscal_final:
            self.l10n_hn_correlativo_fiscal_final_str = str(self.prefix) + str(self.l10n_hn_correlativo_fiscal_final).zfill(8)
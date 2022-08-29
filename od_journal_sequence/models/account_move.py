# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    def _monto_en_letras(self):
        for rec in self:
            rec.l10n_hn_monto_en_letras = str(rec.currency_id.amount_to_text(rec.amount_total)) + ' ***'

    def _monto_en_letras_signed(self):
        for rec in self:
            rec.l10n_hn_monto_en_letras_signed = str(rec.company_id.currency_id.amount_to_text(rec.amount_total_signed)) + ' ***'

    name = fields.Char(string='Numero', required=True, readonly=True, copy=False, default='/')
    invoice_date =fields.Date(default=datetime.today())
    l10n_hn_monto_en_letras = fields.Char(string="Monto en letras", compute="_monto_en_letras")
    l10n_hn_monto_en_letras_signed = fields.Char(string="Monto en letras L", compute="_monto_en_letras_signed")
    l10n_hn_cai = fields.Char(string="CAI")
    l10n_hn_correlativo_fiscal_inicial = fields.Char(string="Rango Inicial")
    l10n_hn_correlativo_fiscal_final = fields.Char(string="Rango Final")
    l10n_hn_fecha_inicial_emision = fields.Date(string="Fecha recepción")
    l10n_hn_fecha_final_emision = fields.Date(string="Fecha final emisión")
    l10n_hn_sag = fields.Char(string="Registro Sag")
    l10n_hn_orden_exenta = fields.Char(string="Orden de compra exenta")
    l10n_hn_constancia_exonerada = fields.Char(string="Constancia registro exonerada")
    partner_id_vat = fields.Char(related='partner_id.vat', string='VAT No')
    sequence_generated = fields.Boolean(string="Sequence Generated", copy=False)
    
    def _constrains_date_sequence(self):
        for record in self:
            if not record.journal_id.sequence_id:
                return super(AccountMove, self)._constrains_date_sequence()
            else:
                pass
            
    def validar_diario_fiscal(self):
        for move in self:
            # fiscal = move.journal_id.sequence_id
            fiscal = move._get_sequence()
            if fiscal.l10n_hn_activo:
                if not self.invoice_date:
                    raise UserError(_('Ingresar la fecha de la factura por favor'))
                if self.invoice_date > fiscal.l10n_hn_fecha_final_emision:
                    raise UserError(_('Fecha fiscal vencida %s ') % (fiscal.l10n_hn_fecha_final_emision))
                if self.invoice_date < fiscal.l10n_hn_fecha_inicial_emision:
                    raise UserError(_('Fecha fiscal fuera de rango %s ') % (fiscal.l10n_hn_fecha_inicial_emision))
                    
                # se usa la secucuencia de factura o nota de credito para obtener la proxima secuencia a evaluar.
                sequence_number_next = self.journal_id.sequence_number_next
                if self.move_type == 'out_refund':
                    sequence_number_next = fiscal.number_next_actual
                    
                if sequence_number_next > fiscal.l10n_hn_correlativo_fiscal_final:
                    # _logger.error("proxima secuancia %s, %s, tipo factura %s", sequence_number_next, fiscal.l10n_hn_correlativo_fiscal_final, self.move_type)
                    raise UserError(_('correlativo fiscal fuera de rango %s ') % (fiscal.l10n_hn_correlativo_fiscal_final))
                if sequence_number_next < fiscal.l10n_hn_correlativo_fiscal_inicial:
                    raise UserError(_('correlativo fiscal debe ser mayor al correlativo inicials %s ') % (fiscal.l10n_hn_correlativo_fiscal_inicial))

                self.l10n_hn_cai = fiscal.l10n_hn_cai
                self.l10n_hn_correlativo_fiscal_inicial = fiscal.l10n_hn_correlativo_fiscal_inicial_str
                self.l10n_hn_correlativo_fiscal_final = fiscal.l10n_hn_correlativo_fiscal_final_str
                self.l10n_hn_fecha_inicial_emision = fiscal.l10n_hn_fecha_inicial_emision
                self.l10n_hn_fecha_final_emision = fiscal.l10n_hn_fecha_final_emision

    @api.depends('posted_before', 'state', 'journal_id', 'date')
    def _compute_name(self):
        for move in self:
            if not move.journal_id.sequence_id:
                _logger.error("secuencia mixin sequence_id %s", move.journal_id)
                return super(AccountMove, self)._compute_name()
            sequence_id = move._get_sequence()
            _logger.error("secuencia sequence_id %s", sequence_id)
            if not sequence_id:
                raise UserError('Please define a sequence on your journal.')
            if not move.sequence_generated and move.state == 'draft':
                move.name = '/'
            elif not move.sequence_generated and move.state != 'draft':
                sequence_date = move.date or move.invoice_date
                move.validar_diario_fiscal()
                move.name = sequence_id.with_context(ir_sequence_date=sequence_date).next_by_id(sequence_date)
                move.sequence_generated = True
                
    def _get_sequence(self):
        self.ensure_one()
        journal = self.journal_id
        if self.move_type in ('entry', 'out_invoice', 'in_invoice', 'out_receipt', 'in_receipt') or not journal.refund_sequence:
            return journal.sequence_id
        if not journal.refund_sequence_id:
            return
        return journal.refund_sequence_id

    # def _post(self, soft=True):
    #     for move in self:
    #         if move.name == '/' or move.name == '' or move.name == ' ':
    #             sequence = move._get_sequence()
    #             if not sequence:
    #                 raise UserError(_('Please define a sequence on your journal.'))
    #             for fiscal in self.journal_id.sequence_id:
    #                 if fiscal.l10n_hn_activo:
    #                     if not self.invoice_date:
    #                         raise UserError(_('Ingresar la fecha de la factura por favor'))
    #                     if self.invoice_date > fiscal.l10n_hn_fecha_final_emision:
    #                         raise UserError(_('Fecha fiscal vencida %s ') % (fiscal.l10n_hn_fecha_final_emision))
    #                     if self.invoice_date < fiscal.l10n_hn_fecha_inicial_emision:
    #                         raise UserError(_('Fecha fiscal fuera de rango %s ') % (fiscal.l10n_hn_fecha_inicial_emision))
    #                     if self.journal_id.sequence_number_next > fiscal.l10n_hn_correlativo_fiscal_final:
    #                         raise UserError(_('correlativo fiscal vencido %s ') % (fiscal.l10n_hn_correlativo_fiscal_final))
    #                     if self.journal_id.sequence_number_next < fiscal.l10n_hn_correlativo_fiscal_inicial:
    #                         raise UserError(_('correlativo fiscal vencido %s ') % (fiscal.l10n_hn_correlativo_fiscal_inicial))

    #                     self.l10n_hn_cai = fiscal.l10n_hn_cai
    #                     self.l10n_hn_correlativo_fiscal_inicial = fiscal.l10n_hn_correlativo_fiscal_inicial_str
    #                     self.l10n_hn_correlativo_fiscal_final = fiscal.l10n_hn_correlativo_fiscal_final_str
    #                     self.l10n_hn_fecha_inicial_emision = fiscal.l10n_hn_fecha_inicial_emision
    #                     self.l10n_hn_fecha_final_emision = fiscal.l10n_hn_fecha_final_emision
    #             move.name = sequence.with_context(ir_sequence_date=move.date).next_by_id()
    #     res = super(AccountMove, self)._post(soft=True)
    #     return res
    
    
    class SequenceMixin2(models.AbstractModel):
        _inherit = 'sequence.mixin'
        
        def _constrains_date_sequence(self):
            constraint_date = fields.Date.to_date(self.env['ir.config_parameter'].sudo().get_param(
                'sequence.mixin.constraint_start_date',
                '1970-01-01'
            ))
            for record in self:
                date = fields.Date.to_date(record[record._sequence_date_field])
                sequence = record[record._sequence_field]
                if sequence and date and date > constraint_date:
                    format_values = record._get_sequence_format_param(sequence)[1]


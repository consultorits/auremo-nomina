# -*- coding: utf-8 -*-
# Part of SysNeo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    amount_change = fields.Monetary(currency_field='currency_id', store=True,
        compute='_compute_amount_change', string="Cambio")
    amount_received = fields.Monetary(currency_field='currency_id', string="Monto Recibido")
    journal_type = fields.Selection(related="journal_id.type", string="Tipo Diario")

    @api.depends('amount_received','amount','journal_id')
    def _compute_amount_change(self):
        for rec in self:
            if rec.journal_id.type == 'cash' and rec.amount_received > 0.0:
                rec.amount_change = rec.amount_received - rec.amount
            else:
                rec.amount_change = 0.0
                rec.amount_received = 0.0

    def _create_payments(self):
        payments = super(AccountPaymentRegister, self)._create_payments()
        if self._context.get('active_model') == 'account.move':
            invoice = self.env['account.move'].browse(self._context.get('active_ids', []))
            invoice.amount_change = self.amount_change
        return payments

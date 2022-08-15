# -*- coding: utf-8 -*-
# Part of SysNeo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError, ValidationError

import json

class AccountWithholding(models.Model):
    _name = 'account.withholding'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Withholding tax"
    _order = 'date desc, name desc, id desc'
    _mail_post_access = 'read'

    @api.model
    def _get_default_journal(self):
        journal_type = 'general'
        company_id = self._context.get('force_company', self._context.get('default_company_id', self.env.company.id))
        domain = [('company_id', '=', company_id), ('type', '=', journal_type)]
        journal = self.env['account.journal'].search(domain, limit=1)

        if not journal:
            error_msg = _('Please define an accounting miscellaneous journal in your company')
            raise UserError(error_msg)
        return journal
    
    def _get_default_currency(self):
        ''' Get the default currency from either the journal, either the default journal's company. '''
        journal = self._get_default_journal()
        return journal.currency_id or journal.company_id.currency_id

    @api.depends('line_ids.wtax_amount')
    def _compute_wtax_tamount(self):
        for rec in self:
            rec.wtax_tamount = sum([l.wtax_amount for l in rec.line_ids])

    company_id = fields.Many2one(
        comodel_name='res.company', 
        string='Company', 
        required=True, 
        index=True, 
        default=lambda self: self.env.company
    )

    name = fields.Char(
        string='Number', 
        required=True, 
        readonly=True, 
        copy=False, 
        default='/'
    )

    partner_id = fields.Many2one(
        comodel_name='res.partner', 
        readonly=True, 
        tracking=True,
        states={'draft': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        string='Proveedor', 
        change_default=True
    )

    ref = fields.Char(
        string="Referencia",
        copy=False,
    )

    tax_id = fields.Char(
        string="NIF",
        related="partner_id.vat",
        store=True,
    )

    date = fields.Date(
        string='Fecha', 
        required=True, 
        index=True, 
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=fields.Date.context_today
    )

    account_date = fields.Date(
        string="Fecha contable",
        index=True, 
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    state = fields.Selection(
        selection=[
            ('draft', 'Borrador'),
            ('posted', 'Publicado'),
            ('cancel', 'Cancelado')
        ], 
        string='Estado', 
        required=True, 
        readonly=True, 
        copy=False, 
        tracking=True,
        default='draft'
    )

    journal_id = fields.Many2one(
        comodel_name='account.journal', 
        string='Diario', 
        readonly=True,
        states={'draft': [('readonly', False)]},
        domain="[('company_id', '=', company_id)]",
        default=_get_default_journal
    )

    user_id = fields.Many2one('res.users', copy=False, tracking=True,
        string='Usuario',
        default=lambda self: self.env.user
    )

    company_currency_id = fields.Many2one(
        string='Company Currency', 
        readonly=True,
        related='company_id.currency_id'
    )

    currency_id = fields.Many2one(
        comodel_name='res.currency', 
        store=True, 
        readonly=True, 
        tracking=True, 
        required=True,
        states={'draft': [('readonly', False)]},
        string='Moneda',
        default=_get_default_currency
    )

    line_ids = fields.One2many(
        comodel_name='account.withholding.line', 
        inverse_name='withholding_id', 
        string='Facturas', 
        copy=True, 
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    wtax_tamount = fields.Monetary(
        string='Monto Total Retención',
        currency_field='currency_id',
        store=True, 
        readonly=True, 
        compute='_compute_wtax_tamount'
    )

    narration = fields.Text(
        string="Notas",
    )

    move_count = fields.Integer(compute="_compute_moves", string='Move Count', copy=False, default=0, store=True)

    move_ids = fields.Many2many('account.move', compute="_compute_moves", string='Asientos contables', copy=False, store=True)

    wtax_widget = fields.Text(compute='_compute_wtax_widget_info')
    # Datos fiscales
    l10n_hn_cai = fields.Char(string="CAI", readonly=True, states={'draft': [('readonly', False)]})
    l10n_hn_correlativo_fiscal_inicial = fields.Char(string="Rango Inicial", readonly=True, states={'draft': [('readonly', False)]})
    l10n_hn_correlativo_fiscal_final = fields.Char(string="Rango Final", readonly=True, states={'draft': [('readonly', False)]})
    l10n_hn_fecha_inicial_emision = fields.Date(string="Fecha recepción", readonly=True, states={'draft': [('readonly', False)]})
    l10n_hn_fecha_final_emision = fields.Date(string="Fecha final emisión", readonly=True, states={'draft': [('readonly', False)]})
    
    def copiar_datos_fiscales(self):
        fiscal = self.journal_id.whsequence_id
        if fiscal.l10n_hn_activo:
            if not self.date:
                raise UserError(_('Ingresar la fecha de la factura por favor'))
            if self.date > fiscal.l10n_hn_fecha_final_emision:
                raise UserError(_('Fecha fiscal vencida %s ') % (fiscal.l10n_hn_fecha_final_emision))
            if self.date < fiscal.l10n_hn_fecha_inicial_emision:
                raise UserError(_('Fecha fiscal fuera de rango %s ') % (fiscal.l10n_hn_fecha_inicial_emision))
            if fiscal.number_next_actual > fiscal.l10n_hn_correlativo_fiscal_final:
                raise UserError(_('correlativo fiscal vencido %s ') % (fiscal.l10n_hn_correlativo_fiscal_final))
            if fiscal.number_next_actual < fiscal.l10n_hn_correlativo_fiscal_inicial:
                raise UserError(_('correlativo fiscal vencido %s ') % (fiscal.l10n_hn_correlativo_fiscal_inicial))

            self.l10n_hn_cai = fiscal.l10n_hn_cai
            self.l10n_hn_correlativo_fiscal_inicial = fiscal.l10n_hn_correlativo_fiscal_inicial_str
            self.l10n_hn_correlativo_fiscal_final = fiscal.l10n_hn_correlativo_fiscal_final_str
            self.l10n_hn_fecha_inicial_emision = fiscal.l10n_hn_fecha_inicial_emision
            self.l10n_hn_fecha_final_emision = fiscal.l10n_hn_fecha_final_emision

    def _compute_wtax_widget_info(self):
        for rec in self:
            rec.wtax_widget = json.dumps(False)

            #pay_term_line_ids = rec.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
            whtax_ids = rec.line_ids.mapped('wtax_id')
            lines = []
            for wtax in whtax_ids:
                monto = sum([l.wtax_amount for l in rec.line_ids.filtered(lambda r: r.wtax_id == wtax)])
                lines.append({'whtax': wtax, 'amount': monto})

            info = {'title': 'Resumen', 'content': []}
            currency_id = rec.currency_id

            if len(lines) != 0:
                for line in lines:
                    info['content'].append({
                        'whtax_name': line.get('whtax').name,
                        'amount': line.get('amount'),
                        'currency': currency_id.symbol,
                        'position': currency_id.position,
                        'digits': [69, currency_id.decimal_places],
                        'whtax_date': fields.Date.to_string(rec.account_date),
                    })
                info['title'] = "Resumen"
                rec.wtax_widget = json.dumps(info)

    @api.depends('line_ids.move_id')
    def _compute_moves(self):
        for rec in self:
            moves = rec.mapped('line_ids.move_id')
            rec.move_ids = moves
            rec.move_count = len(moves)

    def apply_validation(self):
        if not self.journal_id:
            raise UserError("Usted debe definir el diario para los asientos de retención")
        if not self.journal_id.whsequence_id:
            raise UserError("Usted debe definir la secuencia de retenciones en el diario seleccionado")

    def action_post(self):
        for rec in self:
            rec.apply_validation()
            rec.account_date = fields.Date.context_today(rec)
            rec.line_ids.mapped(lambda r: r.create_account_move())
            rec.state = 'posted'
            rec.name = rec.journal_id.whsequence_id.with_context(ir_sequence_date=rec.account_date).next_by_id()
            rec.copiar_datos_fiscales()

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'
            rec.line_ids.mapped(lambda r: r.move_id.sudo().button_draft())
            rec.line_ids.mapped(lambda r: r.move_id.sudo().with_context(force_delete=True).unlink())
            rec.line_ids.write({'base_amount':0.0, 'wtax_amount': 0.0})
            rec.wtax_tamount = 0.0

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

class AccountWithholdingLine(models.Model):
    _name = "account.withholding.line"
    _description = "Withholding Item"
    _order = "date desc, withholding_name desc, id"
    _check_company_auto = True
    
    withholding_id = fields.Many2one(
        comodel_name='account.withholding', 
        string='Retención',
        index=True, 
        required=True, readonly=True, 
        auto_join=True, 
        ondelete="cascade",
        help="The Withholding line."
    )
    
    withholding_name = fields.Char(
        string='Nombre Retención', 
        related='withholding_id.name', 
        store=True, 
        index=True
    )
    
    date = fields.Date(
        string="Fecha",
        related='withholding_id.date', 
        store=True, 
        copy=False, 
        group_operator='min'
    )

    account_date = fields.Date(
        string="Fecha contable",
        related='withholding_id.account_date', 
        index=True, 
        readonly=True,
        store=True, 
    )
    
    ref = fields.Char(
        related='withholding_id.ref', 
        store=True, 
        copy=False, 
        index=True, 
        readonly=False
    )
    
    parent_state = fields.Selection(
        related='withholding_id.state', 
        store=True, 
        readonly=True
    )
    
    journal_id = fields.Many2one(
        related='withholding_id.journal_id', 
        store=True, 
        index=True, 
        copy=False
    )
    
    company_id = fields.Many2one(
        related='withholding_id.company_id', 
        store=True, 
        readonly=True
    )
    
    currency_id = fields.Many2one(
        related='invoice_id.currency_id', 
        string='Company Currency',
        store=True,
    )
    
    company_currency_id = fields.Many2one(
        related='company_id.currency_id', 
        string='Company Currency',
        store=True,
    )
    
    account_id = fields.Many2one(
        comodel_name='account.account', 
        string='Cuenta',
        index=True, 
        ondelete="restrict", 
        check_company=True,
        domain=[('deprecated', '=', False)]
    )

    invoice_id = fields.Many2one(
        comodel_name='account.move', 
        string='Factura',
        required=True, 
    )

    invoice_name = fields.Char(
        related="invoice_id.name",
        string='#Factura', 
        store=True,
    )

    invoice_ref = fields.Char(
        related="invoice_id.ref",
        string='Referencia', 
        store=True,
    )
    
    base_amount = fields.Monetary(
        string='Monto base',
        currency_field='currency_id'
    )

    wtax_id = fields.Many2one(
        comodel_name='account.wtax', 
        string='Nombre Retención', 
    )

    wtax_code = fields.Char(
        related="wtax_id.code",
        string='Código Retención', 
        store=True,
    )
    
    wtax_amount = fields.Monetary(
        string='Monto Retención',
        currency_field='currency_id',
        readonly=True,
    )

    wtax_rate = fields.Float(
        string='Ratio Retención',
    )

    move_id = fields.Many2one(
        comodel_name='account.move',
        string='Asiento contable',
    )

    partner_id = fields.Many2one(
        related='withholding_id.partner_id', 
        string='Proveedor',
        store=True,
    )

    tax_id = fields.Char(
        string="NIF",
        related="partner_id.vat",
        store=True,
    )

    _sql_constraints = [
        ('wtax_invoice_uniq', 'unique (withholding_id, wtax_id, invoice_id, company_id)', 'La retención y la factura debe ser único por documento de retención !'),
    ]

    @api.onchange('invoice_id')
    def onchange_invoicewtax_id(self):
        self.base_amount = self.invoice_id.amount_untaxed

    @api.onchange('wtax_id')
    def onchange_wtax_id(self):
        self.wtax_rate = self.wtax_id.rate
        self.account_id = self.wtax_id.account_id

    @api.onchange('wtax_rate','base_amount')
    def _onchange_wtax_amount(self):
        for line in self:
            line.update({'wtax_amount':self.base_amount * self.wtax_rate/100})

    def _prepare_wtholding_moves(self):
        rec = self
        ref = '%s - %s'%(rec.wtax_id.name, rec.invoice_id.name)
        company_currency = rec.company_id.currency_id

        # Compute amounts.
        counterpart_amount = rec.wtax_amount

        # Manage currency.
        if rec.currency_id == company_currency:
            # Single-currency.
            balance = counterpart_amount
            counterpart_amount = 0.0
            currency_id = False

        else:
            # Multi-currencies.
            balance = rec.currency_id._convert(counterpart_amount, company_currency, rec.company_id, rec.account_date)
            currency_id = rec.currency_id.id

        move_vals = {
            'date': fields.Date.context_today(rec),
            'ref': ref,
            'journal_id': rec.journal_id.id,
            'currency_id': rec.currency_id.id or rec.company_id.currency_id.id,
            'partner_id': rec.partner_id.id,
            'line_ids': [
                # Receivable / Payable / Transfer line.
                (0, 0, {
                    'name': ref,
                    'amount_currency': counterpart_amount if currency_id else 0.0,
                    'currency_id': currency_id,
                    'debit': balance > 0.0 and balance or 0.0,
                    'credit': balance < 0.0 and -balance or 0.0,
                    'date_maturity': rec.withholding_id.account_date,
                    'partner_id': rec.invoice_id.partner_id.commercial_partner_id.id,
                    'account_id': rec.invoice_id.partner_id.commercial_partner_id.property_account_payable_id.id,
                }),
                # Retención.
                (0, 0, {
                    'name': ref,
                    'amount_currency': -counterpart_amount if currency_id else 0.0,
                    'currency_id': currency_id,
                    'debit': balance < 0.0 and -balance or 0.0,
                    'credit': balance > 0.0 and balance or 0.0,
                    'date_maturity': rec.withholding_id.account_date,
                    'partner_id': rec.invoice_id.partner_id.commercial_partner_id.id,
                    'account_id': rec.account_id.id,
                }),
            ],
        }
        return move_vals

    def create_account_move(self):
        for rec in self:
            # se crea el encabezado del asiento
            AccountMove = self.env['account.move'].with_context(default_type='entry')
            rec.move_id  = AccountMove.create(rec._prepare_wtholding_moves())
            rec.move_id.action_post()
            
            # se concilia
            destination_account_id = rec.invoice_id.partner_id.commercial_partner_id.property_account_payable_id
            if rec.invoice_id:
                (rec.move_id + rec.invoice_id).line_ids \
                    .filtered(lambda line: line.account_id == destination_account_id and not line.reconciled)\
                    .reconcile()
            '''
            if rec.move_id:
                rec.move_id.line_ids.sudo().unlink()
                rec.move_id.write(rec._prepare_wtholding_moves())
            else:
                rec.move_id  = AccountMove.create(rec._prepare_wtholding_moves())
            #rec.move_id.action_post()
            '''
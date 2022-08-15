# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError

class AccountCloseBox(models.Model):
    _name = 'account.close.box'
    _description = 'Modulo de cierre de caja'
    _order = 'name desc'

    @api.depends('initial_amount','money_ids.subtotal','billete_ids.subtotal')
    def _get_total(self):
        for res in self:
            res.total_efectivo =  res.initial_amount + sum([x.subtotal for x in res.money_ids]) + sum([x.subtotal for x in res.billete_ids])
            res.total_cobrado = sum([x.subtotal for x in res.money_ids]) + sum([x.subtotal for x in res.billete_ids])

    def get_amount_payment(self):
            for res in self:
                payments = self.env['account.payment'].search(  [ ('date', '=', res.date),('state', '=', 'posted'), ('journal_id.is_chash', '=', True),('payment_type','=','inbound')])
                if payments:
                    res.amount_payment = sum([payment.amount for payment in payments])
                    res.amount_payment_diff = res.total_cobrado - res.amount_payment
                else:
                    res.amount_payment = 0.0
                    res.amount_payment_diff = 0.0

    @api.depends('company_id', )
    def _compute_currency_id(self):
        for res in self:
            res.currency_id = res.company_id.currency_id

    name = fields.Char(string="Arqueo numero", default='Nuevo')
    state = fields.Selection([('new','Nuevo'),('done','Validado'),('cancel','Anulado')],default='new', string='Estado')
    cashier_id = fields.Many2one('res.users', string="Cajero", tracking=2, default=lambda self: self.env.user)
    cashier = fields.Char(string='Caja')
    date = fields.Date(string='Fecha', default=fields.Date.context_today)
    initial_amount = fields.Monetary(string="Saldo inicial",  currency_field='currency_id',)
    total_efectivo = fields.Monetary(compute="_get_total", store=True, string="Total efectivo", currency_field='currency_id',)
    total_cobrado = fields.Monetary(compute="_get_total", store=True, string="Total cobrado", currency_field='currency_id',)
    money_ids = fields.One2many('account.close.box.money', 'close_box_id', string='Monedas')
    billete_ids = fields.One2many('account.close.box.bill', 'close_box_id', string='Billetes')
    journal_payment_ids = fields.One2many('account.close.box.journal', 'close_box_id', string='Medios de pago')
    amount_payment =  fields.Monetary(string="Monto Sistema",compute="get_amount_payment", currency_field='currency_id', )
    amount_payment_diff = fields.Monetary(string="Direfencia", compute="get_amount_payment", currency_field='currency_id',)
    note = fields.Text(string="Observaciones")
    company_id = fields.Many2one('res.company', string='Company', required=True,  default=lambda self: self.env.company.id)
    currency_id = fields.Many2one('res.currency', string='Currency', store=True,  compute='_compute_currency_id', help="Moneda del pago.")

    def action_done(self):
        for res in self:
            if res.name == 'Nuevo':
                sequence = self.env.ref("account_close_box.seq_account_close_box_auto")
                res.name = sequence.next_by_id()
            res.state = 'done'

    def action_cancel(self):
        for res in self:
            res.state = 'cancel'

    def action_open(self):
        for res in self:
            res.state = 'new'

    def unlink(self):
        for res in self:
            if res.name != 'Nuevo':
                raise UserError('No se puede suprimir un registro que haya sido validado!')
        return super(AccountCloseBox, self).unlink()


class AccountCloseBoxMoney(models.Model):
    _name = 'account.close.box.money'

    @api.depends('coin_value','number')
    def _get_subtotal(self):
        for res in self:
            res.subtotal = res.coin_value*res.number

    coin_value = fields.Float(string="Denominacion")
    number = fields.Integer(string="Cantidad contada")
    subtotal = fields.Float(string="Subtotal",compute="_get_subtotal", store=True)
    close_box_id = fields.Many2one('account.close.box', string='Caja')

class AccountCloseBoxBill(models.Model):
    _name = 'account.close.box.bill'

    @api.depends('coin_value', 'number')
    def _get_subtotal(self):
        for res in self:
            res.subtotal = res.coin_value*res.number

    coin_value = fields.Float(string="Denominacion")
    number = fields.Integer(string="Cantidad contada")
    subtotal = fields.Float(string="Subtotal",compute="_get_subtotal", store=True)
    close_box_id = fields.Many2one('account.close.box', string='Caja')

class AccountCloseBoxJournal(models.Model):
    _name = 'account.close.box.journal'

    @api.depends('journal_id', 'amount_cobrado',  )
    def _get_payment_subtotal(self):
        for res in self:
            if  res.journal_id:
                payments = self.env['account.payment'].search([('journal_id','=', res.journal_id.id),('date','=',res.close_box_id.date),('state','=','posted'),('payment_type','=','inbound')])
                res.amount_payment = sum([payment.amount for payment in payments])
            else:
                res.amount_payment = 0.0

    @api.depends('journal_id','amount_cobrado','amount_payment')
    def _get_diferencia(self):
        for res in self:
            res.diferencia =  res.amount_cobrado - res.amount_payment

    @api.depends('journal_id')
    def _compute_currency_id(self):
        for pay in self:
            pay.currency_id = pay.journal_id.currency_id or pay.journal_id.company_id.currency_id

    journal_id = fields.Many2one('account.journal', string="Diario")
    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False, compute='_compute_currency_id', help="Moneda del pago.")
    amount_cobrado = fields.Monetary(currency_field='currency_id', string="Monto Cobrado")
    amount_payment = fields.Monetary(string="Monto Sistema",compute="_get_payment_subtotal", currency_field='currency_id',)
    diferencia = fields.Monetary(string="Diferencia", compute="_get_diferencia", currency_field='currency_id', )
    close_box_id = fields.Many2one('account.close.box', string='Caja')


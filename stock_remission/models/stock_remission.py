# -*- coding: utf-8 -*-
# Part of SysNeo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError, ValidationError

import json

class StockRemission(models.Model):
    _name = 'stock.remission'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Remisión"
    _order = 'date desc, name desc, id desc'


    @api.depends('line_ids.wtax_amount')
    def _compute_wtax_tamount(self):
        for rec in self:
            rec.wtax_tamount = sum([l.wtax_amount for l in rec.line_ids])

    company_id = fields.Many2one(
        comodel_name='res.company', string='Company', required=True, index=True,
        default=lambda self: self.env.company
    )

    name = fields.Char(
        string='Number', required=True, readonly=True, copy=False, default='/'
    )

    partner_id = fields.Many2one(
        comodel_name='res.partner', readonly=True, tracking=True,
        states={'draft': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        string='Direccion entega', change_default=True
    )

    ref = fields.Char(string="Referencia", copy=False,)

    date = fields.Date(string='Fecha', required=True, index=True, readonly=True,
        states={'draft': [('readonly', False)]},default=fields.Date.context_today
    )

    state = fields.Selection(
        selection=[
            ('draft', 'Borrador'),
            ('posted', 'Publicado'),
            ('cancel', 'Cancelado')
        ], 
        string='Estado', required=True, readonly=True, copy=False, tracking=True, default='draft'
    )

    user_id = fields.Many2one(
        comodel_name='res.users', copy=False, tracking=True, string='Usuario',
        default=lambda self: self.env.user
    )

    line_ids = fields.One2many(
        comodel_name='stock.remission.line', inverse_name='remission_id', string='Líneas', 
        copy=True, readonly=True, states={'draft': [('readonly', False)]}
    )

    narration = fields.Text(string="Notas",)

    serie_id = fields.Many2one(comodel_name="remission.serie", string="Serie", required=True,
        readonly=True, states={'draft': [('readonly', False)]})

    doc_origin_type = fields.Selection(
        selection=[
            ('outgoing', 'Entrega'),
            ('internal', 'Transferencia'),
            ('out_invoice', 'Factura'),
        ], 
        string="Tipo Doc.Origen", required=True,
        readonly=True, states={'draft': [('readonly', False)]}
    )

    picking_type_id = fields.Many2one(comodel_name="stock.picking.type", string="Tipo operación", 
        readonly=True, states={'draft': [('readonly', False)]})

    origin_picking_ids = fields.Many2many(comodel_name="stock.picking", string="Picking", 
        readonly=True, states={'draft': [('readonly', False)]})

    origin_invoice_ids = fields.Many2many(comodel_name="account.move", string="Facturas", 
        readonly=True, states={'draft': [('readonly', False)]})
    # Datos fiscales
    l10n_hn_cai = fields.Char(string="CAI", readonly=True, states={'draft': [('readonly', False)]})
    l10n_hn_correlativo_fiscal_inicial = fields.Char(string="Rango Inicial", readonly=True, states={'draft': [('readonly', False)]})
    l10n_hn_correlativo_fiscal_final = fields.Char(string="Rango Final", readonly=True, states={'draft': [('readonly', False)]})
    l10n_hn_fecha_inicial_emision = fields.Date(string="Fecha recepción", readonly=True, states={'draft': [('readonly', False)]})
    l10n_hn_fecha_final_emision = fields.Date(string="Fecha final emisión", readonly=True, states={'draft': [('readonly', False)]})
    
    def copiar_datos_fiscales(self):
        fiscal = self.serie_id.sequence_id
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

    def apply_validation(self):
        if not self.serie_id.sequence_id:
            raise UserError("Usted debe definir una secuencia en la serie de remisión elegida")

    def action_post(self):
        for rec in self:
            rec.apply_validation()
            rec.state = 'posted'
            rec.name = rec.serie_id.sequence_id.with_context(ir_sequence_date=rec.date).next_by_id() if rec.name == '/' else rec.name
            rec.copiar_datos_fiscales()

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_load_lines(self):
        for rec in self:
            rec.line_ids.sudo().unlink()
            if rec.doc_origin_type == 'out_invoice':
                lineas_factura_ids = rec.origin_invoice_ids.mapped('invoice_line_ids')
                for line in lineas_factura_ids:
                    vals = {
                        'remission_id': rec.id,
                        'account_move_id': line.id,
                    }
                    linea_remision = self.env['stock.remission.line'].sudo().create(vals)
                    linea_remision.onchange_stock_invoice_id()
            else:
                lineas_picking_ids = rec.origin_picking_ids.mapped('move_line_ids_without_package')
                for line in lineas_picking_ids:
                    vals = {
                        'remission_id': rec.id,
                        'stock_moveline_id': line.id,
                    }
                    linea_remision = self.env['stock.remission.line'].sudo().create(vals)
                    linea_remision.onchange_stock_invoice_id()

class StockRemissionLine(models.Model):
    _name = "stock.remission.line"
    _description = "Línieas Remisión"
    _order = "id asc"
    _check_company_auto = True
    
    remission_id = fields.Many2one(comodel_name='stock.remission', string='Remisión', 
        index=True, required=True, readonly=True, auto_join=True, ondelete="cascade",
    )

    doc_origin_type = fields.Selection(
        selection=[
            ('outgoing', 'Entrega'),
            ('internal', 'Transferencia'),
            ('out_invoice', 'Factura'),
        ], 
        string="Tipo Doc.Origen", related='remission_id.doc_origin_type'
    )
    
    company_id = fields.Many2one(related='remission_id.company_id', store=True, readonly=True)

    stock_moveline_id = fields.Many2one(comodel_name="stock.move.line", string="Producto Entrega")

    account_move_id = fields.Many2one(comodel_name="account.move.line", string="Producto Factura")

    product_id = fields.Many2one(comodel_name="product.product", string="Producto")

    sequence = fields.Integer(string='Sequence', default=10)

    lote_serie = fields.Char(string='Lote/Serie')
    
    qty = fields.Float(string='Cantidad')

    product_uom_id = fields.Many2one(comodel_name="uom.uom", string="Unidad Medida")

    @api.onchange('stock_moveline_id','account_move_id')
    def onchange_stock_invoice_id(self):
        for rec in self:
            if rec.doc_origin_type == 'out_invoice':
                line = rec.account_move_id
                rec.product_id = line.product_id
                rec.lote_serie = ''
                rec.qty = line.quantity
                rec.product_uom_id = line.product_uom_id
            else:
                line = rec.stock_moveline_id
                rec.product_id = line.product_id
                rec.lote_serie = line.lot_id.name
                rec.qty = line.qty_done
                rec.product_uom_id = line.product_uom_id

class RemissionSerie(models.Model):
    _name = "remission.serie"
    _description = "Series Remisión"
    _order = "id asc"
    _check_company_auto = True
    
    name = fields.Char(string="Nombre", required=True)
    
    sequence_id = fields.Many2one('ir.sequence', string='Secuencia', copy=False, required=True)
    
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company', index=True,
        default=lambda self: self.env.company
    )

    sequence = fields.Integer(string='Sequence', default=10)


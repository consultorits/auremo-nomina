from odoo import fields, api, models, tools, _

class accountReportSar(models.Model):
    _name = 'account.report.sar'
    _description = 'Reporte de libros contables SAR'
    _auto = False

    #conteo = fields.Integer(readonly=True)
    fecha = fields.Date(readonly=True)
    empresa = fields.Char(readonly=True)
    rtn = fields.Char(readonly=True)
    state = fields.Selection([('draft', 'Unposted'), ('posted', 'Posted'), ('cancel', 'Cancelled')], 'Status', readonly=True)
    factura = fields.Char(readonly=True)
    #documento = fields.Many2one('account.move', 'Documento', readonly=True, auto_join=True)

    no_tax_def = fields.Monetary(readonly=True, string='Sin Ind. Impuesto', currency_field='company_currency_id')
    isvimp = fields.Monetary(readonly=True, string='isvimp', currency_field='company_currency_id')
    exeimp = fields.Monetary(readonly=True, string='exeimp', currency_field='company_currency_id')
    isvr10 = fields.Monetary(readonly=True, string='', currency_field='company_currency_id')
    exento = fields.Monetary(readonly=True, string='Importe Exento', currency_field='company_currency_id')
    exonerado = fields.Monetary(readonly=True, string='Importe Exonerado', currency_field='company_currency_id')
    gravado = fields.Monetary(readonly=True, string='Gravado', currency_field='company_currency_id')
    gravado15 = fields.Monetary(readonly=True, string='Gravado 15%', currency_field='company_currency_id')
    gravado18 = fields.Monetary(readonly=True, string='Gravado 18%', currency_field='company_currency_id')
    impuesto15 = fields.Monetary(readonly=True, string='Impuesto 15%', currency_field='company_currency_id')
    impuesto18 = fields.Monetary(readonly=True, string='Impuesto 18%', currency_field='company_currency_id')
    impuesto = fields.Monetary(readonly=True, string='Impuesto Total', currency_field='company_currency_id')
    total = fields.Monetary(readonly=True, string='Total', currency_field='company_currency_id')

    type = fields.Char(readonly=True)
    journal_id = fields.Many2one('account.journal', 'Journal', readonly=True, auto_join=True)
    #partner_id = fields.Many2one('res.partner', 'Partner', readonly=True, auto_join=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True, auto_join=True)
    company_currency_id = fields.Many2one(related='company_id.currency_id', readonly=True)
    move_id = fields.Many2one('account.move', string='Entry', auto_join=True)

    def init(self):
        cr = self._cr
        tools.drop_view_if_exists(cr, self._table)
        query = """
             select A.id,
       A.id as move_id,
       A.type,
       A.fecha,
       A.factura,
       A.state,
       A.journal_id,
       A.company_id,
       A.currency_id,
       A.empresa,
       A.rtn,
       case when A.state != 'cancel' then A.exento else 0.00 end as exento,
       case when A.state != 'cancel' then A.exonerado else 0.00 end as exonerado,
       case when A.state != 'cancel' then A.gravado else 0.00 end as gravado,
       case when A.state != 'cancel' then A.gravado15 else 0.00 end as gravado15,
       case when A.state != 'cancel' then A.gravado18 else 0.00 end as gravado18,
       case when A.state != 'cancel' then A.isv15 else 0.00 end as impuesto15,
       case when A.state != 'cancel' then A.isv18 else 0.00 end as impuesto18,
       0 as no_tax_def,
       case when A.state != 'cancel' then A.isvimp else 0.00 end as isvimp,
       case when A.state != 'cancel' then A.exeimp else 0.00 end as exeimp,
       0 as isvr10,
       0 as impuesto,
       case when A.state != 'cancel' then A.montototal else 0.00 end as total
from
(select 
t1.id,
t1.type ,
t1.fecha,
t1.factura,
t1.state ,
t1.journal_id,
t1.company_id,
t1.currency_id,
t1.empresa,
t1.rtn,
case when t1.state ='cancel' then 0
else
case when t1.type = 'out_refund' then
t1.exento *(-1)
else
t1.exento end end as exento, 
case when t1.state ='cancel' then 0
else
case when t1.type = 'out_refund' then
(t1.Gravado15ISV - t1.Gravado15)*(-1)
else
t1.Gravado15ISV - t1.Gravado15 end end as isv15,
case when t1.state ='cancel' then 0
else
case when t1.type = 'out_refund' then
(t1.Gravado18ISV - t1.Gravado18)*(-1)
else
t1.Gravado18ISV - t1.Gravado18 end end as isv18,
case when t1.state ='cancel' then 0
else
case when t1.type = 'out_refund' then
(t1.isvimportacion)*(-1)
else
t1.isvimportacion end end as isvimp,
case when t1.state ='cancel' then 0
else
case when t1.type = 'out_refund' then
(t1.exeimportacion)*(-1)
else 
t1.exeimportacion end end as exeimp,
case when t1.state ='cancel' then 0
else
case when t1.type = 'out_refund' then
(t1.Gravado15 + t1.Gravado18)*(-1)
else
t1.Gravado15 + t1.Gravado18 end end as gravado,
case when t1.state ='cancel' then 0
else
case when t1.type = 'out_refund' then
(t1.Gravado15)*(-1)
else
t1.Gravado15 end end as gravado15,
case when t1.state ='cancel' then 0
else
case when t1.type = 'out_refund' then
(t1.Gravado18)*(-1)
else
t1.Gravado18 end end as gravado18,
case when t1.state ='cancel' then 0
else
case when t1.type = 'out_refund' then
(t1.exonerado)*(-1)
else
t1.exonerado end end as exonerado,
case when t1.state ='cancel' then 0
else
case when t1.type = 'out_refund' then
(t1.montototal)*(-1)
else 
t1.montototal end end as montototal
from (select am.id,
       am.move_type as type,
       am.invoice_date as fecha,
       CASE WHEN am.move_type = 'in_invoice'
            THEN am.ref
            else am.name end AS factura,
       am.state,
       am.journal_id,
       am.company_id,
       rc.currency_id,
       rp.name AS empresa,
       rp.vat AS rtn,
       (select sum(aml.price_subtotal)
		from account_move_line aml
		left join account_move_line_account_tax_rel amlatr on amlatr.account_move_line_id = aml.id
		left join account_tax at2 on amlatr.account_tax_id  = at2.id 
		where   aml.account_id <> '51' and aml.account_id <> '1870' and aml.move_id  = am.id  and at2."name" = 'ISV 15%') as Gravado15 ,
		(select sum(aml.price_total)
		from account_move_line aml
		left join account_move_line_account_tax_rel amlatr on amlatr.account_move_line_id = aml.id
		left join account_tax at2 on amlatr.account_tax_id  = at2.id 
		where   aml.account_id <> '51' and aml.account_id <> '1870' and aml.move_id  = am.id  and at2."name" = 'ISV 15%') as Gravado15ISV,
		(select sum(aml.price_subtotal)
		from account_move_line aml
		left join account_move_line_account_tax_rel amlatr on amlatr.account_move_line_id = aml.id
		left join account_tax at2 on amlatr.account_tax_id  = at2.id 
		where   aml.account_id <> '51' and aml.account_id <> '1870' and aml.move_id  = am.id  and at2."name" = 'ISV 18%') as Gravado18 ,
		(select sum(aml.price_total)
		from account_move_line aml
		left join account_move_line_account_tax_rel amlatr on amlatr.account_move_line_id = aml.id
		left join account_tax at2 on amlatr.account_tax_id  = at2.id 
		where   aml.account_id <> '51' and aml.account_id <> '1870' and aml.move_id  = am.id  and at2."name" = 'ISV 18%') as Gravado18ISV,
		(select sum(aml.price_total)
		from account_move_line aml
		left join account_move_line_account_tax_rel amlatr on amlatr.account_move_line_id = aml.id
		left join account_tax at2 on amlatr.account_tax_id  = at2.id 
		where   aml.account_id <> '51' and aml.account_id <> '1870' and aml.move_id  = am.id  and at2."name" = 'EXE' ) as exento,
		(select sum(aml.price_total)
		from account_move_line aml
		left join account_move_line_account_tax_rel amlatr on amlatr.account_move_line_id = aml.id
		left join account_tax at2 on amlatr.account_tax_id  = at2.id 
		where   aml.account_id <> '51' and aml.account_id <> '1870' and aml.move_id  = am.id  and at2."name" = 'EXO') as exonerado,
		(select sum(aml.price_total)
		from account_move_line aml
		left join account_move_line_account_tax_rel amlatr on amlatr.account_move_line_id = aml.id
		left join account_tax at2 on amlatr.account_tax_id  = at2.id 
		where   aml.account_id <> '51' and aml.account_id <> '1870' and aml.move_id  = am.id  and at2."name" = 'EXEIMP') as exeimportacion,
		(select sum(aml.price_total)
		from account_move_line aml
		left join account_move_line_account_tax_rel amlatr on amlatr.account_move_line_id = aml.id
		left join account_tax at2 on amlatr.account_tax_id  = at2.id 
		where   aml.account_id <> '51' and aml.account_id <> '1870' and aml.move_id  = am.id  and at2."name" = 'ISVIMP') as isvimportacion,
		am.amount_total as montototal
from account_move am 
left join res_partner as rp on am.partner_id = rp.id
left join res_company as rc on am.company_id = rc.id
left join account_journal as aj on am.journal_id = aj.id
where aj.name in ('Facturas de Clientes','Facturas de Compras',
'Facturas de Ventas Credito','Facturas de Venta Contado',
'Boleta de Compra','Nota de Credito SAR','Facturas de Proveedores')
and am.state in ('posted','cancel') ) as t1) as A 
        """
        sql = """CREATE or REPLACE VIEW %s as (%s)""" % (self._table, query)
        cr.execute(sql)

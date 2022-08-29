from odoo import fields, api, models, tools, _


class accountReportVentasConso(models.Model):
    _name = 'account.report.ventas.conso'
    _description = 'Reporte de libro Ventas '
    _auto = False

    id = fields.Integer(readonly=True)
    fecha = fields.Date(readonly=True)
    empresa = fields.Char(readonly=True)
    rtn = fields.Char(readonly=True)
    factura = fields.Char(readonly=True)
    company_currency_id = fields.Many2one(related='company_id.currency_id', readonly=True)
    gravado = fields.Monetary(readonly=True, string='Gravado', currency_field='company_currency_id')
    gravado15 = fields.Monetary(readonly=True, string='Gravado 15%', currency_field='company_currency_id')
    gravado18 = fields.Monetary(readonly=True, string='Gravado 18%', currency_field='company_currency_id')
    exento = fields.Monetary(readonly=True, string='Importe Exento', currency_field='company_currency_id')
    exonerado = fields.Monetary(readonly=True, string='Importe Exonerado', currency_field='company_currency_id')
    isv15 = fields.Monetary(readonly=True, string='Impuesto 15%', currency_field='company_currency_id')
    isv18 = fields.Monetary(readonly=True, string='Impuesto 18%', currency_field='company_currency_id')
    total = fields.Monetary(readonly=True, string='Total', currency_field='company_currency_id')
    company_id = fields.Many2one('res.company', 'Company', readonly=True, auto_join=True)

    def init(self):
        cr = self._cr
        tools.drop_view_if_exists(cr, self._table)
        query = """
        Select ROW_NUMBER () OVER (ORDER BY B.fecha, B.factura) as contador ,
        CASE WHEN B.id = B.move_id THEN B.id + 999999 ELSE B.id END as id,
        B.move_id as move_id,
        B.type as type,
        B.fecha as fecha,
        B.Empresa as empresa,
        B.rtn  as rtn,
        B.factura as factura,
        B.State as state,
        B.journal_id as journal_id,
        B.company_id as company_id,
        B.currency_id as currency_id,
        sum(B.gravado) as gravado,
        sum(B.gravado15) as gravado15,
        sum(B.gravado18) as gravado18,
        sum(B.exento) as exento,
        sum(B.exonerado) as exonerado,
        sum(B.impuesto15) as isv15,
        sum(B.impuesto18) as isv18,
        sum(B.total) as total
from (
Select A.*
from (
SELECT
    am.id,
    aml.move_id,
    am.move_type AS type,
    am.date AS fecha,
    rp.name AS empresa,
    rp.vat AS rtn,
    CASE WHEN am.journal_id != 2 and am.move_type = 'in_invoice'
        THEN am.ref
        ELSE replace(am.name,'FV','') END AS factura,
    am.state,
    am.journal_id,
    am.company_id,
    rc.currency_id,
       CASE am.move_type when 'out_invoice' THEN
    sum(CASE WHEN am.state != 'cancel' and amlatr.account_tax_id in (1,2,7,8)
        THEN abs(aml.balance) ELSE Null END)
           WHEN 'out_refund' THEN -sum(CASE WHEN am.state != 'cancel' and amlatr.account_tax_id in (1,2,7,8)
        THEN abs(aml.balance) ELSE Null END) ELSE 0 END as gravado,
        CASE am.move_type when 'out_invoice' THEN
    sum(CASE WHEN am.state != 'cancel' and amlatr.account_tax_id in (2)
        THEN abs(aml.balance) ELSE Null END)
           WHEN 'out_refund' THEN -sum(CASE WHEN am.state != 'cancel' and amlatr.account_tax_id in (2)
        THEN abs(aml.balance) ELSE Null END) ELSE 0 END as gravado15,
        CASE am.move_type  when 'out_invoice' THEN
    sum(CASE WHEN am.state != 'cancel' and amlatr.account_tax_id in (8)
        THEN abs(aml.balance) ELSE Null END)
           WHEN 'out_refund' THEN -sum(CASE WHEN am.state != 'cancel' and amlatr.account_tax_id in (8)
        THEN abs(aml.balance) ELSE Null END) ELSE 0 END as gravado18,
        case am.move_type  when 'out_invoice' THEN
    sum(CASE WHEN am.state != 'cancel' and amlatr.account_tax_id in (3)
        THEN abs(aml.balance) ELSE Null END)
         WHEN 'out_refund' THEN -sum(CASE WHEN am.state != 'cancel' and amlatr.account_tax_id in (3)
        THEN abs(aml.balance) ELSE Null END) ELSE 0 END as exento,
       CASE am.move_type  when 'out_invoice' THEN
    sum(CASE WHEN am.state != 'cancel' and amlatr.account_tax_id in (4)
        THEN abs(aml.balance) ELSE Null END)
         WHEN 'out_refund' THEN -sum(CASE WHEN am.state != 'cancel' and amlatr.account_tax_id in (4)
        THEN abs(aml.balance) ELSE Null END) ELSE 0 END as exonerado,
       CASE am.move_type when 'out_invoice' THEN
    sum(CASE WHEN am.state != 'cancel' and aml.tax_line_id in (2)
        THEN abs(aml.balance) ELSE Null END)
         WHEN 'out_refund' THEN -sum(CASE WHEN am.state != 'cancel' and aml.tax_line_id in (2)
        THEN abs(aml.balance) ELSE Null END) ELSE 0 END as impuesto15,
       CASE am.move_type when 'out_invoice' THEN
    sum(CASE WHEN am.state != 'cancel' and aml.tax_line_id in (8)
        THEN abs(aml.balance) ELSE Null END)
         WHEN 'out_refund' THEN -sum(CASE WHEN am.state != 'cancel' and aml.tax_line_id in (8)
        THEN abs(aml.balance) ELSE Null END) ELSE 0 END as impuesto18,
       CASE am.move_type when 'out_invoice' THEN
    sum(CASE WHEN (am.state != 'cancel' and am.move_type in ('out_invoice','out_refund')
                       and aml.exclude_from_invoice_tab = true
                       and tax_repartition_line_id is null
                       --and account_internal_type in ('receivable','payable')
                       )
                       or  (am.state != 'cancel' and am.move_type  in ('in_invoice','in_refund')
                       and tax_repartition_line_id is null
                       --and account_internal_type in ('receivable','payable','other')
                       and credit > 0) THEN abs(aml.balance) ELSE Null END)
        WHEN 'out_refund' THEN -sum(CASE WHEN (am.state != 'cancel' and am.move_type  in ('out_invoice','out_refund')
                       and aml.exclude_from_invoice_tab = true
                       and tax_repartition_line_id is null
                       --and account_internal_type in ('receivable','payable')
                       )
                       or  (am.state != 'cancel' and am.move_type  in ('in_invoice','in_refund')
                       and tax_repartition_line_id is null
                       --and account_internal_type in ('receivable','payable','other')
                       and credit > 0) THEN abs(aml.balance) ELSE Null END) ELSE 0 END as total
    FROM account_move_line AS aml
    LEFT JOIN account_move AS am ON aml.move_id = am.id
    LEFT JOIN res_partner AS rp ON am.partner_id = rp.id
    LEFT JOIN res_company AS rc ON am.company_id = rc.id
    LEFT JOIN account_journal AS aj ON am.journal_id = aj.id
    LEFT JOIN account_move_line_account_tax_rel amlatr ON aml.id = amlatr.account_move_line_id
    WHERE aj.name in ('SAR Ventas')
    AND am.state in ('posted','cancel')
    GROUP BY am.date, am.id, rp.name, rp.vat, rc.currency_id, aml.move_id
    ORDER BY am.move_type  ) A 
	UNION ALL
SELECT
	po.id as id,
	 Max(am.id) as move_id,
	'out_invoice' as type,
	max(am.date) as fecha,
    rp.name as empresa,
	rp.vat as rtn,
	po.pos_reference as factura,
	'posted' as state,
	9 as journal_id,
	1 as company_id,
	44 as currency_id,
	0 as gravado,
	0 as gravado15,
	0 as gravado18,
    0 as exento,
    0 as exonerado,
    0 as impuesto15,
    0 as impuesto18,
    po.amount_total as total
	from pos_order po
        left join res_partner rp on po.partner_id = rp.id
        inner join pos_session ps on ps.id = po.session_id 
        inner join account_move am  on am.ref=ps."name" 
group by po.create_date, po.id,rp."name" ,rp.vat ,po.pos_reference --,po.exento ,po.exonerado ,po.isv15 ,po.isv18 ,po.gravado
 ) B
	group by B.id, B.move_id,B.factura, B.type, B.fecha, B.Empresa, B.rtn ,
	         B.State, B.journal_id, B.company_id, B.currency_id
	order by B.fecha, B.factura"""
        sql = """CREATE or REPLACE VIEW %s as (%s)""" % (self._table, query)
        cr.execute(sql)

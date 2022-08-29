# -*- coding:utf-8 -*-
from odoo import _, api, models
from odoo.tools.misc import format_date

class L10nHNSarCompra(models.AbstractModel):
    _name = "l10n_hn.sar.libro.compras"
    _inherit = "account.report"
    _description = "Libro de Compras"

    @api.model
    def _get_report_name(self):
        return _('Libro de compras')

    filter_date = {'mode':'range','date_from': '', 'date_to': '', 'filter': 'this_month'}
    filter_all_entries = False

    def _get_columns_name(self, options):
        return [
            {'name': _("Fecha"), 'class': 'date'},
            {'name': _("Factura"), 'class': 'texto'},
            {'name': _("Empresa"), 'class': 'texto'},
            {'name': _("RTN"), 'class': 'texto'},
            {'name': _('Importe Gravado 15'), 'class': 'number'},
            {'name': _('Importe Gravado 18'), 'class': 'number'},
            {'name': _('Importe Gravado'), 'class': 'number'},
            {'name': _('Importacion'), 'class': 'number'},
            {'name': _('Importacion Exenta'), 'class': 'number'},
            {'name': _('Importe Exento'), 'class': 'number'},
            {'name': _('Importe Exonerado'), 'class': 'number'},
            {'name': _('Impuesto 15%'), 'class': 'number'},
            {'name': _('Impuesto 18%'), 'class': 'number'},
            {'name': _('Total Impto.'), 'class': 'number'},
            {'name': _('Total'), 'class': 'number'},
        ]

    @api.model
    
    def _get_lines(self, options, line_id=None):
        context = self.env.context
        journal_type = options.get('journal_type', 'purchase')

        lines = []
        line_id = 0

        if journal_type == 'purchase':
            sign = 1.0
        else:
            sign = 1.0

        totals = {}.fromkeys(['gravado15','gravado18', 'gravado', 'isvimp', 'exeimp', 'no_tax_def', 'exento', 'exonerado', 'impuesto15', 'impuesto18', 'impuesto', 'total'], 0)
        domain = [('journal_id.type', '=', journal_type)]

        if context.get('date_to'):
            domain += [('fecha', '<=', context['date_to'])]
        if context.get('date_from'):
            domain += [('fecha', '>=', context['date_from'])]
        for rec in self.env['account.report.sar'].search_read(domain):
            totals['gravado15'] += rec['gravado15']
            totals['gravado18'] += rec['gravado18']
            totals['gravado'] += rec['gravado']
            totals['isvimp'] += rec['isvimp']
            totals['exeimp'] += rec['exeimp']
            totals['exento'] += rec['exento']
            totals['exonerado'] += rec['exonerado']
            totals['no_tax_def'] += rec['no_tax_def']
            totals['impuesto15'] += rec['impuesto15']
            totals['impuesto18'] += rec['impuesto18']
            totals['impuesto'] += rec['impuesto']
            totals['total'] += rec['total']
            if rec['type'] in ['in_invoice', 'in_refund']:
                caret_type = 'account.invoice.in'
            elif rec['type'] in ['out_invoice', 'out_refund']:
                caret_type = 'account.invoice.out'
            else:
                caret_type = 'account.move'

            lines.append({
                'id': rec['id'],
                'name': format_date(self.env, rec['fecha']),
                'class': 'date',
                'level': 2,
                'model': 'account.report.sar',
                'caret_options': caret_type,
                'columns': [
                    {'name': rec['factura']},
                    {'name': rec['empresa'], 'class': 'whitespace_print'},
                    {'name': rec['rtn'], 'class': 'whitespace_print'},
                    {'name': self.format_value(sign * rec['gravado15'])},
                    {'name': self.format_value(sign * rec['gravado18'])},
                    {'name': self.format_value(sign * rec['gravado'])},
                    {'name': self.format_value(sign * rec['isvimp'])},
                    {'name': self.format_value(sign * rec['exeimp'])},
                    {'name': self.format_value(rec['no_tax_def'] + rec['exento'])},
                    {'name': self.format_value(sign * rec['exonerado'])},
                    {'name': self.format_value(sign * rec['impuesto15'])},
                    {'name': self.format_value(sign * rec['impuesto18'])},
                    {'name': self.format_value(sign * rec['impuesto'])},
                    {'name': self.format_value(sign * rec['total'])},
                ],
            })
        line_id += 1

        # ===== Linea de Totales =======
        lines.append({
            'id': 'total',
            'name': _('Total'),
            'class': 'o_account_reports_domain_total',
            'level': 0,
            'columns': [
                {'name': ''},
                {'name': ''},
                {'name': ''},
                {'name': self.format_value(sign * totals['gravado15'])},
                {'name': self.format_value(sign * totals['gravado18'])},
                {'name': self.format_value(sign * totals['gravado'])},
                {'name': self.format_value(sign * totals['isvimp'])},
                {'name': self.format_value(sign * totals['exeimp'])},
                {'name': self.format_value(totals['no_tax_def'] + totals['exento'])},
                {'name': self.format_value(sign * totals['exonerado'])},
                {'name': self.format_value(sign * totals['impuesto15'])},
                {'name': self.format_value(sign * totals['impuesto18'])},
                {'name': self.format_value(sign * totals['impuesto'])},
                {'name': self.format_value(sign * totals['total'])},
            ],
        })

        return lines

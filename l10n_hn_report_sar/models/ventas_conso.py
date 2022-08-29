# -*- coding:utf-8 -*-
from odoo import _, api, models
from odoo.tools.misc import format_date

class L10nHnVentasConso(models.AbstractModel):
    _name = "l10n_hn.ventas.conso"
    _inherit = "account.report"
    _description = "Libro de Ventas Consolidado"

    @api.model
    def _get_report_name(self):
        return _('Libro de Ventas Consolidado')

    filter_date = {'mode':'range','date_from': '', 'date_to': '', 'filter':'this_month'}
    filter_all_entries = False

    def _get_columns_name(self, options):
        return [
            {'name': _("Fecha"), 'class': 'date'},
            {'name': _("Factura"), 'class': 'texto'},
            {'name': _("Empresa"), 'class': 'texto'},
            {'name': _("RTN"), 'class': 'texto'},
            {'name': _('Importe Gravado 15'), 'class': 'number'},
            {'name': _('Importe Gravado 18'), 'class': 'number'},
            {'name': _('Importe Exento'), 'class': 'number'},
            {'name': _('Importe Exonerado'), 'class': 'number'},
            {'name': _('Impuesto 15%'), 'class': 'number'},
            {'name': _('Impuesto 18%'), 'class': 'number'},
            {'name': _('Total'), 'class': 'number'},
        ]

    @api.model
    def _get_lines(self, options, line_id=None):
        context = self.env.context

        lines = []
        line_id = 0
        conteo = 0

        totals = {}.fromkeys(['gravado15','gravado18', 'exento', 'exonerado', 'isv15', 'isv18', 'total'], 0)
        domain = []

        if context.get('date_to'):
            domain += [('fecha', '<=', context['date_to'])]
        if context.get('date_from'):
            domain += [('fecha', '>=', context['date_from'])]
        for rec in self.env['account.report.ventas.conso'].search_read(domain):
            conteo += conteo
            totals['gravado15'] += rec['gravado15']
            totals['gravado18'] += rec['gravado18']
            totals['exento'] += rec['exento']
            totals['exonerado'] += rec['exonerado']
            totals['isv15'] += rec['isv15']
            totals['isv18'] += rec['isv18']
            totals['total'] += rec['total']

            lines.append({
                'id': rec['id'],
                'name': format_date(self.env, rec['fecha']),
                'class': 'date',
                'level': 3,

                'columns': [
                    {'name': rec['factura'], 'class': 'texto'},
                    {'name': rec['empresa'], 'class': 'texto'},
                    {'name': rec['rtn'], 'class': 'texto'},
                    {'name': self.format_value(rec['gravado15'])},
                    {'name': self.format_value(rec['gravado18'])},
                    {'name': self.format_value(rec['exento'])},
                    {'name': self.format_value(rec['exonerado'])},
                    {'name': self.format_value(rec['isv15'])},
                    {'name': self.format_value(rec['isv18'])},
                    {'name': self.format_value(rec['total'])},
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
                {'name': self.format_value(totals['gravado15'])},
                {'name': self.format_value(totals['gravado18'])},
                {'name': self.format_value(totals['exento'])},
                {'name': self.format_value(totals['exonerado'])},
                {'name': self.format_value(totals['isv15'])},
                {'name': self.format_value(totals['isv18'])},
                {'name': self.format_value(totals['total'])},
            ],
        })

        return lines

{
    'name':'Reportes de fiscalizacion',
    'description': """ Explicar tecnico""",
    'installable': True,
    'depends': ['account',
                'account_reports',],
    'data':
        [
         'security/ir.model.access.csv',
         #'report/account_hn_sar_line.xml',
         'views/menu_sar_libro.xml',
         'views/account_report_view.xml',
         'views/assets.xml',
        ],
}
# -*- coding: utf-8 -*-
{
    'name': "Account Close Box",

    'summary': """
        Modulo para cierre de caja de ventas""",

    'description': """
        Modulo para cierre de caja de ventas
    """,

    'author': "SYSNEO CONSULTING",
    'website': "http://sysneo.pe",
    'category': 'Uncategorized',
    'version': '0.4',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/sequence.xml',
        'views/journal.xml',
        'views/account_close_box.xml',
        'report/report_print.xml',
    ],

}

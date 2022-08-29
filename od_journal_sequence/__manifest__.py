# -*- coding: utf-8 -*-

{
    'name': 'Capa Pais Honduras',
    'version': '14.0.4.0.0',
    'category': 'Accounting',
    'summary': 'Secuencia y detalles fiscales',
    'description': 'Capa pais de Honduras',
    'sequence': '1',
    'author': 'IT Solutions',
    'depends': ['account'],
    'demo': [],
    'data': [
        'data/account_data.xml',
        'views/account_journal.xml',
        'views/ir_sequence.xml',
        'views/account_move.xml',
        'report/invoice.xml',
    ],
    'qweb': [],
    'license': 'OPL-1',
    'installable': True,
    'application': False,
    'auto_install': False,
}

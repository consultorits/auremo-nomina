# -*- coding: utf-8 -*-
# Part of SysNeo. See LICENSE file for full copyright and licensing details.

{
    "name": "Account Payment Change",
    'price': '0',
    'currency': "USD",
    "summary": "Account Payment Change",
    'description': """
Account Payment Change
    """,
    "version": "1.0.0",
    "license": "Other proprietary",
    'category': 'Accounting/Accounting',
    "author": "SysNeo",
    "website": "https://sysneo.pe",
    "depends": ["account"],
    "data": [
        "wizard/account_payment_register_views.xml",
        "views/account_move_views.xml",
        "views/report_invoice.xml",
    ],
    "demo": [],
    "installable": True,
}

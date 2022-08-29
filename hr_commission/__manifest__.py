# -*- coding: utf-8 -*-
# Part of SysNeo. See LICENSE file for full copyright and licensing details.

{
    "name": "Hr Commission",
    'price': '0',
    'currency': "USD",
    "summary": "Hr Commission",
    'description': """
Hr Commission
    """,
    "version": "1.0.0",
    "license": "Other proprietary",
    'category': 'Human Resources/Employees',
    "author": "SysNeo",
    "website": "https://sysneo.pe",
    "depends": ["hr","sale","account"],
    "data": [
        "views/hr_employee_views.xml",
        "views/sale_views.xml",
        "views/account_move_views.xml",
    ],
    "demo": [],
    "installable": True,
}

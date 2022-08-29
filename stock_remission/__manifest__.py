# -*- coding: utf-8 -*-
# Part of SysNeo. See LICENSE file for full copyright and licensing details.

{
    "name": "Stock Remission",
    'price': '0',
    'currency': "USD",
    "summary": "Stock Remission",
    'description': """
Stock Remission
    """,
    "version": "13.0.1.0.0",
    "license": "Other proprietary",
    'category': 'Invoice',
    "author": "SysNeo",
    "website": "https://sysneo.pe",
    "depends": ["stock","account"],
    "data": [
        "security/remission_security.xml",
        "security/ir.model.access.csv",
        "report/remission_report.xml",
        "report/report_remission_template.xml",
        "views/remission_view.xml",
        #"views/wtax_view.xml",
        #"views/account_view.xml",
        #"views/templates.xml",
        #"views/whtax_report_view.xml",
    ],
    "demo": [],
    "installable": True,
}

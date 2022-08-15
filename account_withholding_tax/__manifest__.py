# -*- coding: utf-8 -*-
# Part of SysNeo. See LICENSE file for full copyright and licensing details.

{
    "name": "Withholding Tax",
    'price': '0',
    'currency': "USD",
    "summary": "Withholding Tax",
    'description': """
Withholding Tax
    """,
    "version": "14.0.1.0.0",
    "license": "Other proprietary",
    'category': 'Invoice',
    "author": "SysNeo",
    "website": "https://sysneo.pe",
    "depends": ["base", "account","web"],
    "data": [
        "security/whtax_security.xml",
        "security/ir.model.access.csv",
        "report/whtax_report.xml",
        "report/report_whtax_template.xml",
        "views/withholding_view.xml",
        "views/wtax_view.xml",
        "views/account_view.xml",
        "views/templates.xml",
        "views/whtax_report_view.xml",
    ],
    'qweb': [
        "static/src/xml/account_whtax.xml",
    ],
    "demo": [],
    "installable": True,
}

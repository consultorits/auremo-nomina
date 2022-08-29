# -*- coding: utf-8 -*-
{
    'name': "GSIE Benefits by Law",
    "author": "Grupo SIE",
    'summary': """Module to calculate benefits by law""",
    'version': '0.1',
    'depends': ['base', 'hr', 'hr_contract', 'hr_payroll','hr_work_entry_contract'],

    'data': [
        "data/paperformat.xml",
        "security/ir.model.access.csv",
        "views/extra_salaries_view.xml",
        "views/leaves.xml",
        "views/config.xml",
        "views/contract_view_inh.xml",
        "views/vacation_request_view.xml",
        "views/vacations_view.xml",
        "views/payslip_run_inh.xml",
        "reports/vacation_request_report.xml",
        "reports/extra_salary_report.xml",
        "reports/report_reports.xml"
    ],
    'application': True,
}

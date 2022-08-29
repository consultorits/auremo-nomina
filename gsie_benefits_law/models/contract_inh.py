# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class contractInh(models.Model):
    _inherit = "hr.contract"

    fourteen_amount = fields.Float(string="Decimo Cuarto")
    thirteen_amount = fields.Float(string="Aguinaldo")
    vacations_amount = fields.Float(string="Monto Vacaciones")

class payslipRunInh(models.Model):
    _inherit = "hr.payslip.run"

    extra_salary = fields.Boolean(string="Tipo de Pago")
    salary_type = fields.Selection([('thirteen','Decimo Tercer Mes'),('fourteen','Decimo Cuarto Mes'),('vacations','Vacaciones')],string="Tipo de Nomina")
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class extraSalaries(models.Model):
    _name = "benefits.extra.salaries"
    _description = "Calculate to extra salaries (fourteen and thirteen month)"

    name = fields.Char(string="Nombre")
    benefits_type = fields.Selection([('thirteen','Decimo Tercer Mes'),('fourteen','Decimo Cuarto Mes')],string="Tipo beneficio")
    start_date = fields.Date(string="Fecha de Inicio")
    end_date = fields.Date(string="Fecha Final")
    structure_id = fields.Many2one('hr.payroll.structure',string="Estructura Salarial")
    total = fields.Float(string="Total",compute="_get_total")
    journal_id = fields.Many2one('account.journal',string="Diario")
    salary_rule_id =  fields.Many2one('hr.salary.rule',string="Regla Salarial")
    state = fields.Selection([('draft','Borrador'),('validated','Validado')],string="Estado",default="draft")
    line_ids = fields.One2many('extra.salaries.line','extra_salary_id',string="Lineas")

    def getEmployees(self):
        contract_ids = self.env['hr.contract'].search([('state','=','open')])
        self.line_ids.unlink()
        for contract in contract_ids:
            payslip_ids = self.env['hr.payslip'].search([('employee_id','=',contract.employee_id.id),('date_to','>=',self.start_date),('date_to','<=',self.end_date)])
            amount = sum(payslip_ids.mapped('basic_wage'))
            vals = {
                'employee_id': contract.employee_id.id,
                'acumulated_salary': amount,
                'amount': amount / 12,
                'extra_salary_id': self.id
            }
            self.env['extra.salaries.line'].create(vals)

    def validate_benefit(self):
        for line in self.line_ids:
            if self.benefits_type == 'thirteen':
                line.employee_id.contract_id.thirteen_amount = line.amount
            else:
                line.employee_id.contract_id.fourteen_amount = line.amount
        
        self.state = 'validated'

    def sent_to_draft(self):
        self.state = 'draft'

    @api.depends('line_ids')
    def _get_total(self):
        for rec in self:
            rec.total = sum(rec.line_ids.mapped('amount'))

class extraSalariesLine(models.Model):
    _name = "extra.salaries.line"
    _description = "Lines calculate to extra salaries (fourteen and thirteen month)"

    employee_id = fields.Many2one('hr.employee',string="Empleado")
    acumulated_salary = fields.Float(string="Salario Acumulado")
    amount = fields.Float(string="Monto a Pagar")
    extra_salary_id = fields.Many2one('benefits.extra.salaries',string="Salario Extra")
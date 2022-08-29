# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class vacations(models.Model):
    _name = "benefits.vacations"
    _description = "Calculate vacations"

    name = fields.Char(string="Nombre")
    start_date = fields.Date(string="Fecha de Inicio")
    end_date = fields.Date(string="Fecha Final")
    structure_id = fields.Many2one('hr.payroll.structure',string="Estructura Salarial")
    total = fields.Float(string="Total",compute="_get_total")
    journal_id = fields.Many2one('account.journal',string="Diario")
    salary_rule_id =  fields.Many2one('hr.salary.rule',string="Regla Salarial")
    state = fields.Selection([('draft','Borrador'),('validated','Validado')],string="Estado",default="draft")
    line_ids = fields.One2many('vacations.lines','vacation_id',string="Lineas")

    def getEmployees(self):
        request_ids = self.env['vacation.request'].search([('state','=','done'),('date_from','>=',self.start_date),('date_to','<=',self.end_date)])
        self.line_ids.unlink()
        employees = []
        lines = []
        for request in request_ids:
            day_amount = request.employee_id.contract_id.wage / 30
            if request.employee_id.id in employees:
                lines[employees.index(request.employee_id.id)]['vacation_days'] += request.total_days
                lines[employees.index(request.employee_id.id)]['amount'] += request.total_days * day_amount
            else:
                employees.append(request.employee_id.id)
                lines.append({
                    'employee_id': request.employee_id.id,
                    'vacation_days': request.total_days,
                    'day_amount': day_amount,
                    'amount': day_amount * request.total_days,
                    'vacation_id': self.id
                })

        for vac in lines:
            self.env['vacations.lines'].create(vac)

    def validate_benefit(self):
        for line in self.line_ids:
            line.employee_id.contract_id.vacations_amount = line.amount
        
        self.state = 'validated'

    def sent_to_draft(self):
        self.state = 'draft'

    @api.depends('line_ids')
    def _get_total(self):
        for rec in self:
            rec.total = sum(rec.line_ids.mapped('amount'))

class extraSalariesLine(models.Model):
    _name = "vacations.lines"
    _description = "Lines calculate vacations"

    employee_id = fields.Many2one('hr.employee',string="Empleado")
    vacation_days = fields.Integer(string="Dias Vacaciones")
    day_amount = fields.Float(string="Sualdo por Dia")
    amount = fields.Float(string="Monto a Pagar")
    vacation_id = fields.Many2one('benefits.vacations',string="Vacaciones")
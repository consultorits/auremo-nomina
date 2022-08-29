# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import Warning

class VacationRequest(models.Model):
    _name = "vacation.request"
    _inherit = ['mail.thread']
    order = "request_date desc"

    name = fields.Char(string="Nombre")
    employee_id = fields.Many2one("hr.employee", string="Empleado", tracking=True)
    department_id = fields.Many2one("hr.department", "Departamento", tracking=True)
    job_id = fields.Many2one("hr.job", "Puesto", tracking=True)
    request_date = fields.Date("Fecha de la solicitud", default=fields.Date.context_today, tracking=True)
    date_from = fields.Date("Fecha de inicio")
    date_to = fields.Date("Fecha de finalización")
    total_days = fields.Integer("Total días solicitados")
    contract_date = fields.Date("Primera fecha del contrato")
    year = fields.Char("Year")
    
    state = fields.Selection([('draft', 'Borrador'),
                              ('done', 'Aprobado'),
                              ('cancel', 'Rechazado')], "Estado", default="draft")
    vacation_request_detail_ids = fields.One2many("vacation.request.detail", "vacation_request_id", "vacation_request_detail_ids")
    
    def refused(self):
        self.write({'state':'cancel'})

    @api.onchange("request_date")
    def onchangefecha(self):
        if self.request_date:
            varialble_string = datetime.strptime(str(self.request_date), '%Y-%m-%d')
            self.year = str(varialble_string.strftime("%Y"))
           

    @api.onchange("employee_id")
    def getEmployeeInfo(self):
        if self.employee_id:
            self.department_id  = self.employee_id.department_id.id
            self.job_id =  self.employee_id.job_id.id
            contract = self.env["hr.contract"].search([('employee_id', '=', self.employee_id.id),
                                                       ('state', '=', 'open')], limit=1)
            if contract:
                self.contract_date = contract.date_start
    
    @api.onchange("date_from", "date_to")
    def getDays(self):
        if self.date_from and self.date_to:
            days = self.date_to - self.date_from
            self.total_days = days.days + 1
          
    def getInfo(self):
        self.vacation_request_detail_ids.unlink()
        obj_create = self.env["vacation.request.detail"]

        date_str = datetime.today().strftime('%Y-%m-%d')
        date_split = date_str.split("-")
        actual_year = int(date_split[0])
        
        date2_split = str(self.contract_date).split("-")
        contract_date = int(date2_split[0])

        number_work_years = actual_year - contract_date

        config_id = self.env["gsie.leaves.config"].search([('seleccionado', '=', True)])
        if not config_id:
            raise Warning("Ningún ajuste configurado")

        count = 0
        
        for y in range(number_work_years):
            count += 1
            contract_date += 1

            vals = {
                "year":contract_date,
                "vacation_request_id": self.id
            }

            if count == 1:
                vals["vacation_days"] = 10
            
            if count == 2:
                vals["vacation_days"] = 12

            if count == 3:
                vals["vacation_days"] = 15
            
            if count >= 4:
                vals["vacation_days"] = 20
        
            obj_create.create(vals)
       
    def done(self):
        self.write({'state':'done'})
    
    def draft(self):
        self.write({'state':'draft'})

    def unlink(self):
        for r in self:
            if r.state != "draft":
                raise Warning(('No puede borrar este registro'))
        return super(VacationRequest, self).unlink()


class VacationRequestDetal(models.Model):
    _name = "vacation.request.detail"

    year =  fields.Integer("Año")
    vacation_days = fields.Integer("Días de vacaciones")
    
    vacation_request_id = fields.Many2one("vacation.request2", "vacation_request_id")
    

    
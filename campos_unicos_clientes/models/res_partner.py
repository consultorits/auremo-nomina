# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.constrains('name')
    def check_mobile(self):
       for rec in self:
           names = self.env['res.partner'].search([('name','=',rec.name),('id','!=',rec.id)])
           vats = self.env['res.partner'].search([('vat','=',rec.vat),('id','!=',rec.id)])
           mobiles = self.env['res.partner'].search([('mobile','=',rec.mobile),('id','!=',rec.id)])
           #references = self.env['res.partner'].search([('name','=',rec.name),('id','!=',rec.id)])
           if names:
            raise ValidationError("El Campo Nombre en el socio de negocio debe ser unico")
           if vats:
            raise ValidationError("El Campo de RTN(NIF) en el socio de negocio debe ser unico")
           if mobiles:
            raise ValidationError("El Campo de Celular en el socio de negocio debe ser unico")